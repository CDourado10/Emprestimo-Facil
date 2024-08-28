#Emprestimo-Facil\app\schemas\emprestimo.py

from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional
from app.models.emprestimo import StatusEmprestimo
from .base import TimestampedModel

class EmprestimoBase(BaseModel):
    valor: float = Field(..., gt=0)
    taxa_juros: float = Field(..., ge=0)
    data_vencimento: date
    status: StatusEmprestimo = StatusEmprestimo.PENDENTE

class EmprestimoCreate(EmprestimoBase):
    cliente_id: int

class EmprestimoUpdate(BaseModel):
    valor: Optional[float] = Field(None, gt=0)
    taxa_juros: Optional[float] = Field(None, ge=0)
    data_vencimento: Optional[date] = None
    status: Optional[StatusEmprestimo] = None

class Emprestimo(EmprestimoBase, TimestampedModel):
    id: int
    cliente_id: int
    data_solicitacao: datetime
    data_aprovacao: Optional[datetime] = None
    valor_total: Optional[float] = None
    valor_pago: float = 0
    observacoes: Optional[str] = None
    criado_em: datetime
    atualizado_em: Optional[datetime] = None

    class Config:
        orm_mode = True

class PagamentoBase(BaseModel):
    valor: float = Field(..., gt=0)
    metodo_pagamento: str = Field(..., max_length=50)

class PagamentoCreate(PagamentoBase):
    emprestimo_id: int

class Pagamento(PagamentoBase, TimestampedModel):
    id: int
    emprestimo_id: int
    data_pagamento: datetime

    class Config:
        orm_mode = True