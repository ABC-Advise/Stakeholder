from typing import Dict, Any, List
from ..repositories.hiker_repository import HikerRepository
from ..repositories.postgres_repository import PostgresRepository

class ProfileService:
    def __init__(self, hiker_repository: HikerRepository, postgres_repository: PostgresRepository):
        self.hiker_repository = hiker_repository
        self.postgres_repository = postgres_repository

    async def search_and_save_profile(self, username: str) -> Dict[str, Any]:
        """
        Busca um perfil no Instagram e salva no banco de dados
        """
        # Primeiro, verifica se o perfil já existe no banco
        existing_profile = await self.postgres_repository.get_profile(username)
        if existing_profile:
            return existing_profile

        # Se não existir, busca na Hiker API
        profile_data = await self.hiker_repository.buscar_perfil_por_username(username)
        
        # Formata os dados para salvar no banco
        formatted_data = {
            "username": profile_data["username"],
            "full_name": profile_data["full_name"],
            "followers_count": profile_data["followers_count"],
            "following_count": profile_data["following_count"],
            "bio": profile_data["bio"]
        }

        # Salva no banco de dados
        saved_profile = await self.postgres_repository.save_profile(formatted_data)
        return saved_profile

    async def get_profile_details(self, username: str) -> Dict[str, Any]:
        """
        Obtém detalhes completos de um perfil
        """
        # Busca no banco de dados
        profile = await self.postgres_repository.get_profile(username)
        if not profile:
            raise Exception("Perfil não encontrado")

        # Busca detalhes adicionais na Hiker API
        details = await self.hiker_repository.get_profile_details(profile["id"])
        
        # Combina os dados
        return {**profile, "details": details}

    async def list_profiles(self, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Lista perfis salvos no banco de dados
        """
        return await self.postgres_repository.list_profiles(limit, offset) 