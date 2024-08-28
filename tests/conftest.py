#Emprestimo-Facil\tests\conftest.py

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import Base
from app.core.config import settings
from main import app
from fastapi.testclient import TestClient
from app.services import usuario_service
from app.schemas.usuario import UsuarioCreate

# Configuração do banco de dados de teste
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def test_app():
    client = TestClient(app)
    yield client

@pytest.fixture(scope="module")
def test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def test_user(test_db):
    user = usuario_service.criar_usuario(
        test_db,
        UsuarioCreate(
            email="testuser@example.com",
            senha="testpassword",
            nome_completo="Test User"
        )
    )
    return user

@pytest.fixture(scope="module")
def test_auth_header(test_app, test_user):
    login_data = {
        "username": "testuser@example.com",
        "password": "testpassword"
    }
    response = test_app.post("/api/v1/auth/login", data=login_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}