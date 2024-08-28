#Emprestimo-Facil\app\schemas\usuario.py

from pydantic import BaseModel, EmailStr, Field, field_validator
import re
from typing import Optional
from datetime import datetime
from app.models.usuario import TipoUsuario
from .base import TimestampedModel

class UsuarioBase(BaseModel):
    email: EmailStr
    nome_completo: str = Field(..., min_length=1, max_length=100)
    tipo: TipoUsuario = TipoUsuario.CLIENTE
    is_active: bool = True
    telefone: Optional[str] = Field(None, max_length=20)

class UsuarioCreate(UsuarioBase):
    senha: str = Field(..., min_length=8)

    @field_validator('senha')
    @classmethod
    def senha_forte(cls, v):
        if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$', v):
            raise ValueError('A senha deve conter pelo menos 8 caracteres, incluindo letras e números')
        return v

class UsuarioUpdate(BaseModel):
    email: Optional[EmailStr] = None
    nome_completo: Optional[str] = Field(None, min_length=1, max_length=100)
    senha: Optional[str] = Field(None, min_length=8)
    tipo: Optional[TipoUsuario] = None
    is_active: Optional[bool] = None
    telefone: Optional[str] = Field(None, max_length=20)

class UsuarioInDB(UsuarioBase, TimestampedModel):
    id: int
    hashed_password: str
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    class Config:
        orm_mode = True

class Usuario(UsuarioInDB):
    pass

class UsuarioOut(BaseModel):
    id: int
    email: EmailStr
    nome_completo: str
    tipo: TipoUsuario
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[int] = None
    tipo: Optional[TipoUsuario] = None