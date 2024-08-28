#Emprestimo-Facil\app\services\emprestimo_service.py

from sqlalchemy.orm import Session
from app.models.emprestimo import Emprestimo, StatusEmprestimo, Pagamento
from app.schemas.emprestimo import EmprestimoCreate, EmprestimoUpdate, PagamentoCreate
from datetime import datetime, date
from .base_service import BaseService
from typing import List
from app.core.config import settings
from app.services.notification_service import NotificationFactory
from app.services.calculo_juros import CalculoJuros, TipoJuros, TipoMora, RegraFixa, RegraRecorrente
from decimal import Decimal
from app.services.cache import cache, cache_decorator
from app.core.celery_app import enviar_notificacao_async
from app.core.logger import get_logger
from app.services.garantia_service import GarantiaService
from app.schemas.garantia import GarantiaCreate

logger = get_logger(__name__)

class EmprestimoService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db)
        self.notification_factory = NotificationFactory()
        self.calculo_juros = CalculoJuros()

    def criar_emprestimo(self, emprestimo: EmprestimoCreate):
        try:
            db_emprestimo = Emprestimo(**emprestimo.model_dump(exclude={'regras_pagamento'}))
            db_emprestimo.regras_pagamento = self._criar_regras_pagamento(emprestimo.regras_pagamento)
            db_emprestimo.proximo_vencimento = self._calcular_proximo_vencimento(db_emprestimo)
            self.db.add(db_emprestimo)
            self.db.commit()
            self.db.refresh(db_emprestimo)
            self._notificar_cliente(db_emprestimo, "criacao")
            logger.info(f"Empréstimo criado com sucesso: ID {db_emprestimo.id}")
            return db_emprestimo
        except Exception as e:
            logger.error(f"Erro ao criar empréstimo: {str(e)}")
            self.handle_exception(e, 400)

    @cache_decorator(expire_time=3600)
    async def obter_emprestimo(self, emprestimo_id: int):
        emprestimo = await self.db.query(Emprestimo).filter(Emprestimo.id == emprestimo_id).first()
        if not emprestimo:
            self.handle_not_found(f"Empréstimo com id {emprestimo_id} não encontrado")
        return emprestimo

    def listar_emprestimos(self, page: int = 1, per_page: int = 20, filtros: dict = None):
        query = self.db.query(Emprestimo)
        if filtros:
            if 'status' in filtros:
                query = query.filter(Emprestimo.status == filtros['status'])
            if 'cliente_id' in filtros:
                query = query.filter(Emprestimo.cliente_id == filtros['cliente_id'])
        return self.paginate(query, page, per_page)

    async def atualizar_emprestimo(self, emprestimo_id: int, emprestimo_update: EmprestimoUpdate):
        db_emprestimo = await self.obter_emprestimo(emprestimo_id)
        for key, value in emprestimo_update.model_dump(exclude_unset=True).items():
            setattr(db_emprestimo, key, value)
        db_emprestimo.atualizado_em = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_emprestimo)
        self._notificar_cliente(db_emprestimo, "atualizacao")
        await cache.delete(f"emprestimo:{emprestimo_id}")
        await cache.delete("lista_emprestimos")
        return db_emprestimo

    async def deletar_emprestimo(self, emprestimo_id: int):
        db_emprestimo = await self.obter_emprestimo(emprestimo_id)
        db_emprestimo.status = StatusEmprestimo.CANCELADO
        db_emprestimo.atualizado_em = datetime.utcnow()
        self.db.commit()
        self._notificar_cliente(db_emprestimo, "cancelamento")
        await cache.delete(f"emprestimo:{emprestimo_id}")
        await cache.delete("lista_emprestimos")
        return db_emprestimo

    def registrar_pagamento(self, emprestimo_id: int, pagamento: PagamentoCreate):
        emprestimo = self.obter_emprestimo(emprestimo_id)
        valor_devido = self.calcular_valor_total_devido(emprestimo)

        if pagamento.valor > valor_devido:
            raise ValueError("O valor do pagamento excede o valor devido")

        novo_pagamento = Pagamento(
            emprestimo_id=emprestimo.id,
            valor=pagamento.valor,
            data_pagamento=datetime.utcnow(),
            metodo_pagamento=pagamento.metodo_pagamento
        )
        self.db.add(novo_pagamento)

        if pagamento.valor >= valor_devido:
            emprestimo.status = StatusEmprestimo.QUITADO
            emprestimo.valor = Decimal('0')
        else:
            emprestimo.valor -= pagamento.valor

        emprestimo.proximo_vencimento = self._calcular_proximo_vencimento(emprestimo)
        emprestimo.atualizado_em = datetime.utcnow()

        self.db.commit()
        self.db.refresh(emprestimo)
        self._notificar_cliente(emprestimo, "pagamento")
        return emprestimo

    def calcular_valor_total_devido(self, emprestimo: Emprestimo, data_calculo: date = None):
        if data_calculo is None:
            data_calculo = date.today()

        valor_principal = Decimal(str(emprestimo.valor))
        
        regras_juros = [
            {
                'taxa': regra.taxa_juros,
                'regra': regra,
                'tipo': regra.tipo_juros
            }
            for regra in emprestimo.regras_juros
        ]
        
        regras_mora = [
            {
                'taxa': regra.taxa_mora,
                'data_vencimento': regra.data_vencimento,
                'regra': regra,
                'tipo': regra.tipo_mora
            }
            for regra in emprestimo.regras_mora
        ]

        return self.calculo_juros.calcular_valor_total_devido(
            valor_principal,
            emprestimo.data_solicitacao,
            data_calculo,
            regras_juros,
            regras_mora
        )

    def verificar_atrasos(self):
        hoje = date.today()
        emprestimos_atrasados = self.db.query(Emprestimo).filter(
            Emprestimo.proximo_vencimento < hoje,
            Emprestimo.status == StatusEmprestimo.ATIVO
        ).all()
        
        for emprestimo in emprestimos_atrasados:
            emprestimo.status = StatusEmprestimo.ATRASADO
            self._notificar_cliente(emprestimo, "atraso")
        
        self.db.commit()
        return emprestimos_atrasados

    def _criar_regras_pagamento(self, regras_dict: List[dict]):
        regras = []
        for regra in regras_dict:
            if regra['tipo'] == 'fixo':
                regras.append(RegraFixa(regra['dia'], regra.get('mes')))
            elif regra['tipo'] == 'recorrente':
                regras.append(RegraRecorrente(regra['intervalo'], regra['unidade']))
        return regras

    def _calcular_proximo_vencimento(self, emprestimo: Emprestimo, data_base: date = None):
        if data_base is None:
            data_base = date.today()
        return min(regra.proxima_data(data_base) for regra in emprestimo.regras_pagamento)

    def _notificar_cliente(self, emprestimo: Emprestimo, tipo_notificacao: str):
        cliente = emprestimo.cliente
        if not cliente:
            logger.warning(f"Cliente não encontrado para o empréstimo {emprestimo.id}")
            return

        mensagem = self._criar_mensagem_notificacao(emprestimo, tipo_notificacao)
        
        enviar_notificacao_async.delay(cliente.email, mensagem, "email")

    def _criar_mensagem_notificacao(self, emprestimo: Emprestimo, tipo_notificacao: str) -> str:
        if tipo_notificacao == "criacao":
            return f"Seu empréstimo de R${emprestimo.valor:.2f} foi criado com sucesso. Próximo vencimento: {emprestimo.proximo_vencimento.strftime('%d/%m/%Y')}"
        elif tipo_notificacao == "atualizacao":
            return f"Seu empréstimo foi atualizado. Valor atual: R${emprestimo.valor:.2f}"
        elif tipo_notificacao == "cancelamento":
            return f"Seu empréstimo de R${emprestimo.valor:.2f} foi cancelado."
        elif tipo_notificacao == "atraso":
            valor_devido = self.calcular_valor_total_devido(emprestimo)
            return f"Seu empréstimo está atrasado. Valor atual devido: R${valor_devido:.2f}. Por favor, entre em contato conosco."
        elif tipo_notificacao == "pagamento":
            return f"Recebemos seu pagamento. Saldo atual do empréstimo: R${emprestimo.valor:.2f}"
        else:
            return f"Atualização sobre seu empréstimo de R${emprestimo.valor:.2f}."

    def gerar_relatorio_emprestimos(self, data_inicio: date, data_fim: date = None):
        if data_fim is None:
            data_fim = date.today()

        emprestimos = self.db.query(Emprestimo).filter(
            Emprestimo.data_solicitacao >= data_inicio,
            Emprestimo.data_solicitacao <= data_fim
        ).all()

        total_emprestado = sum(e.valor for e in emprestimos)
        total_a_receber = sum(self.calcular_valor_total_devido(e) for e in emprestimos if e.status != StatusEmprestimo.QUITADO)
        emprestimos_ativos = sum(1 for e in emprestimos if e.status == StatusEmprestimo.ATIVO)
        emprestimos_atrasados = sum(1 for e in emprestimos if e.status == StatusEmprestimo.ATRASADO)

        return {
            "periodo": f"{data_inicio} a {data_fim}",
            "total_emprestado": total_emprestado,
            "total_a_receber": total_a_receber,
            "emprestimos_ativos": emprestimos_ativos,
            "emprestimos_atrasados": emprestimos_atrasados,
            "detalhes": [self._detalhe_emprestimo(e) for e in emprestimos]
        }

    def _detalhe_emprestimo(self, emprestimo: Emprestimo):
        valor_atual = self.calcular_valor_total_devido(emprestimo)
        return {
            "id": emprestimo.id,
            "cliente": emprestimo.cliente.nome,
            "valor_original": emprestimo.valor,
            "valor_atual": valor_atual,
            "status": emprestimo.status.value,
            "proximo_vencimento": emprestimo.proximo_vencimento
        }

    def adicionar_garantia(self, emprestimo_id: int, garantia: GarantiaCreate):
        emprestimo = self.obter_emprestimo(emprestimo_id)
        if emprestimo:
            garantia_service = GarantiaService(self.db)
            return garantia_service.criar_garantia(garantia, emprestimo_id)
        return None

    def remover_garantia(self, emprestimo_id: int, garantia_id: int):
        emprestimo = self.obter_emprestimo(emprestimo_id)
        if emprestimo:
            garantia_service = GarantiaService(self.db)
            return garantia_service.remover_garantia(garantia_id)
        return False

    def listar_garantias(self, emprestimo_id: int):
        emprestimo = self.obter_emprestimo(emprestimo_id)
        if emprestimo:
            return emprestimo.garantias
        return []