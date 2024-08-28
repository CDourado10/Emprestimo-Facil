#Emprestimo-Facil\tests\test_emprestimos.py

import pytest
from app.core.config import settings
from app.schemas.emprestimo import StatusEmprestimo

def test_criar_emprestimo(test_app, test_db, test_auth_header):
    # Primeiro, crie um cliente
    cliente_data = {
        "nome": "Cliente Empréstimo",
        "email": "emprestimo@example.com",
        "telefone": "555555555",
        "cpf": "12312312312",
        "data_nascimento": "1988-08-08"
    }
    cliente_response = test_app.post(f"{settings.API_V1_STR}/clientes/", json=cliente_data, headers=test_auth_header)
    cliente_id = cliente_response.json()["id"]

    emprestimo_data = {
        "cliente_id": cliente_id,
        "valor": 1000.00,
        "taxa_juros": 0.05,
        "data_solicitacao": "2023-05-01",
        "data_vencimento": "2023-06-01",
        "status": StatusEmprestimo.PENDENTE.value
    }
    response = test_app.post(f"{settings.API_V1_STR}/emprestimos/", json=emprestimo_data, headers=test_auth_header)
    assert response.status_code == 200
    data = response.json()
    assert data["valor"] == 1000.00
    assert data["status"] == StatusEmprestimo.PENDENTE.value

def test_listar_emprestimos(test_app, test_db, test_auth_header):
    response = test_app.get(f"{settings.API_V1_STR}/emprestimos/", headers=test_auth_header)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_obter_emprestimo(test_app, test_db, test_auth_header):
    # Primeiro, crie um cliente
    cliente_data = {
        "nome": "Cliente Empréstimo Obter",
        "email": "emprestimo.obter@example.com",
        "telefone": "444444444",
        "cpf": "98798798798",
        "data_nascimento": "1992-02-02"
    }
    cliente_response = test_app.post(f"{settings.API_V1_STR}/clientes/", json=cliente_data, headers=test_auth_header)
    cliente_id = cliente_response.json()["id"]

    # Agora, crie um empréstimo
    emprestimo_data = {
        "cliente_id": cliente_id,
        "valor": 2000.00,
        "taxa_juros": 0.1,
        "data_solicitacao": "2023-05-01",
        "data_vencimento": "2023-07-01",
        "status": StatusEmprestimo.ATIVO.value
    }
    create_response = test_app.post(f"{settings.API_V1_STR}/emprestimos/", json=emprestimo_data, headers=test_auth_header)
    emprestimo_id = create_response.json()["id"]
    
    response = test_app.get(f"{settings.API_V1_STR}/emprestimos/{emprestimo_id}", headers=test_auth_header)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == emprestimo_id
    assert data["valor"] == 2000.00

def test_atualizar_emprestimo(test_app, test_db, test_auth_header):
    # Primeiro, crie um cliente e um empréstimo
    cliente_data = {
        "nome": "Cliente Empréstimo Atualizar",
        "email": "emprestimo.atualizar@example.com",
        "telefone": "333333333",
        "cpf": "45645645645",
        "data_nascimento": "1995-05-05"
    }
    cliente_response = test_app.post(f"{settings.API_V1_STR}/clientes/", json=cliente_data, headers=test_auth_header)
    cliente_id = cliente_response.json()["id"]

    emprestimo_data = {
        "cliente_id": cliente_id,
        "valor": 3000.00,
        "taxa_juros": 0.15,
        "data_solicitacao": "2023-06-01",
        "data_vencimento": "2023-08-01",
        "status": StatusEmprestimo.PENDENTE.value
    }
    create_response = test_app.post(f"{settings.API_V1_STR}/emprestimos/", json=emprestimo_data, headers=test_auth_header)
    emprestimo_id = create_response.json()["id"]

    # Agora, atualize o empréstimo
    update_data = {
        "status": StatusEmprestimo.ATIVO.value,
        "valor": 3500.00
    }
    response = test_app.put(f"{settings.API_V1_STR}/emprestimos/{emprestimo_id}", json=update_data, headers=test_auth_header)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == StatusEmprestimo.ATIVO.value
    assert data["valor"] == 3500.00

# Adicione mais testes conforme necessário