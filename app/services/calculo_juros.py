# app/services/calculo_juros.py

from abc import ABC, abstractmethod
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from typing import List, Optional
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum

class TipoJuros(Enum):
    SIMPLES = "simples"
    COMPOSTO = "composto"

class TipoMora(Enum):
    SIMPLES = "simples"
    COMPOSTO = "composto"
    DIARIO = "diario"

class TipoRegra(Enum):
    FIXO = "fixo"
    RECORRENTE = "recorrente"

class BaseRegra(ABC):
    @abstractmethod
    def proxima_data(self, data_base: date) -> date:
        pass

class RegraFixa(BaseRegra):
    def __init__(self, dia: int, mes: Optional[int] = None):
        self.dia = dia
        self.mes = mes

    def proxima_data(self, data_base: date) -> date:
        if self.mes:
            # Regra anual
            prox_data = date(data_base.year, self.mes, self.dia)
            if prox_data <= data_base:
                prox_data = date(data_base.year + 1, self.mes, self.dia)
        else:
            # Regra mensal
            prox_data = data_base.replace(day=self.dia)
            if prox_data <= data_base:
                prox_data += relativedelta(months=1)
        return prox_data

class RegraRecorrente(BaseRegra):
    def __init__(self, intervalo: int, unidade: str):
        self.intervalo = intervalo
        self.unidade = unidade

    def proxima_data(self, data_base: date) -> date:
        if self.unidade == 'dias':
            return data_base + timedelta(days=self.intervalo)
        elif self.unidade == 'semanas':
            return data_base + timedelta(weeks=self.intervalo)
        elif self.unidade == 'meses':
            return data_base + relativedelta(months=self.intervalo)
        elif self.unidade == 'anos':
            return data_base + relativedelta(years=self.intervalo)
        else:
            raise ValueError(f"Unidade de tempo inválida: {self.unidade}")

class CalculoJuros:
    @staticmethod
    def calcular_periodo_base(regra: BaseRegra, data_base: date) -> int:
        proxima_data = regra.proxima_data(data_base)
        return (proxima_data - data_base).days

    @staticmethod
    def calcular_juros(valor_principal: Decimal, taxa_juros: Decimal, data_inicio: date, data_fim: date, regra: BaseRegra, tipo_juros: TipoJuros) -> Decimal:
        periodo_base = CalculoJuros.calcular_periodo_base(regra, data_inicio)
        dias = (data_fim - data_inicio).days
        taxa_ajustada = taxa_juros * (Decimal(dias) / Decimal(periodo_base))
        
        if tipo_juros == TipoJuros.SIMPLES:
            return valor_principal * (taxa_ajustada / Decimal('100'))
        elif tipo_juros == TipoJuros.COMPOSTO:
            return valor_principal * ((1 + taxa_ajustada / Decimal('100')) - 1)
        else:
            raise ValueError("Tipo de juros não suportado")

    @staticmethod
    def calcular_mora(valor_principal: Decimal, taxa_mora: Decimal, data_vencimento: date, data_pagamento: date, regra: BaseRegra, tipo_mora: TipoMora) -> Decimal:
        periodo_base = CalculoJuros.calcular_periodo_base(regra, data_vencimento)
        dias_atraso = (data_pagamento - data_vencimento).days
        if dias_atraso <= 0:
            return Decimal('0')

        taxa_ajustada = taxa_mora * (Decimal(dias_atraso) / Decimal(periodo_base))
        
        if tipo_mora == TipoMora.SIMPLES:
            return valor_principal * (taxa_ajustada / Decimal('100'))
        elif tipo_mora == TipoMora.COMPOSTO:
            return valor_principal * ((1 + taxa_ajustada / Decimal('100')) - 1)
        elif tipo_mora == TipoMora.DIARIO:
            taxa_diaria = taxa_mora / Decimal(periodo_base)
            return valor_principal * (taxa_diaria / Decimal('100')) * dias_atraso
        else:
            raise ValueError("Tipo de mora não suportado")

    @staticmethod
    def calcular_valor_total_devido(
        valor_principal: Decimal,
        data_inicio: date,
        data_calculo: date,
        regras_juros: List[dict],
        regras_mora: List[dict]
    ) -> Decimal:
        total_juros = Decimal('0')
        total_mora = Decimal('0')

        for regra_juros in regras_juros:
            juros = CalculoJuros.calcular_juros(
                valor_principal,
                Decimal(str(regra_juros['taxa'])),
                data_inicio,
                data_calculo,
                regra_juros['regra'],
                regra_juros['tipo']
            )
            total_juros += juros

        for regra_mora in regras_mora:
            if data_calculo > regra_mora['data_vencimento']:
                mora = CalculoJuros.calcular_mora(
                    valor_principal,
                    Decimal(str(regra_mora['taxa'])),
                    regra_mora['data_vencimento'],
                    data_calculo,
                    regra_mora['regra'],
                    regra_mora['tipo']
                )
                total_mora += mora

        return CalculoJuros.calcular_total_devido(valor_principal, total_juros, total_mora)

    @staticmethod
    def calcular_parcelas(valor_total: Decimal, num_parcelas: int) -> List[Decimal]:
        valor_parcela = valor_total / num_parcelas
        parcelas = [valor_parcela.quantize(Decimal('.01'), rounding=ROUND_HALF_UP) for _ in range(num_parcelas)]
        parcelas[-1] += valor_total - sum(parcelas)
        return parcelas

    @staticmethod
    def calcular_amortizacao(valor_principal: Decimal, taxa_juros: Decimal, num_parcelas: int, regra: BaseRegra, tipo_juros: TipoJuros) -> List[dict]:
        if tipo_juros == TipoJuros.SIMPLES:
            return CalculoJuros._amortizacao_sac(valor_principal, taxa_juros, num_parcelas, regra)
        elif tipo_juros == TipoJuros.COMPOSTO:
            return CalculoJuros._amortizacao_price(valor_principal, taxa_juros, num_parcelas, regra)
        else:
            raise ValueError("Tipo de juros não suportado para amortização")

    @staticmethod
    def _amortizacao_price(valor_principal: Decimal, taxa_juros: Decimal, num_parcelas: int, regra: BaseRegra) -> List[dict]:
        periodo_base = CalculoJuros.calcular_periodo_base(regra, date.today())
        taxa = (taxa_juros / Decimal('100')) * (Decimal(periodo_base) / Decimal(365))
        parcela = valor_principal * (taxa * (1 + taxa) ** num_parcelas) / ((1 + taxa) ** num_parcelas - 1)
        saldo_devedor = valor_principal
        amortizacao = []

        for _ in range(num_parcelas):
            juros = saldo_devedor * taxa
            amortizado = parcela - juros
            saldo_devedor -= amortizado
            amortizacao.append({
                "parcela": parcela.quantize(Decimal('.01'), rounding=ROUND_HALF_UP),
                "juros": juros.quantize(Decimal('.01'), rounding=ROUND_HALF_UP),
                "amortizado": amortizado.quantize(Decimal('.01'), rounding=ROUND_HALF_UP),
                "saldo_devedor": saldo_devedor.quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
            })

        return amortizacao

    @staticmethod
    def _amortizacao_sac(valor_principal: Decimal, taxa_juros: Decimal, num_parcelas: int, regra: BaseRegra) -> List[dict]:
        periodo_base = CalculoJuros.calcular_periodo_base(regra, date.today())
        taxa = (taxa_juros / Decimal('100')) * (Decimal(periodo_base) / Decimal(365))
        amortizado = valor_principal / num_parcelas
        saldo_devedor = valor_principal
        amortizacao = []

        for _ in range(num_parcelas):
            juros = saldo_devedor * taxa
            parcela = amortizado + juros
            saldo_devedor -= amortizado
            amortizacao.append({
                "parcela": parcela.quantize(Decimal('.01'), rounding=ROUND_HALF_UP),
                "juros": juros.quantize(Decimal('.01'), rounding=ROUND_HALF_UP),
                "amortizado": amortizado.quantize(Decimal('.01'), rounding=ROUND_HALF_UP),
                "saldo_devedor": saldo_devedor.quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
            })

        return amortizacao

    @staticmethod
    def calcular_prazo_maximo(valor_principal: Decimal, taxa_juros: Decimal, valor_maximo: Decimal, regra: BaseRegra, tipo_juros: TipoJuros) -> int:
        periodo_base = CalculoJuros.calcular_periodo_base(regra, date.today())
        taxa_ajustada = taxa_juros * (Decimal(periodo_base) / Decimal(365))
        if tipo_juros == TipoJuros.SIMPLES:
            return int((valor_maximo / valor_principal - 1) / (taxa_ajustada / Decimal('100')))
        elif tipo_juros == TipoJuros.COMPOSTO:
            return int(Decimal.ln(valor_maximo / valor_principal) / Decimal.ln(1 + taxa_ajustada / Decimal('100')))
        else:
            raise ValueError("Tipo de juros não suportado para cálculo de prazo máximo")