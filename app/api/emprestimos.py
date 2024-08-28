#Emprestimo-Facil\app\api\emprestimos.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.logger import get_logger
from app.db.database import get_db
from app.schemas.emprestimo import Emprestimo, EmprestimoCreate, EmprestimoUpdate
from app.services import emprestimo_service
from app.api.deps import get_current_user
from app.schemas.usuario import Usuario
from app.core.security import rate_limited
from app.services.estatistica_service import EstatisticaService
from typing import Dict, Any

router = APIRouter()
logger = get_logger(__name__)

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

@router.get("/estatisticas/gerais", response_model=Dict[str, Any])
def obter_estatisticas_gerais(db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    estatistica_service = EstatisticaService(db)
    return estatistica_service.obter_estatisticas_gerais()

@router.get("/estatisticas/cliente/{cliente_id}", response_model=Dict[str, Any])
def obter_estatisticas_cliente(cliente_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    estatistica_service = EstatisticaService(db)
    return estatistica_service.obter_estatisticas_cliente(cliente_id)

@router.get("/estatisticas/ranking-clientes", response_model=List[Dict[str, Any]])
def obter_ranking_clientes(
    limite: int = Query(10, ge=1, le=100),
    ordem: str = Query("desc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    estatistica_service = EstatisticaService(db)
    return estatistica_service.obter_ranking_clientes(limite, ordem)

@router.get("/estatisticas/filtradas", response_model=Dict[str, Any])
def obter_estatisticas_filtradas(
    valor_min: float = Query(None, ge=0),
    valor_max: float = Query(None, ge=0),
    data_inicio: str = Query(None),
    data_fim: str = Query(None),
    status: str = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    filtros = {
        "valor_min": valor_min,
        "valor_max": valor_max,
        "data_inicio": data_inicio,
        "data_fim": data_fim,
        "status": status
    }
    filtros = {k: v for k, v in filtros.items() if v is not None}
    estatistica_service = EstatisticaService(db)
    return estatistica_service.obter_estatisticas_filtradas(filtros)

@router.get("/estatisticas/bons-pagadores", response_model=List[Dict[str, Any]])
def identificar_bons_pagadores(
    limite: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    estatistica_service = EstatisticaService(db)
    return estatistica_service.identificar_bons_pagadores(limite)

@router.get("/estatisticas/maus-pagadores", response_model=List[Dict[str, Any]])
def identificar_maus_pagadores(
    limite: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    estatistica_service = EstatisticaService(db)
    return estatistica_service.identificar_maus_pagadores(limite)

@router.get("/estatisticas/projecao-caixa", response_model=Dict[str, Any])
def projetar_fluxo_caixa(
    periodo_dias: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    estatistica_service = EstatisticaService(db)
    return estatistica_service.projetar_fluxo_caixa(periodo_dias)

@router.get("/estatisticas/tendencias", response_model=List[Dict[str, Any]])
def analisar_tendencias(
    periodo_meses: int = Query(12, ge=1, le=60),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    estatistica_service = EstatisticaService(db)
    return estatistica_service.analisar_tendencias(periodo_meses)