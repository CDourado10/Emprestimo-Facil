#Emprestimo-Facil\app\models\usuario.py

from sqlalchemy import Boolean, Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
from app.db.database import Base
import enum
from app.models.mixins import TimestampMixin

class TipoUsuario(enum.Enum):
    ADMIN = "admin"
    OPERADOR = "operador"
    CLIENTE = "cliente"

class Usuario(Base, TimestampMixin):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    nome_completo = Column(String(100), index=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    tipo = Column(Enum(TipoUsuario), default=TipoUsuario.CLIENTE, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    telefone = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))

    def __repr__(self):
        return f"<Usuario(id={self.id}, email='{self.email}', tipo='{self.tipo.value}')>"