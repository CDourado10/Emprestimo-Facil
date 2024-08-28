#Emprestimo-Facil\app\models\cliente.py

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from app.db.database import Base
from app.models.mixins import TimestampMixin
import re

class Cliente(Base, TimestampMixin):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    telefone = Column(String(20))
    cpf = Column(String(14), unique=True, index=True, nullable=True)
    data_nascimento = Column(DateTime, nullable=False)
    endereco = Column(String(200))
    ativo = Column(Boolean, default=True, nullable=False)
    criado_em = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())

    emprestimos = relationship("Emprestimo", back_populates="cliente", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Cliente(id={self.id}, nome='{self.nome}', email='{self.email}')>"
    
    @validates('email')
    def validate_email(self, key, address):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", address):
            raise ValueError("Invalid email address")
        return address

    @validates('cpf')
    def validate_cpf(self, key, cpf):
        if not re.match(r"^\d{3}\.\d{3}\.\d{3}-\d{2}$", cpf):
            raise ValueError("Invalid CPF format")
        return cpf