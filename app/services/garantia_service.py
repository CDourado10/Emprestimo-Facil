from sqlalchemy.orm import Session
from app.models.garantia import Garantia
from app.schemas.garantia import GarantiaCreate, GarantiaUpdate
from .base_service import BaseService
from app.core.logger import get_logger

logger = get_logger(__name__)

class GarantiaService(BaseService[Garantia, GarantiaCreate, GarantiaUpdate]):
    def __init__(self, db: Session):
        super().__init__(Garantia, db)

    def criar_garantia(self, garantia: GarantiaCreate, emprestimo_id: int):
        db_garantia = Garantia(**garantia.dict(), emprestimo_id=emprestimo_id)
        self.db.add(db_garantia)
        self.db.commit()
        self.db.refresh(db_garantia)
        logger.info(f"Garantia criada para o empréstimo {emprestimo_id}")
        return db_garantia

    def atualizar_garantia(self, garantia_id: int, garantia: GarantiaUpdate):
        db_garantia = self.obter(garantia_id)
        if db_garantia:
            for key, value in garantia.dict(exclude_unset=True).items():
                setattr(db_garantia, key, value)
            self.db.commit()
            self.db.refresh(db_garantia)
            logger.info(f"Garantia {garantia_id} atualizada")
            return db_garantia
        return None

    def remover_garantia(self, garantia_id: int):
        db_garantia = self.obter(garantia_id)
        if db_garantia:
            self.db.delete(db_garantia)
            self.db.commit()
            logger.info(f"Garantia {garantia_id} removida")
            return True
        return False
