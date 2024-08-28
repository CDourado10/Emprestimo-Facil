from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String, func
from sqlalchemy.orm import relationship
from app.db.database import Base
from app.models.mixins import TimestampMixin

class Pagamento(Base, TimestampMixin):
    __tablename__ = "pagamentos"

    id = Column(Integer, primary_key=True, index=True)
    emprestimo_id = Column(Integer, ForeignKey("emprestimos.id"), nullable=False)
    valor = Column(Float, nullable=False)
    data_pagamento = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    metodo_pagamento = Column(String(50), nullable=False)

    emprestimo = relationship("Emprestimo", back_populates="pagamentos")

    def __repr__(self):
        return f"<Pagamento(id={self.id}, emprestimo_id={self.emprestimo_id}, valor={self.valor})>"
