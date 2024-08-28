#Emprestimo-Facil\app\services\estatistica_service.py

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, case
from app.models.emprestimo import Emprestimo, StatusEmprestimo
from app.models.cliente import Cliente
from app.models.pagamento import Pagamento
from app.services.emprestimo_service import EmprestimoService
from app.core.logger import get_logger
from typing import List, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal

logger = get_logger(__name__)

class EstatisticaService:
    def __init__(self, db: Session):
        self.db = db
        self.emprestimo_service = EmprestimoService(db)

    def obter_estatisticas_gerais(self) -> Dict[str, Any]:
        total_emprestimos = self.db.query(func.count(Emprestimo.id)).scalar()
        valor_total_emprestado = self.db.query(func.sum(Emprestimo.valor)).scalar() or 0
        valor_total_recebido = self.db.query(func.sum(Pagamento.valor)).scalar() or 0
        emprestimos_ativos = self.db.query(func.count(Emprestimo.id)).filter(Emprestimo.status == StatusEmprestimo.ATIVO).scalar()
        emprestimos_atrasados = self.db.query(func.count(Emprestimo.id)).filter(Emprestimo.status == StatusEmprestimo.ATRASADO).scalar()

        return {
            "total_emprestimos": total_emprestimos,
            "valor_total_emprestado": float(valor_total_emprestado),
            "valor_total_recebido": float(valor_total_recebido),
            "emprestimos_ativos": emprestimos_ativos,
            "emprestimos_atrasados": emprestimos_atrasados,
            "taxa_inadimplencia": (emprestimos_atrasados / total_emprestimos) * 100 if total_emprestimos > 0 else 0
        }

    def obter_estatisticas_cliente(self, cliente_id: int) -> Dict[str, Any]:
        emprestimos = self.db.query(Emprestimo).filter(Emprestimo.cliente_id == cliente_id).all()
        total_emprestimos = len(emprestimos)
        valor_total_emprestado = sum(e.valor for e in emprestimos)
        valor_total_pago = sum(e.valor_pago for e in emprestimos)
        emprestimos_ativos = sum(1 for e in emprestimos if e.status == StatusEmprestimo.ATIVO)
        emprestimos_atrasados = sum(1 for e in emprestimos if e.status == StatusEmprestimo.ATRASADO)

        return {
            "total_emprestimos": total_emprestimos,
            "valor_total_emprestado": float(valor_total_emprestado),
            "valor_total_pago": float(valor_total_pago),
            "emprestimos_ativos": emprestimos_ativos,
            "emprestimos_atrasados": emprestimos_atrasados,
            "taxa_inadimplencia": (emprestimos_atrasados / total_emprestimos) * 100 if total_emprestimos > 0 else 0
        }

    def obter_ranking_clientes(self, limite: int = 10, ordem: str = "desc") -> List[Dict[str, Any]]:
        query = self.db.query(
            Cliente.id,
            Cliente.nome,
            func.count(Emprestimo.id).label("total_emprestimos"),
            func.sum(Emprestimo.valor).label("valor_total_emprestado"),
            func.sum(Emprestimo.valor_pago).label("valor_total_pago")
        ).join(Emprestimo).group_by(Cliente.id)

        if ordem == "desc":
            query = query.order_by(func.sum(Emprestimo.valor_pago).desc())
        else:
            query = query.order_by(func.sum(Emprestimo.valor_pago).asc())

        resultados = query.limit(limite).all()

        return [
            {
                "id": r.id,
                "nome": r.nome,
                "total_emprestimos": r.total_emprestimos,
                "valor_total_emprestado": float(r.valor_total_emprestado),
                "valor_total_pago": float(r.valor_total_pago)
            }
            for r in resultados
        ]

    def obter_estatisticas_filtradas(self, filtros: dict) -> List[Dict[str, Any]]:
        query = self.db.query(Emprestimo)

        if 'valor_min' in filtros:
            query = query.filter(Emprestimo.valor >= filtros['valor_min'])
        if 'valor_max' in filtros:
            query = query.filter(Emprestimo.valor <= filtros['valor_max'])
        if 'data_inicio' in filtros:
            query = query.filter(Emprestimo.data_solicitacao >= filtros['data_inicio'])
        if 'data_fim' in filtros:
            query = query.filter(Emprestimo.data_solicitacao <= filtros['data_fim'])
        if 'status' in filtros:
            query = query.filter(Emprestimo.status == filtros['status'])

        emprestimos = query.all()

        return [
            {
                "id": e.id,
                "valor": e.valor,
                "status": e.status.value,
                "data_solicitacao": e.data_solicitacao,
                "data_vencimento": e.data_vencimento,
                "valor_pago": e.valor_pago,
                "cliente_id": e.cliente_id
            }
            for e in emprestimos
        ]

    def identificar_bons_pagadores(self, limite: int = 10) -> List[Dict[str, Any]]:
        query = self.db.query(
            Cliente.id,
            Cliente.nome,
            func.count(Emprestimo.id).label("total_emprestimos"),
            func.sum(Emprestimo.valor).label("valor_total_emprestado"),
            func.sum(Emprestimo.valor_pago).label("valor_total_pago")
        ).join(Emprestimo).group_by(Cliente.id).having(
            and_(
                func.count(Emprestimo.id) > 0,
                func.sum(Emprestimo.valor_pago) >= func.sum(Emprestimo.valor)
            )
        ).order_by((func.sum(Emprestimo.valor_pago) / func.sum(Emprestimo.valor)).desc())

        resultados = query.limit(limite).all()

        return [
            {
                "id": r.id,
                "nome": r.nome,
                "total_emprestimos": r.total_emprestimos,
                "valor_total_emprestado": float(r.valor_total_emprestado),
                "valor_total_pago": float(r.valor_total_pago),
                "taxa_pagamento": (r.valor_total_pago / r.valor_total_emprestado) * 100 if r.valor_total_emprestado > 0 else 0
            }
            for r in resultados
        ]

    def identificar_maus_pagadores(self, limite: int = 10) -> List[Dict[str, Any]]:
        query = self.db.query(
            Cliente.id,
            Cliente.nome,
            func.count(Emprestimo.id).label("total_emprestimos"),
            func.sum(Emprestimo.valor).label("valor_total_emprestado"),
            func.sum(Emprestimo.valor_pago).label("valor_total_pago"),
            func.sum(case((Emprestimo.status == StatusEmprestimo.ATRASADO, 1), else_=0)).label("emprestimos_atrasados")
        ).join(Emprestimo).group_by(Cliente.id).having(
            func.count(Emprestimo.id) > 0
        ).order_by(func.sum(case((Emprestimo.status == StatusEmprestimo.ATRASADO, 1), else_=0)).desc())

        resultados = query.limit(limite).all()

        return [
            {
                "id": r.id,
                "nome": r.nome,
                "total_emprestimos": r.total_emprestimos,
                "valor_total_emprestado": float(r.valor_total_emprestado),
                "valor_total_pago": float(r.valor_total_pago),
                "emprestimos_atrasados": r.emprestimos_atrasados,
                "taxa_inadimplencia": (r.emprestimos_atrasados / r.total_emprestimos) * 100 if r.total_emprestimos > 0 else 0
            }
            for r in resultados
        ]

    def projetar_fluxo_caixa(self, periodo_dias: int = 30) -> Dict[str, Any]:
        data_limite = datetime.now() + timedelta(days=periodo_dias)
        emprestimos_ativos = self.db.query(Emprestimo).filter(
            Emprestimo.status.in_([StatusEmprestimo.ATIVO, StatusEmprestimo.ATRASADO])
        ).all()

        total_a_receber = Decimal(0)
        projecao_por_dia = {}

        for emprestimo in emprestimos_ativos:
            valor_devido = self.emprestimo_service.calcular_valor_total_devido(emprestimo, data_limite)
            total_a_receber += valor_devido

            data_vencimento = emprestimo.proximo_vencimento
            if data_vencimento <= data_limite:
                dia_vencimento = data_vencimento.strftime("%Y-%m-%d")
                if dia_vencimento not in projecao_por_dia:
                    projecao_por_dia[dia_vencimento] = Decimal(0)
                projecao_por_dia[dia_vencimento] += valor_devido

        return {
            "total_a_receber": float(total_a_receber),
            "projecao_por_dia": {k: float(v) for k, v in projecao_por_dia.items()}
        }

    def analisar_tendencias(self, periodo_meses: int = 12) -> Dict[str, Any]:
        data_inicio = datetime.now() - timedelta(days=30 * periodo_meses)
        query = self.db.query(
            func.date_trunc('month', Emprestimo.data_solicitacao).label('mes'),
            func.count(Emprestimo.id).label('total_emprestimos'),
            func.sum(Emprestimo.valor).label('valor_total_emprestado'),
            func.avg(Emprestimo.taxa_juros).label('taxa_juros_media')
        ).filter(Emprestimo.data_solicitacao >= data_inicio).group_by(func.date_trunc('month', Emprestimo.data_solicitacao)).order_by('mes')

        resultados = query.all()

        return [
            {
                "mes": r.mes.strftime("%Y-%m"),
                "total_emprestimos": r.total_emprestimos,
                "valor_total_emprestado": float(r.valor_total_emprestado),
                "taxa_juros_media": float(r.taxa_juros_media)
            }
            for r in resultados
        ]