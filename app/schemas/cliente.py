#Emprestimo-Facil\app\schemas\cliente.py

from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional
from .base import TimestampedModel
import re

class ClienteBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    telefone: str = Field(..., max_length=20)
    cpf: str = Field(..., min_length=11, max_length=14)
    data_nascimento: datetime
    endereco: Optional[str] = Field(None, max_length=200)

    @field_validator('cpf')
    @classmethod
    def cpf_valido(cls, v: str) -> str:
        if not re.match(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$', v):
            raise ValueError('CPF inválido')
        return v

class ClienteCreate(ClienteBase):
    pass

class ClienteUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    telefone: Optional[str] = Field(None, max_length=20)
    endereco: Optional[str] = Field(None, max_length=200)

class Cliente(ClienteBase, TimestampedModel):
    id: int
    ativo: bool
    criado_em: datetime
    atualizado_em: Optional[datetime] = None

    class Config:
        orm_mode = True