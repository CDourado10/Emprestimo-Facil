#Emprestimo-Facil\tests\test_auth.py

import pytest
from app.core.config import settings

def test_criar_usuario(test_app, test_db):
    usuario_data = {
        "email": "novo@example.com",
        "senha": "senha123",
        "nome_completo": "Novo Usuário"
    }
    response = test_app.post(f"{settings.API_V1_STR}/auth/register", json=usuario_data)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "novo@example.com"
    assert "id" in data

def test_login(test_app, test_db, test_user):
    login_data = {
        "username": "testuser@example.com",
        "password": "testpassword"
    }
    response = test_app.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(test_app):
    login_data = {
        "username": "invalid@example.com",
        "password": "wrongpassword"
    }
    response = test_app.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
    assert response.status_code == 401