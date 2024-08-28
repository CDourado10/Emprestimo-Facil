#Emprestimo-Facil\tests\test_emprestimo_service.py

import pytest
from datetime import date, timedelta
from decimal import Decimal
from app.services.emprestimo_service import EmprestimoService
from app.models.emprestimo import Emprestimo, StatusEmprestimo
from app.schemas.emprestimo import EmprestimoCreate, PagamentoCreate, EmprestimoUpdate

@pytest.fixture
def emprestimo_service(db_session):
    return EmprestimoService(db_session)

@pytest.fixture
def cliente_fixture(db_session):
    # Criar um cliente de teste no banco de dados
    from app.schemas.cliente import ClienteCreate
    from app.services.cliente_service import ClienteService

    cliente_service = ClienteService(db_session)
    cliente_create = ClienteCreate(
        nome="João da Silva",
        cpf="123.456.789-00",
        email="joao@example.com",
        telefone="(11) 98765-4321",
        endereco="Rua das Flores, 123",
        data_nascimento=date(1990, 1, 1)
    )
    cliente = cliente_service.criar_cliente(cliente_create)
    return cliente
    ...

@pytest.fixture
def emprestimo_fixture(db_session, cliente_fixture):
    emprestimo_service = EmprestimoService(db_session)
    emprestimo_create = EmprestimoCreate(**criar_dados_emprestimo(cliente_fixture.id))
    emprestimo = emprestimo_service.criar_emprestimo(emprestimo_create)
    db_session.commit()
    return emprestimo

def criar_dados_emprestimo(cliente_id):
    return {
        "cliente_id": cliente_id,
        "valor": Decimal("1000.00"),
        "taxa_juros": Decimal("10"),
        "data_vencimento": date.today() + timedelta(days=30),
        "regras_pagamento": [{"tipo": "fixo", "dia": 10}]
    }

def test_criar_emprestimo(emprestimo_service, cliente_fixture):
    emprestimo_create = EmprestimoCreate(**criar_dados_emprestimo(cliente_fixture.id))
    emprestimo = emprestimo_service.criar_emprestimo(emprestimo_create)
    assert emprestimo.cliente_id == cliente_fixture.id
    assert emprestimo.valor == Decimal("1000.00")
    assert emprestimo.status == StatusEmprestimo.PENDENTE

def test_obter_emprestimo(emprestimo_service, emprestimo_fixture):
    emprestimo = emprestimo_service.obter_emprestimo(emprestimo_fixture.id)
    assert emprestimo.id == emprestimo_fixture.id
    assert emprestimo.cliente_id == emprestimo_fixture.cliente_id

def test_listar_emprestimos(emprestimo_service, emprestimo_fixture):
    emprestimos = emprestimo_service.listar_emprestimos()
    assert len(emprestimos) > 0
    assert any(e.id == emprestimo_fixture.id for e in emprestimos)

def test_atualizar_emprestimo(emprestimo_service, emprestimo_fixture):
    update_data = EmprestimoUpdate(valor=Decimal("1200.00"))
    emprestimo_atualizado = emprestimo_service.atualizar_emprestimo(emprestimo_fixture.id, update_data)
    assert emprestimo_atualizado.valor == Decimal("1200.00")

def test_deletar_emprestimo(emprestimo_service, emprestimo_fixture):
    emprestimo_deletado = emprestimo_service.deletar_emprestimo(emprestimo_fixture.id)
    assert emprestimo_deletado.status == StatusEmprestimo.CANCELADO

def test_registrar_pagamento(emprestimo_service, emprestimo_fixture):
    pagamento = PagamentoCreate(valor=Decimal("500.00"))
    emprestimo_atualizado = emprestimo_service.registrar_pagamento(emprestimo_fixture.id, pagamento)
    assert emprestimo_atualizado.valor == emprestimo_fixture.valor - Decimal("500.00")

def test_calcular_valor_total_devido(emprestimo_service, emprestimo_fixture):
    valor_devido = emprestimo_service.calcular_valor_total_devido(emprestimo_fixture)
    assert valor_devido > emprestimo_fixture.valor

def test_verificar_atrasos(emprestimo_service, emprestimo_fixture):
    # Modificar a data de vencimento do empréstimo para simular um atraso
    emprestimo_fixture.proximo_vencimento = date.today() - timedelta(days=1)
    emprestimo_service.db.commit()

    emprestimos_atrasados = emprestimo_service.verificar_atrasos()
    assert any(e.id == emprestimo_fixture.id for e in emprestimos_atrasados)
    assert emprestimo_fixture.status == StatusEmprestimo.ATRASADO

def test_gerar_relatorio_emprestimos(emprestimo_service, emprestimo_fixture):
    data_inicio = date.today() - timedelta(days=30)
    data_fim = date.today()
    relatorio = emprestimo_service.gerar_relatorio_emprestimos(data_inicio, data_fim)
    assert "total_emprestado" in relatorio
    assert "total_a_receber" in relatorio
    assert "emprestimos_ativos" in relatorio
    assert "emprestimos_atrasados" in relatorio
    assert "detalhes" in relatorio