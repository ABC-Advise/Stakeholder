from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from src.services.profile_finder_service import ProfileFinderService
from src.api.deps import get_profile_finder_service
from src.utils.busca_historico import registrar_busca

router = APIRouter(tags=["Busca Seguidores"])

# ... outros endpoints existentes ...

@router.post("/search-names-in-followers", tags=["Busca Seguidores"])
async def search_names_in_followers(
    target_username: str,
    names_to_find: List[str],
    similarity_threshold: float = 0.8,
    profile_finder_service: ProfileFinderService = Depends(get_profile_finder_service)
) -> Dict[str, Any]:
    """
    Busca nomes específicos entre os seguidores de um perfil do Instagram.
    
    Args:
        target_username: Username do perfil-alvo
        names_to_find: Lista de nomes a serem buscados
        similarity_threshold: Limiar de similaridade para matching (0.0 a 1.0)
        
    Returns:
        Dict contendo os nomes encontrados e informações adicionais
    """
    result = await profile_finder_service.find_names_in_followers(
        target_username=target_username,
        names_to_find=names_to_find,
        similarity_threshold=similarity_threshold
    )
    # Registrar busca no histórico
    status = 'erro' if result.get("error") else 'concluida'
    nome = f"Seguidores de {target_username} ({', '.join(names_to_find)})"
    registrar_busca(nome, 'seguidores', status)
    if result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"])
    return result 