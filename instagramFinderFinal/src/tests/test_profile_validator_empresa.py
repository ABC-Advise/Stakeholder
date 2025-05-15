import pytest
from unittest.mock import MagicMock
from src.services.profile_validator import ProfileValidator

@pytest.fixture
def validator():
    validator_instance = ProfileValidator()
    yield validator_instance
    validator_instance.close()

def test_validar_nome_empresa_exato(validator):
    nome_fantasia = "Constrowins Engenharia"
    nome_perfil = "CONSTROWINS ENGENHARIA"
    score = validator.validar_nome_empresa(nome_fantasia, nome_perfil)
    assert score == 1.0

def test_validar_nome_empresa_similar(validator):
    nome_fantasia = "Constrowins Engenharia"
    nome_perfil = "Constrowins"
    score = validator.validar_nome_empresa(nome_fantasia, nome_perfil)
    assert score == 0.8

def test_validar_nome_empresa_diferente(validator):
    nome_fantasia = "Constrowins Engenharia"
    nome_perfil = "Outra Empresa"
    score = validator.validar_nome_empresa(nome_fantasia, nome_perfil)
    assert score == 0.0

def test_validar_nome_empresa_completamente_diferente(validator):
    nome_fantasia = "Constrowins"
    nome_perfil = "XPTO Aleatorio Total"
    score = validator.validar_nome_empresa(nome_fantasia, nome_perfil)
    assert score == 0.0

def mock_db_execute(descricao_segmento: str | None):
    mock_result = MagicMock()
    if descricao_segmento is None:
        mock_result.fetchone.return_value = None
    else:
        mock_record = MagicMock()
        mock_record._mapping = {"descricao": descricao_segmento}
        mock_result.fetchone.return_value = mock_record
    
    mock_session_execute = MagicMock()
    mock_session_execute.return_value = mock_result
    return mock_session_execute

def test_validar_segmento_encontrado(validator: ProfileValidator):
    validator.session.execute = mock_db_execute("Construção de Edifícios Residenciais")
    bio = "Especialistas em construção de edifícios residenciais e comerciais."
    assert validator.validar_segmento(segmento_id=1, bio=bio) is True
    validator.session.execute.assert_called_once()

def test_validar_segmento_nao_encontrado(validator: ProfileValidator):
    validator.session.execute = mock_db_execute("Comércio de peças automotivas")
    bio = "Empresa de desenvolvimento de software e tecnologia."
    assert validator.validar_segmento(segmento_id=2, bio=bio) is False
    validator.session.execute.assert_called_once()

def test_validar_segmento_descricao_vazia_no_banco(validator: ProfileValidator):
    validator.session.execute = mock_db_execute("") 
    bio = "Qualquer bio aqui."
    assert validator.validar_segmento(segmento_id=3, bio=bio) is False
    validator.session.execute.assert_called_once()

def test_validar_segmento_descricao_none_no_banco(validator: ProfileValidator):
    validator.session.execute = mock_db_execute(None) 
    bio = "Qualquer bio aqui."
    assert validator.validar_segmento(segmento_id=4, bio=bio) is False
    validator.session.execute.assert_called_once()
    
def test_validar_segmento_bio_vazia(validator: ProfileValidator):
    validator.session.execute = mock_db_execute("Consultoria Empresarial")
    bio = ""
    assert validator.validar_segmento(segmento_id=5, bio=bio) is False
    validator.session.execute.assert_called_once()

def test_validar_segmento_descricao_e_stopword_mas_encontrado_fallback(validator: ProfileValidator):
    validator.session.execute = mock_db_execute("e") 
    bio = "Teste e mais testes" 
    assert validator.validar_segmento(segmento_id=6, bio=bio) is True
    validator.session.execute.assert_called_once()

def test_validar_segmento_descricao_longa_com_stopwords_encontrada(validator: ProfileValidator):
    validator.session.execute = mock_db_execute("Fabricação de outros produtos alimentícios não especificados anteriormente")
    bio = "Somos uma empresa de fabricação de outros produtos alimentícios não especificados anteriormente, com qualidade."
    assert validator.validar_segmento(segmento_id=7, bio=bio) is True
    validator.session.execute.assert_called_once()

def test_validar_segmento_descricao_com_numeros(validator: ProfileValidator):
    validator.session.execute = mock_db_execute("Certificação ISO 9001 em Gestão da Qualidade")
    bio = "Empresa com ISO 9001 Gestão e foco no cliente." 
    assert validator.validar_segmento(segmento_id=8, bio=bio) is True
    validator.session.execute.assert_called_once()  

def test_validar_perfil_empresa_completo(validator):
    empresa = {
        "nome_fantasia": "Constrowins Engenharia",
        "segmento_id": 26 
    }
    perfis = [
        {
            "username": "constrowins",
            "full_name": "CONSTROWINS ENGENHARIA",
            "bio": "Há mais de 15 anos presente em grandes obras. Empresa certificada.", 
            "is_business": True
        },
        {
            "username": "outra_empresa",
            "full_name": "Outra Empresa",
            "bio": "Empresa de tecnologia",
            "is_business": False
        }
    ]
    
    original_validar_segmento = validator.validar_segmento
    
    def mock_segmento_para_completo(seg_id, bio_text):
        if seg_id == 26 and "obras" in validator.normalizar(bio_text): 
             return True
        return False 

    validator.validar_segmento = lambda segmento_id_param, bio_param: True if segmento_id_param == 26 else False

    resultado = validator.validar_perfil_empresa(empresa, perfis)
    validator.validar_segmento = original_validar_segmento # Restore

    assert resultado is not None
    assert resultado["perfil"]["username"] == "constrowins"
    assert resultado["score"] == 103

def test_validar_perfil_empresa_sem_match(validator):
    empresa = {
        "nome_fantasia": "Constrowins Engenharia",
        "segmento_id": 26
    }
    perfis = [
        {
            "username": "outra_empresa",
            "full_name": "Outra Empresa", 
            "bio": "Empresa de tecnologia",
            "is_business": False
        }
    ]
    resultado = validator.validar_perfil_empresa(empresa, perfis)
    assert resultado is None

@pytest.mark.asyncio
async def test_validar_perfil_empresa():
    validator = ProfileValidator()
    
    # Dados de teste
    empresa = {
        "nome_fantasia": "Empresa Teste",
        "segmento_id": 1
    }
    
    perfis_instagram = [
        {
            "username": "empresateste",
            "full_name": "Empresa Teste",
            "bio": "Empresa de tecnologia",
            "is_private": False,
            "is_business": True
        },
        {
            "username": "outro_usuario",
            "full_name": "Outro Nome",
            "bio": "Outra bio",
            "is_private": False,
            "is_business": False
        }
    ]
    
    # Testa a validação
    perfil_valido, todos_perfis = await validator.validar_perfil_empresa(empresa, perfis_instagram)
    
    # Verifica se o perfil correto foi selecionado
    assert perfil_valido is not None
    assert perfil_valido["perfil"]["username"] == "empresateste"
    assert perfil_valido["score"] > 0
    
    # Verifica se todos os perfis foram processados
    assert len(todos_perfis) == 2

@pytest.mark.asyncio
async def test_validar_perfil_empresa_privado():
    validator = ProfileValidator()
    
    # Dados de teste
    empresa = {
        "nome_fantasia": "Empresa Teste",
        "segmento_id": 1
    }
    
    perfis_instagram = [
        {
            "username": "empresateste",
            "full_name": "Empresa Teste",
            "bio": "Empresa de tecnologia",
            "is_private": True,
            "is_business": True
        }
    ]
    
    # Testa a validação
    perfil_valido, todos_perfis = await validator.validar_perfil_empresa(empresa, perfis_instagram)
    
    # Verifica se o perfil privado foi descartado
    assert perfil_valido is None
    assert len(todos_perfis) == 1
    assert todos_perfis[0]["score"] == 0

