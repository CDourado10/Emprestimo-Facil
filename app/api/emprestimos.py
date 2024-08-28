#Emprestimo-Facil\app\api\emprestimos.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
import logging
from app.db.database import get_db
from app.schemas.emprestimo import Emprestimo, EmprestimoCreate, EmprestimoUpdate
from app.services import emprestimo_service
from app.api.deps import get_current_user
from app.schemas.usuario import Usuario
from app.core.security import rate_limited

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=Emprestimo)
@rate_limited(max_calls=5, time_frame=60)
def criar_emprestimo(
    emprestimo: EmprestimoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    new_emprestimo = emprestimo_service.criar_emprestimo(db=db, emprestimo=emprestimo, user_id=current_user.id)
    logger.info(f"Novo empréstimo criado por {current_user.email}: {new_emprestimo.id}")
    return new_emprestimo

@router.get("/", response_model=List[Emprestimo])
def listar_emprestimos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    emprestimos = emprestimo_service.listar_emprestimos(db, skip=skip, limit=limit, user_id=current_user.id)
    logger.info(f"Lista de empréstimos acessada por {current_user.email}")
    return emprestimos

@router.get("/{emprestimo_id}", response_model=Emprestimo)
def obter_emprestimo(
    emprestimo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    db_emprestimo = emprestimo_service.obter_emprestimo(db, emprestimo_id=emprestimo_id, user_id=current_user.id)
    if db_emprestimo is None:
        raise HTTPException(status_code=404, detail="Empréstimo não encontrado ou não autorizado")
    logger.info(f"Empréstimo {emprestimo_id} acessado por {current_user.email}")
    return db_emprestimo

@router.put("/{emprestimo_id}", response_model=Emprestimo)
def atualizar_emprestimo(
    emprestimo_id: int,
    emprestimo: EmprestimoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    db_emprestimo = emprestimo_service.atualizar_emprestimo(db, emprestimo_id=emprestimo_id, emprestimo=emprestimo, user_id=current_user.id)
    if db_emprestimo is None:
        raise HTTPException(status_code=404, detail="Empréstimo não encontrado ou não autorizado")
    logger.info(f"Empréstimo {emprestimo_id} atualizado por {current_user.email}")
    return db_emprestimo

@router.delete("/{emprestimo_id}", response_model=Emprestimo)
def deletar_emprestimo(
    emprestimo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    db_emprestimo = emprestimo_service.deletar_emprestimo(db, emprestimo_id=emprestimo_id, user_id=current_user.id)
    if db_emprestimo is None:
        raise HTTPException(status_code=404, detail="Empréstimo não encontrado ou não autorizado")
    logger.info(f"Empréstimo {emprestimo_id} deletado por {current_user.email}")
    return db_emprestimo