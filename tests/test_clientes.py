#Emprestimo-Facil\tests\test_clientes.py

import pytest
from app.core.config import settings

def test_criar_cliente(test_app, test_db, test_auth_header):
    cliente_data = {
        "nome": "Cliente Teste",
        "email": "cliente@example.com",
        "telefone": "123456789",
        "cpf": "12345678901",
        "data_nascimento": "1990-01-01"
    }
    response = test_app.post(f"{settings.API_V1_STR}/clientes/", json=cliente_data, headers=test_auth_header)
    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == "Cliente Teste"
    assert data["email"] == "cliente@example.com"

def test_listar_clientes(test_app, test_db, test_auth_header):
    response = test_app.get(f"{settings.API_V1_STR}/clientes/", headers=test_auth_header)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_obter_cliente(test_app, test_db, test_auth_header):
    # Primeiro, crie um cliente
    cliente_data = {
        "nome": "Cliente Obter",
        "email": "obter@example.com",
        "telefone": "987654321",
        "cpf": "98765432109",
        "data_nascimento": "1985-05-05"
    }
    create_response = test_app.post(f"{settings.API_V1_STR}/clientes/", json=cliente_data, headers=test_auth_header)
    cliente_id = create_response.json()["id"]
    
    response = test_app.get(f"{settings.API_V1_STR}/clientes/{cliente_id}", headers=test_auth_header)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == cliente_id
    assert data["nome"] == "Cliente Obter"

def test_atualizar_cliente(test_app, test_db, test_auth_header):
    # Primeiro, crie um cliente
    cliente_data = {
        "nome": "Cliente Atualizar",
        "email": "atualizar@example.com",
        "telefone": "123123123",
        "cpf": "11122233344",
        "data_nascimento": "1980-10-10"
    }
    create_response = test_app.post(f"{settings.API_V1_STR}/clientes/", json=cliente_data, headers=test_auth_header)
    cliente_id = create_response.json()["id"]

    # Agora, atualize o cliente
    update_data = {
        "nome": "Cliente Atualizado",
        "telefone": "999999999"
    }
    response = test_app.put(f"{settings.API_V1_STR}/clientes/{cliente_id}", json=update_data, headers=test_auth_header)
    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == "Cliente Atualizado"
    assert data["telefone"] == "999999999"

def test_deletar_cliente(test_app, test_db, test_auth_header):
    # Primeiro, crie um cliente
    cliente_data = {
        "nome": "Cliente Deletar",
        "email": "deletar@example.com",
        "telefone": "777777777",
        "cpf": "55566677788",
        "data_nascimento": "1975-12-25"
    }
    create_response = test_app.post(f"{settings.API_V1_STR}/clientes/", json=cliente_data, headers=test_auth_header)
    cliente_id = create_response.json()["id"]

    # Agora, delete o cliente
    response = test_app.delete(f"{settings.API_V1_STR}/clientes/{cliente_id}", headers=test_auth_header)
    assert response.status_code == 200

    # Verifique se o cliente foi realmente deletado
    get_response = test_app.get(f"{settings.API_V1_STR}/clientes/{cliente_id}", headers=test_auth_header)
    assert get_response.status_code == 404