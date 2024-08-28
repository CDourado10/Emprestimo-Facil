from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.database import Base
from app.models.mixins import TimestampMixin
import enum

class TipoGarantia(enum.Enum):
    IMOVEL = "imovel"
    VEICULO = "veiculo"
    FIADOR = "fiador"
    OUTROS = "outros"

class Garantia(Base, TimestampMixin):
    __tablename__ = "garantias"

    id = Column(Integer, primary_key=True, index=True)
    emprestimo_id = Column(Integer, ForeignKey("emprestimos.id"), nullable=False)
    tipo = Column(Enum(TipoGarantia), nullable=False)
    descricao = Column(String(500), nullable=False)
    valor = Column(Float, nullable=False)

    emprestimo = relationship("Emprestimo", back_populates="garantias")

    def __repr__(self):
        return f"<Garantia(id={self.id}, tipo='{self.tipo.value}', valor={self.valor})>"
