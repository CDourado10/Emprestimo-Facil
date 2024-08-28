#Emprestimo-Facil\app\api\usuarios.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
import logging

from app.db.database import get_db
from app.schemas.usuario import UsuarioOut, UsuarioUpdate
from app.services import usuario_service
from app.api.deps import get_current_user
from app.core.security import rate_limited

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[UsuarioOut])
def listar_usuarios(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100), 
    db: Session = Depends(get_db),
    current_user: UsuarioOut = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Não autorizado")
    usuarios = usuario_service.listar_usuarios(db, skip=skip, limit=limit)
    logger.info(f"Lista de usuários acessada por {current_user.email}")
    return usuarios

@router.get("/{user_id}", response_model=UsuarioOut)
def obter_usuario(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: UsuarioOut = Depends(get_current_user)
):
    if not current_user.is_admin and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Não autorizado")
    db_usuario = usuario_service.obter_usuario(db, usuario_id=user_id)
    if db_usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    logger.info(f"Usuário {user_id} acessado por {current_user.email}")
    return db_usuario

@router.put("/{user_id}", response_model=UsuarioOut)
@rate_limited(max_calls=5, time_frame=60)
def atualizar_usuario(
    user_id: int,
    usuario: UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user: UsuarioOut = Depends(get_current_user)
):
    if not current_user.is_admin and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Não autorizado")
    db_usuario = usuario_service.atualizar_usuario(db, user_id, usuario)
    if db_usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    logger.info(f"Usuário {user_id} atualizado por {current_user.email}")
    return db_usuario

@router.delete("/{user_id}", response_model=UsuarioOut)
def deletar_usuario(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UsuarioOut = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Não autorizado")
    db_usuario = usuario_service.deletar_usuario(db, user_id)
    if db_usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    logger.info(f"Usuário {user_id} deletado por {current_user.email}")
    return db_usuario