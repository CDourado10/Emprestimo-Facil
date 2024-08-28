#Emprestimo-Facil\app\services\usuario_service.py

from sqlalchemy.orm import Session
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate
from app.core.security import get_password_hash, verify_password
from datetime import datetime
from app.core.config import settings
from .base_service import BaseService
from typing import List, Optional


class UsuarioService(BaseService):
    def criar_usuario(self, usuario: UsuarioCreate):
        try:
            hashed_password = get_password_hash(usuario.senha)
            db_usuario = Usuario(**usuario.model_dump(exclude={'senha'}), hashed_password=hashed_password)
            self.db.add(db_usuario)
            self.db.commit()
            self.db.refresh(db_usuario)
            self.logger.info(f"Usuário criado com sucesso: {db_usuario.email}")
            return db_usuario
        except Exception as e:
            self.handle_exception(e, 400)

    def obter_usuario(self, usuario_id: int) -> Optional[Usuario]:
        usuario = self.db.query(Usuario).filter(Usuario.id == usuario_id).first()
        if not usuario:
            self.handle_not_found(f"Usuário com id {usuario_id} não encontrado")
        return usuario

    def obter_usuario_por_email(self, email: str) -> Optional[Usuario]:
        return self.db.query(Usuario).filter(Usuario.email == email).first()

    def listar_usuarios(self, page: int = 1, per_page: int = None):
        if per_page is None:
            per_page = settings.get_pagination_settings()["PAGE_SIZE"]
        query = self.db.query(Usuario)
        return self.paginate(query, page, per_page)

    def atualizar_usuario(self, usuario_id: int, usuario: UsuarioUpdate):
        try:
            db_usuario = self.obter_usuario(usuario_id)
            if db_usuario:
                update_data = usuario.model_dump(exclude_unset=True)
                if 'senha' in update_data:
                    update_data['hashed_password'] = get_password_hash(update_data.pop('senha'))
                for key, value in update_data.items():
                    setattr(db_usuario, key, value)
                db_usuario.updated_at = datetime.utcnow()
                self.db.commit()
                self.db.refresh(db_usuario)
                self.logger.info(f"Usuário atualizado com sucesso: {db_usuario.email}")
            return db_usuario
        except Exception as e:
            self.handle_exception(e, 400)

    def deletar_usuario(self, usuario_id: int):
        try:
            db_usuario = self.obter_usuario(usuario_id)
            if db_usuario:
                db_usuario.is_active = False
                db_usuario.updated_at = datetime.utcnow()
                self.db.commit()
                self.logger.info(f"Usuário desativado com sucesso: {db_usuario.email}")
            return db_usuario
        except Exception as e:
            self.handle_exception(e, 400)

    def autenticar_usuario(self, email: str, senha: str) -> Optional[Usuario]:
        try:
            usuario = self.obter_usuario_por_email(email)
            if not usuario or not usuario.is_active:
                return None
            if not verify_password(senha, usuario.hashed_password):
                return None
            return usuario
        except Exception as e:
            self.handle_exception(e, 400)

    def atualizar_ultimo_login(self, usuario: Usuario):
        try:
            usuario.last_login = datetime.utcnow()
            self.db.commit()
            self.logger.info(f"Último login atualizado para o usuário: {usuario.email}")
        except Exception as e:
            self.handle_exception(e, 400)