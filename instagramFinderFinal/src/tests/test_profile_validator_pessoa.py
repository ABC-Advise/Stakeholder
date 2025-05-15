import pytest
from src.services.profile_validator import ProfileValidator

@pytest.fixture
def validator():
    validator = ProfileValidator()
    yield validator
    validator.close()

def test_validar_perfil_pessoa_nome_completo_match(validator):
    pessoa_info = {"firstname": "João", "lastname": "Silva"}
    perfis = [
        {
            "username": "joaosilva",
            "full_name": "João Silva",
            "bio": "Desenvolvedor de software"
        }
    ]
    resultado = validator.validar_perfil_pessoa(pessoa_info, perfis)
    assert resultado is not None
    assert resultado["perfil"]["username"] == "joaosilva"
    assert resultado["score"] == 100
    assert resultado["detalhes_validacao"]["melhor_variacao_match_leve"] == "joao silva"

def test_validar_perfil_pessoa_nome_composto(validator):
    pessoa_info = {"firstname": "Ana Paula", "lastname": "Oliveira"}
    perfis = [
        {
            "username": "anapaula.oliveira",
            "full_name": "Ana Paula Oliveira",
            "bio": "Médica pediatra"
        }
    ]
    resultado = validator.validar_perfil_pessoa(pessoa_info, perfis)
    assert resultado is not None
    assert resultado["perfil"]["username"] == "anapaula.oliveira"
    assert resultado["score"] == 100
    assert resultado["detalhes_validacao"]["melhor_variacao_match_leve"] == "ana paula oliveira"

def test_validar_perfil_pessoa_sobrenome_composto(validator):
    pessoa_info = {"firstname": "Carlos", "lastname": "Silva Santos"}
    perfis = [
        {
            "username": "carlossilvasantos",
            "full_name": "Carlos Silva Santos",
            "bio": "Professor de matemática"
        }
    ]
    resultado = validator.validar_perfil_pessoa(pessoa_info, perfis)
    assert resultado is not None
    assert resultado["perfil"]["username"] == "carlossilvasantos"
    assert resultado["score"] == 100
    assert resultado["detalhes_validacao"]["melhor_variacao_match_leve"] == "carlos silva santos"

def test_validar_perfil_pessoa_nome_similar(validator):
    pessoa_info = {"firstname": "Roberto", "lastname": "Almeida"}
    perfis = [
        {
            "username": "roberto.almeida",
            "full_name": "Roberto Almeida Silva",
            "bio": "Engenheiro civil"
        }
    ]
    resultado = validator.validar_perfil_pessoa(pessoa_info, perfis)
    assert resultado is None, "Perfil com nome adicional deve ser rejeitado pois o nome original vem do RG"

def test_validar_perfil_pessoa_nome_diferente(validator):
    pessoa_info = {"firstname": "Pedro", "lastname": "Souza"}
    perfis = [
        {
            "username": "outro.nome",
            "full_name": "Outro Nome",
            "bio": "Fotógrafo"
        }
    ]
    resultado = validator.validar_perfil_pessoa(pessoa_info, perfis)
    assert resultado is None

def test_validar_perfil_pessoa_nome_vazio(validator):
    pessoa_info = {"firstname": "", "lastname": "Silva"}
    perfis = [
        {
            "username": "silva",
            "full_name": "Silva",
            "bio": "Artista"
        }
    ]
    resultado = validator.validar_perfil_pessoa(pessoa_info, perfis)
    assert resultado is None

def test_validar_perfil_pessoa_multiplos_perfis(validator):
    pessoa_info = {"firstname": "Lucas", "lastname": "Mendes"}
    perfis = [
        {
            "username": "lucasmendes",
            "full_name": "Lucas Mendes",
            "bio": "Músico"
        },
        {
            "username": "lucas.m",
            "full_name": "L. Mendes",
            "bio": "Produtor musical"
        },
        {
            "username": "outro.nome",
            "full_name": "Outro Nome",
            "bio": "Artista"
        }
    ]
    resultado = validator.validar_perfil_pessoa(pessoa_info, perfis)
    assert resultado is not None
    assert resultado["perfil"]["username"] == "lucasmendes"
    assert resultado["score"] == 100
    assert resultado["detalhes_validacao"]["melhor_variacao_match_leve"] == "lucas mendes"

def test_validar_perfil_pessoa_nome_com_acentos(validator):
    pessoa_info = {"firstname": "José", "lastname": "Márcio"}
    perfis = [
        {
            "username": "josemarcio",
            "full_name": "Jose Marcio",
            "bio": "Professor"
        }
    ]
    resultado = validator.validar_perfil_pessoa(pessoa_info, perfis)
    assert resultado is not None
    assert resultado["perfil"]["username"] == "josemarcio"
    assert resultado["score"] >= 65
    assert resultado["detalhes_validacao"]["melhor_variacao_match_leve"] is not None

def test_validar_perfil_pessoa_nome_com_caracteres_especiais(validator):
    pessoa_info = {"firstname": "Maria", "lastname": "da Silva"}
    perfis = [
        {
            "username": "mariadasilva",
            "full_name": "Maria da Silva",
            "bio": "Arquiteta"
        }
    ]
    resultado = validator.validar_perfil_pessoa(pessoa_info, perfis)
    assert resultado is not None
    assert resultado["perfil"]["username"] == "mariadasilva"
    assert resultado["score"] >= 65
    assert resultado["detalhes_validacao"]["melhor_variacao_match_leve"] is not None 