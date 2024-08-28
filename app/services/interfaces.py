# app/services/interfaces.py

from abc import ABC, abstractmethod
from typing import List, Optional
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate, Usuario
from app.schemas.cliente import ClienteCreate, ClienteUpdate, Cliente
from app.schemas.emprestimo import EmprestimoCreate, EmprestimoUpdate, Emprestimo

class IUsuarioService(ABC):
    @abstractmethod
    def criar_usuario(self, usuario: UsuarioCreate) -> Usuario:
        pass

    @abstractmethod
    def obter_usuario(self, usuario_id: int) -> Optional[Usuario]:
        pass

    @abstractmethod
    def obter_usuario_por_email(self, email: str) -> Optional[Usuario]:
        pass

    @abstractmethod
    def listar_usuarios(self, page: int, per_page: int) -> List[Usuario]:
        pass

    @abstractmethod
    def atualizar_usuario(self, usuario_id: int, usuario: UsuarioUpdate) -> Optional[Usuario]:
        pass

    @abstractmethod
    def deletar_usuario(self, usuario_id: int) -> Optional[Usuario]:
        pass

    @abstractmethod
    def autenticar_usuario(self, email: str, senha: str) -> Optional[Usuario]:
        pass

    @abstractmethod
    def atualizar_ultimo_login(self, usuario: Usuario) -> None:
        pass

class IClienteService(ABC):
    @abstractmethod
    def criar_cliente(self, cliente: ClienteCreate) -> Cliente:
        pass

    @abstractmethod
    def obter_cliente(self, cliente_id: int) -> Optional[Cliente]:
        pass

    @abstractmethod
    def listar_clientes(self, page: int, per_page: int) -> List[Cliente]:
        pass

    @abstractmethod
    def atualizar_cliente(self, cliente_id: int, cliente: ClienteUpdate) -> Optional[Cliente]:
        pass

    @abstractmethod
    def deletar_cliente(self, cliente_id: int) -> Optional[Cliente]:
        pass

class IEmprestimoService(ABC):
    @abstractmethod
    def criar_emprestimo(self, emprestimo: EmprestimoCreate) -> Emprestimo:
        pass

    @abstractmethod
    def obter_emprestimo(self, emprestimo_id: int) -> Optional[Emprestimo]:
        pass

    @abstractmethod
    def listar_emprestimos(self, page: int, per_page: int) -> List[Emprestimo]:
        pass

    @abstractmethod
    def atualizar_emprestimo(self, emprestimo_id: int, emprestimo: EmprestimoUpdate) -> Optional[Emprestimo]:
        pass

    @abstractmethod
    def deletar_emprestimo(self, emprestimo_id: int) -> Optional[Emprestimo]:
        pass

    @abstractmethod
    def calcular_juros(self, emprestimo: Emprestimo) -> float:
        pass

    @abstractmethod
    def verificar_atrasos(self) -> List[Emprestimo]:
        pass