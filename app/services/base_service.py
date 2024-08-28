# app/services/base_service.py

from typing import List, TypeVar, Generic
from sqlalchemy.orm import Session
from fastapi import HTTPException, Query
import logging


T = TypeVar('T')

class BaseService(Generic[T]):
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(self.__class__.__name__)

    def handle_not_found(self, message: str):
        self.logger.warning(message)
        raise HTTPException(status_code=404, detail=message)
    
    def handle_exception(self, exception: Exception, status_code: int = 500):
        self.logger.error(f"Error: {str(exception)}")
        raise HTTPException(status_code=status_code, detail=str(exception))
    
    def paginate(self, query, page: int = Query(1, ge=1), per_page: int = Query(20, le=100)) -> List[T]:
        return query.offset((page - 1) * per_page).limit(per_page).all()

