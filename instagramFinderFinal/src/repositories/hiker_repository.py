import os
from hikerapi import AsyncClient
from dotenv import load_dotenv
from typing import Dict, Any
import aiohttp

load_dotenv()

class HikerRepository:
    def __init__(self):
        self.api_key = os.getenv("HIKER_API_KEY")
        self.client = AsyncClient(token=self.api_key)
        self.base_url = os.getenv("HIKER_BASE_URL")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def buscar_perfil_por_username(self, username: str) -> dict:
        """Busca informações básicas de um perfil do Instagram pelo username."""
        if not isinstance(username, str) or not username.strip():
            raise ValueError("O username deve ser uma string não vazia.")
        try:
            return await self.client.user_by_username_v1(username)
        except Exception as e:
            return {"error": f"Erro ao buscar perfil: {str(e)}"}

    async def get_profile_details(self, profile_id: str) -> dict:
        """Obtém detalhes adicionais de um perfil pelo ID."""
        if not isinstance(profile_id, str) or not profile_id.strip():
            raise ValueError("O profile_id deve ser uma string não vazia.")
        try:
            # Exemplo: pode ser user_about_v1 ou outro método conforme documentação
            return await self.client.user_about_v1(profile_id)
        except Exception as e:
            return {"error": f"Erro ao obter detalhes do perfil: {str(e)}"}

    async def buscar_perfil_por_id(self, user_id: str) -> dict:
        if not isinstance(user_id, str) or not user_id.strip():
            raise ValueError("O user_id deve ser uma string não vazia.")
        try:
            return await self.client.user_by_id_v1(user_id)
        except Exception as e:
            return {"error": f"Erro ao buscar perfil por ID: {str(e)}"}

    async def buscar_perfil_por_url(self, url: str) -> dict:
        if not isinstance(url, str) or not url.strip():
            raise ValueError("A URL deve ser uma string não vazia.")
        try:
            return await self.client.user_by_url_v1(url)
        except Exception as e:
            return {"error": f"Erro ao buscar perfil por URL: {str(e)}"}

    async def buscar_perfis_por_nome(self, nome: str) -> dict:
        if not isinstance(nome, str) or not nome.strip():
            raise ValueError("O nome deve ser uma string não vazia.")
        try:
            # search_accounts_v2 retorna múltiplos perfis
            return await self.client.search_accounts_v2(query=nome)
        except Exception as e:
            return {"error": f"Erro ao buscar perfis por nome: {str(e)}"}

    async def buscar_web_profile_info(self, username: str) -> dict:
        if not isinstance(username, str) or not username.strip():
            raise ValueError("O username deve ser uma string não vazia.")
        try:
            return await self.client.user_web_profile_info_v1(username)
        except Exception as e:
            return {"error": f"Erro ao buscar web profile info: {str(e)}"}

    async def buscar_seguidores(self, user_id: str, max_id: str = None) -> Dict[str, Any]:
        """
        Busca os seguidores de um usuário do Instagram.
        
        Args:
            user_id: ID do usuário
            max_id: ID máximo para paginação (opcional)
            
        Returns:
            Dict contendo a lista de seguidores ou erro
        """
        try:
            print(f"[DEBUG] Buscando seguidores para user_id: {user_id} com max_id: {max_id}")
            params = {"user_id": user_id}
            if max_id is not None:
                params["max_id"] = max_id
            return await self.client.user_followers_chunk_v1(**params)
        except Exception as e:
            print(f"[DEBUG] Erro ao buscar seguidores: {str(e)}")
            return {"error": f"Erro ao buscar seguidores: {str(e)}"} 