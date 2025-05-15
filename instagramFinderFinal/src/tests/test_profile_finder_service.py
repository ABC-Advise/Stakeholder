import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.services.profile_finder_service import ProfileFinderService
from src.repositories.hiker_repository import HikerRepository
from src.repositories.postgres_repository import PostgresRepository
from src.services.profile_validator import ProfileValidator

@pytest.fixture
def mock_hiker_repository():
    mock = Mock(spec=HikerRepository)
    mock.buscar_perfis_por_nome = AsyncMock()
    mock.buscar_seguidores = AsyncMock()
    return mock

@pytest.fixture
def mock_postgres_repository():
    mock = Mock(spec=PostgresRepository)
    mock.get_entity = AsyncMock()
    mock.get_entities_without_instagram = AsyncMock()
    mock.get_related_entities = AsyncMock()
    return mock

@pytest.fixture
def mock_profile_validator():
    mock = Mock(spec=ProfileValidator)
    mock.validar_perfil_empresa = Mock()
    mock.validar_perfil_pessoa = Mock()
    mock.validar_perfil_advogado = Mock()
    return mock

@pytest.fixture
def profile_finder_service(mock_hiker_repository, mock_postgres_repository, mock_profile_validator):
    service = ProfileFinderService(mock_hiker_repository, mock_postgres_repository)
    service.validator = mock_profile_validator
    return service

@pytest.mark.asyncio
async def test_find_profiles_for_entity_empresa(profile_finder_service, mock_postgres_repository, mock_hiker_repository, mock_profile_validator):
    # Arrange
    entity_type = "empresa"
    entity_id = 1
    empresa = {
        "id": 1,
        "nome_fantasia": "Constrowins Engenharia",
        "segmento_id": 26
    }
    candidates = [
        {
            "username": "constrowins",
            "full_name": "CONSTROWINS ENGENHARIA",
            "bio": "Há mais de 15 anos presente em grandes obras. Empresa certificada.",
            "is_business": True
        }
    ]
    validated_profile = {
        "perfil": candidates[0],
        "score": 103,
        "is_business_profile": True,
        "empresa": empresa,
        "detalhes_validacao": {
            "nome_pontos": 80,
            "bio_pontos": 10,
            "username_pontos": 8,
            "is_business_bonus": 5,
            "segmento_encontrado": True
        }
    }

    mock_postgres_repository.get_entity.return_value = empresa
    mock_hiker_repository.buscar_perfis_por_nome.return_value = {"users": candidates}
    mock_profile_validator.validar_perfil_empresa.return_value = validated_profile

    # Act
    result = await profile_finder_service.find_profiles_for_entity(entity_type, entity_id)

    # Assert
    assert result["entity"] == empresa
    assert result["candidates"] == candidates
    assert result["validated_profile"] == validated_profile
    mock_postgres_repository.get_entity.assert_called_once_with(entity_type, entity_id)
    mock_hiker_repository.buscar_perfis_por_nome.assert_called_once()
    mock_profile_validator.validar_perfil_empresa.assert_called_once_with(empresa, candidates)

@pytest.mark.asyncio
async def test_find_profiles_for_entity_pessoa(profile_finder_service, mock_postgres_repository, mock_hiker_repository, mock_profile_validator):
    # Arrange
    entity_type = "pessoa"
    entity_id = 1
    pessoa = {
        "id": 1,
        "firstname": "João",
        "lastname": "Silva",
        "empresa_id": 1
    }
    empresa = {
        "id": 1,
        "nome_fantasia": "Empresa Teste",
        "instagram_username": "empresateste"
    }
    candidates = [
        {
            "username": "joaosilva",
            "full_name": "João Silva",
            "bio": "Desenvolvedor de software"
        }
    ]
    validated_profile = {
        "perfil": candidates[0],
        "score": 85,
        "is_business_profile": False,
        "pessoa": pessoa
    }

    mock_postgres_repository.get_entity.side_effect = lambda t, i: pessoa if t == "pessoa" else empresa
    mock_hiker_repository.buscar_perfis_por_nome.return_value = {"users": candidates}
    mock_hiker_repository.buscar_seguidores.return_value = {"users": candidates}
    mock_profile_validator.validar_perfil_pessoa.return_value = validated_profile

    # Act
    result = await profile_finder_service.find_profiles_for_entity(entity_type, entity_id)

    # Assert
    assert result["entity"] == pessoa
    assert result["candidates"] == candidates
    assert result["validated_profile"] == validated_profile
    assert mock_postgres_repository.get_entity.call_count == 2
    mock_postgres_repository.get_entity.assert_any_call(entity_type, entity_id)
    mock_postgres_repository.get_entity.assert_any_call("empresa", pessoa["empresa_id"])
    mock_hiker_repository.buscar_perfis_por_nome.assert_called_once()
    mock_hiker_repository.buscar_seguidores.assert_called_once_with(empresa["instagram_username"])
    mock_profile_validator.validar_perfil_pessoa.assert_called_once_with(pessoa, candidates)

@pytest.mark.asyncio
async def test_find_profiles_for_entity_advogado(profile_finder_service, mock_postgres_repository, mock_hiker_repository, mock_profile_validator):
    # Arrange
    entity_type = "advogado"
    entity_id = 1
    advogado = {
        "id": 1,
        "firstname": "Maria",
        "lastname": "Santos",
        "empresa_id": 1
    }
    empresa = {
        "id": 1,
        "nome_fantasia": "Escritório de Advocacia",
        "instagram_username": "escritorioadv"
    }
    candidates = [
        {
            "username": "mariasantos.adv",
            "full_name": "Maria Santos",
            "bio": "Advogada ⚖️ OAB 12345"
        }
    ]
    validated_profile = {
        "perfil": candidates[0],
        "score": 90,
        "is_business_profile": False,
        "advogado": advogado
    }

    mock_postgres_repository.get_entity.side_effect = lambda t, i: advogado if t == "advogado" else empresa
    mock_hiker_repository.buscar_perfis_por_nome.return_value = {"users": candidates}
    mock_hiker_repository.buscar_seguidores.return_value = {"users": candidates}
    mock_profile_validator.validar_perfil_advogado.return_value = validated_profile

    # Act
    result = await profile_finder_service.find_profiles_for_entity(entity_type, entity_id)

    # Assert
    assert result["entity"] == advogado
    assert result["candidates"] == candidates
    assert result["validated_profile"] == validated_profile
    assert mock_postgres_repository.get_entity.call_count == 2
    mock_postgres_repository.get_entity.assert_any_call(entity_type, entity_id)
    mock_postgres_repository.get_entity.assert_any_call("empresa", advogado["empresa_id"])
    mock_hiker_repository.buscar_perfis_por_nome.assert_called_once()
    mock_hiker_repository.buscar_seguidores.assert_called_once_with(empresa["instagram_username"])
    mock_profile_validator.validar_perfil_advogado.assert_called_once_with(advogado, candidates)

@pytest.mark.asyncio
async def test_find_profiles_for_entity_not_found(profile_finder_service, mock_postgres_repository):
    # Arrange
    entity_type = "empresa"
    entity_id = 999
    mock_postgres_repository.get_entity.return_value = None

    # Act & Assert
    with pytest.raises(ValueError, match=f"Entidade {entity_type} com ID {entity_id} não encontrada"):
        await profile_finder_service.find_profiles_for_entity(entity_type, entity_id)

@pytest.mark.asyncio
async def test_find_profiles_for_entity_invalid_type(profile_finder_service, mock_postgres_repository):
    # Arrange
    entity_type = "invalid_type"
    entity_id = 1
    entity = {"id": 1, "nome": "Teste"}
    mock_postgres_repository.get_entity.return_value = entity

    # Act
    result = await profile_finder_service.find_profiles_for_entity(entity_type, entity_id)

    # Assert
    assert result["entity"] == entity
    assert result["candidates"] == []
    assert result["validated_profile"] is None

@pytest.mark.asyncio
async def test_find_profiles_for_all_entities(profile_finder_service, mock_postgres_repository, mock_hiker_repository, mock_profile_validator):
    # Arrange
    entity_type = "empresa"
    entities = [
        {"id": 1, "nome_fantasia": "Empresa 1"},
        {"id": 2, "nome_fantasia": "Empresa 2"}
    ]
    candidates = [
        {
            "username": "empresa1",
            "full_name": "Empresa 1",
            "bio": "Empresa de tecnologia",
            "is_business": True
        }
    ]
    validated_profile = {
        "perfil": candidates[0],
        "score": 90,
        "is_business_profile": True,
        "empresa": entities[0]
    }

    mock_postgres_repository.get_entities_without_instagram.return_value = entities
    mock_postgres_repository.get_entity.side_effect = lambda t, i: entities[i-1]
    mock_hiker_repository.buscar_perfis_por_nome.return_value = {"users": candidates}
    mock_profile_validator.validar_perfil_empresa.return_value = validated_profile

    # Act
    results = await profile_finder_service.find_profiles_for_all_entities(entity_type)

    # Assert
    assert len(results) == 2
    assert all("entity" in result for result in results)
    assert all("candidates" in result for result in results)
    assert all("validated_profile" in result for result in results)
    mock_postgres_repository.get_entities_without_instagram.assert_called_once_with(entity_type)
    assert mock_postgres_repository.get_entity.call_count == 2
    assert mock_hiker_repository.buscar_perfis_por_nome.call_count == 2
    assert mock_profile_validator.validar_perfil_empresa.call_count == 2

@pytest.mark.asyncio
async def test_find_profiles_for_company_and_related(profile_finder_service, mock_postgres_repository, mock_hiker_repository, mock_profile_validator):
    # Arrange
    company_id = 1
    company = {
        "id": 1,
        "nome_fantasia": "Empresa Principal",
        "segmento_id": 26
    }
    related_entities = [
        {"id": 1, "type": "pessoa", "firstname": "João", "lastname": "Silva"},
        {"id": 2, "type": "advogado", "firstname": "Maria", "lastname": "Santos"}
    ]
    candidates = [
        {
            "username": "empresaprincipal",
            "full_name": "Empresa Principal",
            "bio": "Empresa líder no mercado",
            "is_business": True
        }
    ]
    validated_profile = {
        "perfil": candidates[0],
        "score": 95,
        "is_business_profile": True,
        "empresa": company
    }

    async def mock_get_entity(entity_type: str, entity_id: int):
        if entity_type == "empresa" and entity_id == company_id:
            return company
        elif entity_type == "pessoa" and entity_id == related_entities[0]["id"]:
            return related_entities[0]
        elif entity_type == "advogado" and entity_id == related_entities[1]["id"]:
            return related_entities[1]
        return None

    mock_postgres_repository.get_entity.side_effect = mock_get_entity
    mock_postgres_repository.get_related_entities.return_value = related_entities
    mock_hiker_repository.buscar_perfis_por_nome.return_value = {"users": candidates}
    mock_profile_validator.validar_perfil_empresa.return_value = validated_profile
    mock_profile_validator.validar_perfil_pessoa.return_value = {
        "perfil": candidates[0],
        "score": 85,
        "is_business_profile": False,
        "pessoa": related_entities[0]
    }
    mock_profile_validator.validar_perfil_advogado.return_value = {
        "perfil": candidates[0],
        "score": 80,
        "is_business_profile": False,
        "advogado": related_entities[1]
    }

    # Act
    result = await profile_finder_service.find_profiles_for_company_and_related(company_id)

    # Assert
    assert "company" in result
    assert "related_entities" in result
    assert len(result["related_entities"]) == 2
    assert all("entity" in r for r in result["related_entities"])
    assert all("candidates" in r for r in result["related_entities"])
    assert all("validated_profile" in r for r in result["related_entities"]) 
    mock_postgres_repository.get_entity.assert_called()
    mock_postgres_repository.get_related_entities.assert_called_once_with(company_id)
    assert mock_hiker_repository.buscar_perfis_por_nome.call_count == 3
    assert mock_profile_validator.validar_perfil_empresa.call_count >= 1
    assert mock_profile_validator.validar_perfil_pessoa.call_count >= 1
    assert mock_profile_validator.validar_perfil_advogado.call_count >= 1

@pytest.mark.asyncio
async def test_find_profiles_for_company_and_related_with_errors(profile_finder_service, mock_postgres_repository, mock_hiker_repository, mock_profile_validator):
    # Arrange
    company_id = 1
    company = {
        "id": 1,
        "nome_fantasia": "Empresa Principal",
        "segmento_id": 26
    }
    related_entities = [
        {"id": 1, "type": "pessoa", "firstname": "João", "lastname": "Silva"},
        {"id": 2, "type": "advogado", "firstname": "Maria", "lastname": "Santos"},
        {"id": 3, "type": "invalid_type", "nome": "Entidade Inválida"}
    ]
    candidates = [
        {
            "username": "empresaprincipal",
            "full_name": "Empresa Principal",
            "bio": "Empresa líder no mercado",
            "is_business": True
        }
    ]
    validated_profile = {
        "perfil": candidates[0],
        "score": 95,
        "is_business_profile": True,
        "empresa": company
    }

    async def mock_get_entity_with_errors(entity_type: str, entity_id: int):
        if entity_type == "empresa" and entity_id == company_id:
            return company
        elif entity_type == "pessoa" and entity_id == related_entities[0]["id"]:
            raise ValueError(f"Entidade {entity_type} com ID {entity_id} não encontrada")
        elif entity_type == "advogado" and entity_id == related_entities[1]["id"]:
            return related_entities[1]
        elif entity_type == "invalid_type" and entity_id == related_entities[2]["id"]:
            raise ValueError(f"Entidade {entity_type} com ID {entity_id} não encontrada")
        return None

    mock_postgres_repository.get_entity.side_effect = mock_get_entity_with_errors
    mock_postgres_repository.get_related_entities.return_value = related_entities
    mock_hiker_repository.buscar_perfis_por_nome.return_value = {"users": candidates}
    mock_profile_validator.validar_perfil_empresa.return_value = validated_profile
    mock_profile_validator.validar_perfil_advogado.return_value = {
        "perfil": candidates[0],
        "score": 80,
        "is_business_profile": False,
        "advogado": related_entities[1]
    }

    # Act
    result = await profile_finder_service.find_profiles_for_company_and_related(company_id)

    # Assert
    assert "company" in result
    assert "related_entities" in result
    assert len(result["related_entities"]) == 3
    
    # Verificar resultado da empresa
    assert result["company"]["entity"] == company
    assert result["company"]["candidates"] == candidates
    assert result["company"]["validated_profile"] == validated_profile
    
    # Verificar resultados das entidades relacionadas
    pessoa_result = result["related_entities"][0]
    assert pessoa_result["entity"] == related_entities[0]
    assert "error" in pessoa_result
    assert f"Entidade pessoa com ID {related_entities[0]['id']} não encontrada" in pessoa_result["error"]
    
    advogado_result = result["related_entities"][1]
    assert advogado_result["entity"] == related_entities[1]
    assert "error" not in advogado_result
    assert "candidates" in advogado_result
    assert "validated_profile" in advogado_result
    assert advogado_result["candidates"] == candidates
    assert advogado_result["validated_profile"]["score"] == 80

    invalid_result = result["related_entities"][2]
    assert invalid_result["entity"] == related_entities[2]
    assert "error" in invalid_result
    assert f"Entidade invalid_type com ID {related_entities[2]['id']} não encontrada" in invalid_result["error"]

    mock_postgres_repository.get_entity.assert_called()
    mock_postgres_repository.get_related_entities.assert_called_once_with(company_id)
    assert mock_hiker_repository.buscar_perfis_por_nome.call_count == 2
    assert mock_profile_validator.validar_perfil_empresa.call_count >= 1
    mock_profile_validator.validar_perfil_pessoa.assert_not_called()
    assert mock_profile_validator.validar_perfil_advogado.call_count >= 1 