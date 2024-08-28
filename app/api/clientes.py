#Emprestimo-Facil\app\api\clientes.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
import logging
from app.db.database import get_db
from app.schemas.cliente import Cliente, ClienteCreate, ClienteUpdate
from app.schemas.usuario import Usuario
from app.services import cliente_service
from app.api.deps import get_current_user
from app.core.security import rate_limited

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=Cliente)
@rate_limited(max_calls=10, time_frame=60)
def criar_cliente(
    cliente: ClienteCreate, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Apenas administradores podem criar novos clientes")
    new_cliente = cliente_service.criar_cliente(db=db, cliente=cliente)
    logger.info(f"Novo cliente criado por {current_user.email}: {new_cliente.id}")
    return new_cliente

@router.get("/", response_model=List[Cliente])
def listar_clientes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100), 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    clientes = cliente_service.listar_clientes(db, skip=skip, limit=limit)
    logger.info(f"Lista de clientes acessada por {current_user.email}")
    return clientes

@router.get("/{cliente_id}", response_model=Cliente)
def obter_cliente(
    cliente_id: int, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    db_cliente = cliente_service.obter_cliente(db, cliente_id=cliente_id)
    if db_cliente is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    logger.info(f"Cliente {cliente_id} acessado por {current_user.email}")
    return db_cliente

@router.put("/{cliente_id}", response_model=Cliente)
def atualizar_cliente(
    cliente_id: int, 
    cliente: ClienteUpdate, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Apenas administradores podem atualizar clientes")
    db_cliente = cliente_service.atualizar_cliente(db, cliente_id=cliente_id, cliente=cliente)
    if db_cliente is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    logger.info(f"Cliente {cliente_id} atualizado por {current_user.email}")
    return db_cliente

@router.delete("/{cliente_id}", response_model=Cliente)
def deletar_cliente(
    cliente_id: int, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Apenas administradores podem deletar clientes")
    db_cliente = cliente_service.deletar_cliente(db, cliente_id=cliente_id)
    if db_cliente is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    logger.info(f"Cliente {cliente_id} deletado por {current_user.email}")
    return db_cliente