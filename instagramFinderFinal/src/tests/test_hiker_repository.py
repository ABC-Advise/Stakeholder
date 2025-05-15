import pytest
from unittest.mock import AsyncMock, patch
from src.repositories.hiker_repository import HikerRepository

@pytest.mark.asyncio
@patch('hikerapi.AsyncClient.user_by_username_v1', new_callable=AsyncMock)
async def test_buscar_perfil_por_username_sucesso(mock_user_by_username,):
    mock_user_by_username.return_value = {"username": "exemplo", "full_name": "Exemplo"}
    repo = HikerRepository()
    result = await repo.buscar_perfil_por_username("exemplo")
    assert result["username"] == "exemplo"
    assert result["full_name"] == "Exemplo"

@pytest.mark.asyncio
@patch('hikerapi.AsyncClient.user_by_username_v1', new_callable=AsyncMock)
async def test_buscar_perfil_por_username_erro(mock_user_by_username):
    mock_user_by_username.side_effect = Exception("Perfil não encontrado")
    repo = HikerRepository()
    result = await repo.buscar_perfil_por_username("naoexiste")
    assert "error" in result

@pytest.mark.asyncio
@patch('hikerapi.AsyncClient.user_about_v1', new_callable=AsyncMock)
async def test_get_profile_details_sucesso(mock_user_about):
    mock_user_about.return_value = {"id": "123", "bio": "bio exemplo"}
    repo = HikerRepository()
    result = await repo.get_profile_details("123")
    assert result["id"] == "123"
    assert result["bio"] == "bio exemplo"

@pytest.mark.asyncio
@patch('hikerapi.AsyncClient.user_about_v1', new_callable=AsyncMock)
async def test_get_profile_details_erro(mock_user_about):
    mock_user_about.side_effect = Exception("Erro ao obter detalhes")
    repo = HikerRepository()
    result = await repo.get_profile_details("123")
    assert "error" in result

@pytest.mark.asyncio
@patch('hikerapi.AsyncClient.user_by_id_v1', new_callable=AsyncMock)
async def test_buscar_perfil_por_id_sucesso(mock_user_by_id):
    mock_user_by_id.return_value = {"id": "123", "username": "exemplo"}
    repo = HikerRepository()
    result = await repo.buscar_perfil_por_id("123")
    assert result["id"] == "123"
    assert result["username"] == "exemplo"

@pytest.mark.asyncio
@patch('hikerapi.AsyncClient.user_by_url_v1', new_callable=AsyncMock)
async def test_buscar_perfil_por_url_sucesso(mock_user_by_url):
    mock_user_by_url.return_value = {"username": "exemplo", "url": "https://instagram.com/exemplo"}
    repo = HikerRepository()
    result = await repo.buscar_perfil_por_url("https://instagram.com/exemplo")
    assert result["username"] == "exemplo"
    assert "url" in result

@pytest.mark.asyncio
@patch('hikerapi.AsyncClient.search_accounts_v2', new_callable=AsyncMock)
async def test_buscar_perfis_por_nome_sucesso(mock_search_accounts):
    mock_search_accounts.return_value = {"accounts": [{"username": "exemplo1"}, {"username": "exemplo2"}]}
    repo = HikerRepository()
    result = await repo.buscar_perfis_por_nome("exemplo")
    assert "accounts" in result
    assert len(result["accounts"]) > 1

@pytest.mark.asyncio
@patch('hikerapi.AsyncClient.user_web_profile_info_v1', new_callable=AsyncMock)
async def test_buscar_web_profile_info_sucesso(mock_web_profile_info):
    mock_web_profile_info.return_value = {"username": "exemplo", "bio": "bio exemplo"}
    repo = HikerRepository()
    result = await repo.buscar_web_profile_info("exemplo")
    assert result["username"] == "exemplo"
    assert "bio" in result 