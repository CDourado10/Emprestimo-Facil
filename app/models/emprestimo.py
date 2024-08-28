#Emprestimo-Facil\app\models\emprestimo.py

from sqlalchemy import Column, Integer, Float, Date, ForeignKey, String, DateTime, Enum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum
from app.models.mixins import TimestampMixin

class StatusEmprestimo(enum.Enum):
    PENDENTE = "pendente"
    APROVADO = "aprovado"
    ATIVO = "ativo"
    QUITADO = "quitado"
    ATRASADO = "atrasado"
    CANCELADO = "cancelado"

class Emprestimo(Base, TimestampMixin):
    __tablename__ = "emprestimos"
    

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    valor = Column(Float, nullable=False)
    taxa_juros = Column(Float, nullable=False)
    data_solicitacao = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    data_aprovacao = Column(DateTime(timezone=True))
    data_vencimento = Column(Date, nullable=False)
    status = Column(Enum(StatusEmprestimo), default=StatusEmprestimo.PENDENTE, nullable=False)
    valor_total = Column(Float)
    valor_pago = Column(Float, default=0)
    observacoes = Column(String(500))
    criado_em = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())

    cliente = relationship("Cliente", back_populates="emprestimos")
    pagamentos = relationship("Pagamento", back_populates="emprestimo", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_cliente_status', 'cliente_id', 'status'),
        Index('idx_data_vencimento', 'data_vencimento'),
    )

    def __repr__(self):
        return f"<Emprestimo(id={self.id}, cliente_id={self.cliente_id}, valor={self.valor}, status='{self.status.value}')>"

class Pagamento(Base):
    __tablename__ = "pagamentos"

    id = Column(Integer, primary_key=True, index=True)
    emprestimo_id = Column(Integer, ForeignKey("emprestimos.id"), nullable=False)
    valor = Column(Float, nullable=False)
    data_pagamento = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    metodo_pagamento = Column(String(50), nullable=False)

    emprestimo = relationship("Emprestimo", back_populates="pagamentos")

    def __repr__(self):
        return f"<Pagamento(id={self.id}, emprestimo_id={self.emprestimo_id}, valor={self.valor})>"