from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from ..config.database import get_db
from ..repositories.hiker_repository import HikerRepository
from ..repositories.postgres_repository import PostgresRepository
from ..services.profile_service import ProfileService

router = APIRouter(prefix="/profiles", tags=["profiles"])

def get_profile_service(db: Session = Depends(get_db)) -> ProfileService:
    hiker_repository = HikerRepository()
    postgres_repository = PostgresRepository(db)
    return ProfileService(hiker_repository, postgres_repository)

@router.get("/{username}")
async def get_profile(username: str, service: ProfileService = Depends(get_profile_service)):
    """
    Busca um perfil pelo username
    """
    try:
        profile = await service.search_and_save_profile(username)
        return profile
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{username}/details")
async def get_profile_details(username: str, service: ProfileService = Depends(get_profile_service)):
    """
    Obtém detalhes completos de um perfil
    """
    try:
        details = await service.get_profile_details(username)
        return details
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/")
async def list_profiles(
    limit: int = 10,
    offset: int = 0,
    service: ProfileService = Depends(get_profile_service)
):
    """
    Lista perfis salvos no banco de dados
    """
    try:
        profiles = await service.list_profiles(limit, offset)
        return profiles
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 