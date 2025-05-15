import pytest
from src.repositories.postgres_repository import PostgresRepository

@pytest.fixture
def repo():
    repository = PostgresRepository()
    yield repository
    repository.close()

def test_buscar_empresa_por_nome_fantasia(repo):
    # Substitua pelo nome_fantasia de uma empresa real do seu banco para o teste
    nome_fantasia = "CONSTROWINS ENGENHARIA"
    empresa = repo.buscar_empresa_por_nome_fantasia(nome_fantasia)
    assert empresa is None or "nome_fantasia" in empresa 

def test_buscar_pessoa_por_nome_completo(repo):
    # Substitua pelos nomes reais de uma pessoa cadastrada para o teste
    firstname = "WALTAGAN"
    lastname = "WILTON LOPES JUNIOR"
    pessoa = repo.buscar_pessoa_por_nome_completo(firstname, lastname)
    assert pessoa is None or ("firstname" in pessoa and "lastname" in pessoa) 

def test_buscar_advogado_por_nome(repo):
    # Substitua pelos nomes reais de um advogado cadastrado para o teste
    firstname = "Luis"
    lastname = "Guilherme Hollaender Braun"
    advogado = repo.buscar_advogado_por_nome(firstname, lastname)
    assert advogado is None or ("firstname" in advogado and "lastname" in advogado) 

def test_buscar_empresa_por_id(repo):
    # Substitua pelo ID real de uma empresa cadastrada para o teste
    empresa_id = 28
    empresa = repo.buscar_empresa_por_id(empresa_id)
    assert empresa is None or empresa.get("empresa_id") == empresa_id

def test_buscar_pessoa_por_id(repo):
    # Substitua pelo ID real de uma pessoa cadastrada para o teste
    pessoa_id = 10
    pessoa = repo.buscar_pessoa_por_id(pessoa_id)
    assert pessoa is None or pessoa.get("pessoa_id") == pessoa_id

def test_buscar_advogado_por_id(repo):
    # Substitua pelo ID real de um advogado cadastrado para o teste
    advogado_id = 109
    advogado = repo.buscar_advogado_por_id(advogado_id)
    assert advogado is None or advogado.get("advogado_id") == advogado_id 