import pytest
from app.services.garantia_service import GarantiaService
from app.schemas.garantia import GarantiaCreate, GarantiaUpdate, TipoGarantia

@pytest.fixture
def garantia_service(db_session):
    return GarantiaService(db_session)

def test_criar_garantia(garantia_service, emprestimo_fixture):
    garantia_create = GarantiaCreate(
        tipo=TipoGarantia.IMOVEL,
        descricao="Casa na praia",
        valor=500000.00
    )
    garantia = garantia_service.criar_garantia(garantia_create, emprestimo_fixture.id)
    assert garantia.tipo == TipoGarantia.IMOVEL
    assert garantia.descricao == "Casa na praia"
    assert garantia.valor == 500000.00
    assert garantia.emprestimo_id == emprestimo_fixture.id

def test_atualizar_garantia(garantia_service, emprestimo_fixture):
    garantia_create = GarantiaCreate(
        tipo=TipoGarantia.VEICULO,
        descricao="Carro popular",
        valor=30000.00
    )
    garantia = garantia_service.criar_garantia(garantia_create, emprestimo_fixture.id)
    
    garantia_update = GarantiaUpdate(valor=35000.00)
    garantia_atualizada = garantia_service.atualizar_garantia(garantia.id, garantia_update)
    assert garantia_atualizada.valor == 35000.00

def test_remover_garantia(garantia_service, emprestimo_fixture):
    garantia_create = GarantiaCreate(
        tipo=TipoGarantia.FIADOR,
        descricao="Fiador com renda comprovada",
        valor=100000.00
    )
    garantia = garantia_service.criar_garantia(garantia_create, emprestimo_fixture.id)
    
    assert garantia_service.remover_garantia(garantia.id) == True
    assert garantia_service.obter(garantia.id) is None
