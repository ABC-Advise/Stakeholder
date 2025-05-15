import pytest
from unittest.mock import Mock, patch
from ..services.profile_service import ProfileService
from ..repositories.hiker_repository import HikerRepository
from ..repositories.postgres_repository import PostgresRepository

@pytest.fixture
def mock_hiker_repository():
    return Mock(spec=HikerRepository)

@pytest.fixture
def mock_postgres_repository():
    return Mock(spec=PostgresRepository)

@pytest.fixture
def profile_service(mock_hiker_repository, mock_postgres_repository):
    return ProfileService(mock_hiker_repository, mock_postgres_repository)

@pytest.mark.asyncio
async def test_search_and_save_profile_existing(profile_service, mock_postgres_repository):
    # Arrange
    username = "test_user"
    existing_profile = {
        "id": 1,
        "username": username,
        "full_name": "Test User",
        "followers_count": 1000,
        "following_count": 500,
        "bio": "Test bio"
    }
    mock_postgres_repository.get_profile.return_value = existing_profile

    # Act
    result = await profile_service.search_and_save_profile(username)

    # Assert
    assert result == existing_profile
    mock_postgres_repository.get_profile.assert_called_once_with(username)
    mock_postgres_repository.save_profile.assert_not_called()

@pytest.mark.asyncio
async def test_search_and_save_profile_new(profile_service, mock_hiker_repository, mock_postgres_repository):
    # Arrange
    username = "new_user"
    hiker_profile = {
        "username": username,
        "full_name": "New User",
        "followers_count": 2000,
        "following_count": 1000,
        "bio": "New bio"
    }
    saved_profile = {**hiker_profile, "id": 1}

    mock_postgres_repository.get_profile.return_value = None
    mock_hiker_repository.buscar_perfil_por_username.return_value = hiker_profile
    mock_postgres_repository.save_profile.return_value = saved_profile

    # Act
    result = await profile_service.search_and_save_profile(username)

    # Assert
    assert result == saved_profile
    mock_postgres_repository.get_profile.assert_called_once_with(username)
    mock_hiker_repository.buscar_perfil_por_username.assert_called_once_with(username)
    mock_postgres_repository.save_profile.assert_called_once()

@pytest.mark.asyncio
async def test_get_profile_details(profile_service, mock_hiker_repository, mock_postgres_repository):
    # Arrange
    username = "test_user"
    profile = {
        "id": 1,
        "username": username,
        "full_name": "Test User",
        "followers_count": 1000,
        "following_count": 500,
        "bio": "Test bio"
    }
    details = {
        "engagement_rate": 3.5,
        "average_likes": 500,
        "average_comments": 50,
        "post_frequency": 2.5
    }

    mock_postgres_repository.get_profile.return_value = profile
    mock_hiker_repository.get_profile_details.return_value = details

    # Act
    result = await profile_service.get_profile_details(username)

    # Assert
    assert result == {**profile, "details": details}
    mock_postgres_repository.get_profile.assert_called_once_with(username)
    mock_hiker_repository.get_profile_details.assert_called_once_with(profile["id"])

@pytest.mark.asyncio
async def test_list_profiles(profile_service, mock_postgres_repository):
    # Arrange
    profiles = [
        {
            "id": 1,
            "username": "user1",
            "full_name": "User One",
            "followers_count": 1000,
            "following_count": 500,
            "bio": "Bio 1"
        },
        {
            "id": 2,
            "username": "user2",
            "full_name": "User Two",
            "followers_count": 2000,
            "following_count": 1000,
            "bio": "Bio 2"
        }
    ]
    mock_postgres_repository.list_profiles.return_value = profiles

    # Act
    result = await profile_service.list_profiles(limit=10, offset=0)

    # Assert
    assert result == profiles
    mock_postgres_repository.list_profiles.assert_called_once_with(10, 0) 