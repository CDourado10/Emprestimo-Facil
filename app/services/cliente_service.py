#Emprestimo-Facil\app\services\cliente_service.py

from sqlalchemy.orm import Session
from app.models.cliente import Cliente
from app.schemas.cliente import ClienteCreate, ClienteUpdate
from datetime import datetime
from .base_service import BaseService
from typing import List

class ClienteService(BaseService):
    def criar_cliente(self, cliente: ClienteCreate):
        try:
            db_cliente = Cliente(**cliente.model_dump())
            self.db.add(db_cliente)
            self.db.commit()
            self.db.refresh(db_cliente)
            self.logger.info(f"Cliente criado com sucesso: {db_cliente.id}")
            return db_cliente
        except Exception as e:
            self.handle_exception(e, 400)

    def obter_cliente(db: Session, cliente_id: int):
        return db.query(Cliente).filter(Cliente.id == cliente_id, Cliente.ativo == True).first()
    
    def listar_clientes(self, page: int = 1, per_page: int = 20) -> List[Cliente]:
        query = self.db.query(Cliente).filter(Cliente.ativo == True)
        return self.paginate(query, page, per_page)

    def atualizar_cliente(db: Session, cliente_id: int, cliente: ClienteUpdate):
        db_cliente = db.query(Cliente).filter(Cliente.id == cliente_id, Cliente.ativo == True).first()
        if db_cliente:
            update_data = cliente.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_cliente, key, value)
            db_cliente.atualizado_em = datetime.utcnow()
            db.commit()
            db.refresh(db_cliente)
        return db_cliente

    def deletar_cliente(db: Session, cliente_id: int):
        db_cliente = db.query(Cliente).filter(Cliente.id == cliente_id, Cliente.ativo == True).first()
        if db_cliente:
            db_cliente.ativo = False
            db_cliente.atualizado_em = datetime.utcnow()
            db.commit()
        return db_cliente