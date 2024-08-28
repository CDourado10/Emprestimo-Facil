#Emprestimo-Facil\app\api\auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import logging

from app.core.config import settings
from app.core.security import create_access_token
from app.db.database import get_db
from app.schemas.usuario import Token, UsuarioOut, UsuarioCreate
from app.services import usuario_service
from app.core.security import rate_limited

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/login", response_model=Token)
@rate_limited(max_calls=5, time_frame=60)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario = usuario_service.autenticar_usuario(db, form_data.username, form_data.password)
    if not usuario:
        logger.warning(f"Tentativa de login mal-sucedida para o usuário: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    security_settings = settings.get_security_settings()
    access_token_expires = timedelta(minutes=security_settings["ACCESS_TOKEN_EXPIRE_MINUTES"])
    access_token = create_access_token(
        subject=str(usuario.id), expires_delta=access_token_expires
    )
    usuario_service.atualizar_ultimo_login(db, usuario)
    logger.info(f"Login bem-sucedido para o usuário: {usuario.email}")
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=UsuarioOut)
@rate_limited(max_calls=3, time_frame=60)
def register_user(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    db_usuario = usuario_service.obter_usuario_por_email(db, email=usuario.email)
    if db_usuario:
        logger.warning(f"Tentativa de registro com e-mail já existente: {usuario.email}")
        raise HTTPException(status_code=400, detail="Email já registrado")
    new_user = usuario_service.criar_usuario(db=db, usuario=usuario)
    logger.info(f"Novo usuário registrado: {new_user.email}")
    return new_user