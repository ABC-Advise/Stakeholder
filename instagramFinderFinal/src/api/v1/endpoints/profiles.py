from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response
from typing import List, Dict, Any, Optional
from src.services.profile_finder_service import ProfileFinderService
from src.repositories.postgres_repository import PostgresRepository
from src.api.deps import get_profile_finder_service
from src.api.models import (
    EntityProfileResponse, 
    AllEntitiesResponseItem, 
    CompanyRelatedResponse,
    ErrorResponse,
    ConfirmInstagramRequest
)
from sqlalchemy import text
from src.config.database import AsyncSessionLocal
import os
import json
import hashlib
from datetime import datetime, timedelta
import requests
from src.utils.busca_historico import obter_ultimas_buscas, registrar_busca
from src.services.find_path_refatorado import PathFinderConfig, SupabaseManager
from src.services.redis_manager import RedisManager
import time
import asyncio
from src.config import supabase_config

CACHE_DIR = "./cache_busca"
CACHE_EXPIRATION_MINUTES = 5

# Singleton do SupabaseManager
_supabase_manager = None

def get_supabase_manager():
    global _supabase_manager
    if _supabase_manager is None:
        redis_manager = RedisManager(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=int(os.getenv('REDIS_DB', 0)),
            password=os.getenv('REDIS_PASSWORD', None),
            connect_timeout=int(os.getenv('REDIS_CONNECT_TIMEOUT', 2))
        )
        _supabase_manager = SupabaseManager(redis_manager)
    return _supabase_manager

def get_postgres_repository():
    return PostgresRepository()

router = APIRouter()

@router.get(
    "/ultimas_buscas",
    response_model=Dict[str, Any],
    summary="Estatísticas gerais e histórico das últimas buscas"
)
async def ultimas_buscas(
    postgres_repo: PostgresRepository = Depends(get_postgres_repository)
):
    estatisticas = await postgres_repo.get_dashboard_stats()
    ultimas_buscas = obter_ultimas_buscas()
    return {
        "estatisticas": estatisticas,
        "ultimas_buscas": ultimas_buscas
    }

@router.get(
    "/{entity_type}",
    response_model=EntityProfileResponse,
    summary="Busca perfil para uma entidade específica por ID ou CPF/CNPJ/OAB",
    description="""Busca, valida e retorna o perfil do Instagram para uma entidade específica.
    
    Pode ser buscado diretamente pelo **entity_id** da entidade OU 
    pelo **identifier** (CPF para pessoa, CNPJ para empresa, CPF/CNPJ/OAB para advogado).
    
    **Exatamente um** dos parâmetros `entity_id` ou `identifier` deve ser fornecido.
    Para advogados, o campo `identifier` pode ser o CPF, CNPJ ou o número da OAB.
    """
)
async def find_entity_profile(
    entity_type: str = Path(..., description="Tipo da entidade (empresa, pessoa ou advogado)"),
    entity_id: Optional[int] = Query(None, description="ID da entidade (opcional se identifier for fornecido)"),
    identifier: Optional[str] = Query(None, description="CPF/CNPJ/OAB da entidade (opcional se entity_id for fornecido)"),
    profile_finder_service: ProfileFinderService = Depends(get_profile_finder_service),
    postgres_repo: PostgresRepository = Depends(get_postgres_repository)
) -> Any:
    """
    Endpoint para buscar perfil de entidade por ID ou CPF/CNPJ/OAB.
    """
    target_entity_id: Optional[int] = None

    if (entity_id is None and identifier is None) or (entity_id is not None and identifier is not None):
        raise HTTPException(
            status_code=400,
            detail="Exatamente um dos parâmetros 'entity_id' ou 'identifier' deve ser fornecido."
        )

    if identifier is not None:
        try:
            found_id = await postgres_repo.get_entity_id_by_cpf_cnpj(entity_type, identifier)
            if found_id is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Entidade '{entity_type}' com identificador '{identifier}' não encontrada."
                )
            target_entity_id = found_id
        except Exception as e:
            print(f"ERRO ao buscar ID por identificador '{identifier}': {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao buscar ID para o identificador fornecido: {str(e)}"
            )
    else:
        target_entity_id = entity_id

    if target_entity_id is None:
        raise HTTPException(status_code=500, detail="Erro interno: ID da entidade não determinado.")

    try:
        result = await profile_finder_service.find_profiles_for_entity(entity_type, target_entity_id)
        # Registrar busca no histórico
        nome = result.get('entity', {}).get('nome') or result.get('entity', {}).get('nome_fantasia') or result.get('entity', {}).get('razao_social') or str(target_entity_id)
        registrar_busca(nome, entity_type, 'concluida')
        return result
    except ValueError as e:
        registrar_busca(str(target_entity_id), entity_type, 'erro')
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        registrar_busca(str(target_entity_id), entity_type, 'erro')
        print(f"Erro inesperado ao processar {entity_type} ID {target_entity_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno ao processar a busca de perfil: {str(e)}")

@router.get(
    "/entities/all/{entity_type}", 
    response_model=Dict[str, Any],
    summary="Busca perfis para todas as entidades de um tipo sem Instagram",
    responses={500: {"model": ErrorResponse}}
)
async def find_all_entity_profiles(
    entity_type: str = Path(..., description="Tipo da entidade (empresa, pessoa, advogado)"),
    service: ProfileFinderService = Depends(get_profile_finder_service)
):
    """Busca perfis para todas as entidades de um tipo que ainda não possuem Instagram."""
    allowed_types = ["empresa", "pessoa", "advogado"]
    if entity_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"Tipo de entidade inválido. Use um de: {allowed_types}")
    try:
        results = await service.find_profiles_for_all_entities(entity_type)
        registrar_busca(f"Busca geral {entity_type}", entity_type, 'concluida')
        return results
    except Exception as e:
        registrar_busca(f"Busca geral {entity_type}", entity_type, 'erro')
        print(f"Erro inesperado em find_all_entity_profiles: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao processar a requisição.")

@router.get(
    "/company/{company_id}/related",
    response_model=CompanyRelatedResponse,
    summary="Busca perfis para uma empresa e seus relacionados",
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def find_company_and_related_profiles(
    company_id: int = Path(..., description="ID da empresa principal"),
    service: ProfileFinderService = Depends(get_profile_finder_service)
):
    """Busca perfis para a empresa principal e suas entidades relacionadas (pessoas/advogados sem Instagram)."""
    try:
        result = await service.find_profiles_for_company_and_related(company_id)
        nome = result.get('company', {}).get('entity', {}).get('nome_fantasia') or result.get('company', {}).get('entity', {}).get('razao_social') or str(company_id)
        registrar_busca(nome, 'empresa', 'concluida')
        return result
    except ValueError as e: # Captura erro caso o método levante ValueError diretamente
        registrar_busca(str(company_id), 'empresa', 'erro')
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        registrar_busca(str(company_id), 'empresa', 'erro')
        print(f"Erro inesperado em find_company_and_related_profiles: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao processar a requisição.")

@router.post(
    "/entity/{entity_type}/{entity_id}/confirm_instagram",
    response_model=Dict[str, Any],
    responses={
        200: {"description": "Instagram confirmado com sucesso"},
        400: {"model": ErrorResponse, "description": "Tipo de entidade inválido ou dados inválidos"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    }
)
async def confirm_instagram(
    entity_type: str,
    entity_id: int,
    request: ConfirmInstagramRequest,
    postgres_repo: PostgresRepository = Depends(get_postgres_repository)
):
    """
    Confirma manualmente o Instagram associado a uma entidade.
    
    - **entity_type**: Tipo da entidade (pessoa, advogado ou empresa)
    - **entity_id**: ID da entidade
    - **instagram**: Username do Instagram a ser confirmado
    """
    try:
        # Validar tipo de entidade
        if entity_type not in ["pessoa", "advogado", "empresa"]:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de entidade inválido. Deve ser 'pessoa', 'advogado' ou 'empresa'"
            )
            
        # Atualizar Instagram
        async with AsyncSessionLocal() as session:
            table_name = f"plataforma_stakeholders.{entity_type}"
            id_column = f"{entity_type}_id"
            
            query = text(f"""
                UPDATE {table_name}
                SET instagram = :instagram
                WHERE {id_column} = :entity_id
            """)
            
            await session.execute(
                query, 
                {
                    "instagram": request.instagram,
                    "entity_id": entity_id
                }
            )
            await session.commit()
            
            return {
                "message": f"Instagram confirmado com sucesso para {entity_type} {entity_id}",
                "entity": {
                    "id": entity_id,
                    "instagram": request.instagram
                }
            }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao confirmar Instagram: {str(e)}"
        )

@router.get(
    "/company/related/by-cnpj",
    response_model=CompanyRelatedResponse,
    summary="Busca perfis para uma empresa e seus relacionados via CNPJ",
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def find_company_and_related_by_cnpj(
    cnpj: str = Query(..., description="CNPJ da empresa"),
    postgres_repo: PostgresRepository = Depends(get_postgres_repository),
    service: ProfileFinderService = Depends(get_profile_finder_service)
):
    """Busca perfis para a empresa principal e suas entidades relacionadas (pessoas/advogados sem Instagram) via CNPJ."""
    try:
        company_id = await postgres_repo.get_entity_id_by_cpf_cnpj('empresa', cnpj)
        if not company_id:
            raise HTTPException(status_code=404, detail=f"Empresa com CNPJ {cnpj} não encontrada.")
        result = await service.find_profiles_for_company_and_related(company_id)
        if "error" in result and "não encontrada" in result["error"]:
            raise HTTPException(status_code=404, detail=result["error"])
        elif "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except Exception as e:
        print(f"Erro inesperado em find_company_and_related_by_cnpj: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao processar a requisição.")

@router.get(
    "/entities/list/all",
    response_model=Dict[str, Any],
    summary="Lista paginada de todas as entidades (empresa, pessoa, advogado) com status de Instagram"
)
async def list_all_entities(
    pagina: int = Query(1, ge=1, description="Número da página"),
    limite: int = Query(10, ge=1, le=100, description="Limite de itens por página"),
):
    query = """
        SELECT empresa_id AS id, cnpj, NULL AS cpf, nome_fantasia AS nome, instagram, 'empresa' AS tipo
        FROM plataforma_stakeholders.empresa
        UNION ALL
        SELECT pessoa_id AS id, NULL AS cnpj, cpf, firstname || ' ' || lastname AS nome, instagram, 'pessoa' AS tipo
        FROM plataforma_stakeholders.pessoa
        UNION ALL
        SELECT advogado_id AS id, NULL AS cnpj, cpf, firstname || ' ' || lastname AS nome, instagram, 'advogado' AS tipo
        FROM plataforma_stakeholders.advogado
        ORDER BY nome
        OFFSET :offset LIMIT :limit
    """
    offset = (pagina - 1) * limite

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text(query),
            {"offset": offset, "limit": limite}
        )
        rows = result.fetchall()

        data = []
        for row in rows:
            status = "Encontrado" if row.instagram else "Não encontrado"
            entidade = {
                "id": str(row.id),
                "nome": row.nome,
                "instagram": row.instagram,
                "status": status,
                "tipo": row.tipo
            }
            if row.tipo == "empresa":
                entidade["cnpj"] = row.cnpj
            else:
                entidade["cpf"] = row.cpf
            data.append(entidade)

        total = len(data)

        return {
            "data": data,
            "total": total,
            "pagina": pagina,
            "limite": limite
        }

@router.get(
    "/entities/list/empresa",
    response_model=Dict[str, Any],
    summary="Lista paginada de empresas"
)
async def list_empresas(
    pagina: int = Query(1, ge=1, description="Número da página"),
    limite: int = Query(10, ge=1, le=100, description="Limite de itens por página"),
):
    query = """
        SELECT empresa_id AS id, cnpj, nome_fantasia AS nome, instagram
        FROM plataforma_stakeholders.empresa
        ORDER BY nome_fantasia
        OFFSET :offset LIMIT :limit
    """
    offset = (pagina - 1) * limite

    async with AsyncSessionLocal() as session:
        result = await session.execute(text(query), {"offset": offset, "limit": limite})
        rows = result.fetchall()
        data = []
        for row in rows:
            status = "Encontrado" if row.instagram else "Não encontrado"
            data.append({
                "id": str(row.id),
                "cnpj": row.cnpj,
                "nome": row.nome or "",
                "instagram": row.instagram,
                "status": status
            })
        total = await session.scalar(text("SELECT COUNT(*) FROM plataforma_stakeholders.empresa"))
        return {
            "data": data,
            "total": total,
            "pagina": pagina,
            "limite": limite
        }

@router.get(
    "/entities/list/pessoa",
    response_model=Dict[str, Any],
    summary="Lista paginada de pessoas"
)
async def list_pessoas(
    pagina: int = Query(1, ge=1, description="Número da página"),
    limite: int = Query(10, ge=1, le=100, description="Limite de itens por página"),
):
    query = """
        SELECT pessoa_id AS id, cpf, firstname || ' ' || lastname AS nome, instagram
        FROM plataforma_stakeholders.pessoa
        ORDER BY firstname, lastname
        OFFSET :offset LIMIT :limit
    """
    offset = (pagina - 1) * limite

    async with AsyncSessionLocal() as session:
        result = await session.execute(text(query), {"offset": offset, "limit": limite})
        rows = result.fetchall()
        data = []
        for row in rows:
            status = "Encontrado" if row.instagram else "Não encontrado"
            data.append({
                "id": str(row.id),
                "cpf": row.cpf,
                "nome": row.nome or "",
                "instagram": row.instagram,
                "status": status
            })
        total = await session.scalar(text("SELECT COUNT(*) FROM plataforma_stakeholders.pessoa"))
        return {
            "data": data,
            "total": total,
            "pagina": pagina,
            "limite": limite
        }

@router.get(
    "/entities/list/advogado",
    response_model=Dict[str, Any],
    summary="Lista paginada de advogados"
)
async def list_advogados(
    pagina: int = Query(1, ge=1, description="Número da página"),
    limite: int = Query(10, ge=1, le=100, description="Limite de itens por página"),
):
    query = """
        SELECT advogado_id AS id, cpf, firstname || ' ' || lastname AS nome, instagram
        FROM plataforma_stakeholders.advogado
        ORDER BY firstname, lastname
        OFFSET :offset LIMIT :limit
    """
    offset = (pagina - 1) * limite

    async with AsyncSessionLocal() as session:
        result = await session.execute(text(query), {"offset": offset, "limit": limite})
        rows = result.fetchall()
        data = []
        for row in rows:
            status = "Encontrado" if row.instagram else "Não encontrado"
            data.append({
                "id": str(row.id),
                "cpf": row.cpf,
                "nome": row.nome or "",
                "instagram": row.instagram,
                "status": status
            })
        total = await session.scalar(text("SELECT COUNT(*) FROM plataforma_stakeholders.advogado"))
        return {
            "data": data,
            "total": total,
            "pagina": pagina,
            "limite": limite
        }

def sanitize_filename(s: str) -> str:
    s = s.lower().replace(" ", "_")
    s = "".join(c for c in s if c.isalnum() or c in ("_", "-"))
    return s[:50]

def get_cache_path(tipo: str, query: str, pagina: int = None, limite: int = None) -> str:
    base = f"{tipo}_{query}"
    if pagina is not None and limite is not None:
        base += f"_{pagina}_{limite}"
    base = sanitize_filename(base)
    hash_part = hashlib.md5(base.encode()).hexdigest()[:8]
    filename = f"cache_{base}_{hash_part}.json"
    return os.path.join(CACHE_DIR, filename)

def is_cache_valid(path: str) -> bool:
    if not os.path.exists(path):
        return False
    mtime = datetime.fromtimestamp(os.path.getmtime(path))
    return datetime.now() - mtime < timedelta(minutes=CACHE_EXPIRATION_MINUTES)

def load_cache(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def save_cache(path: str, data):
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
    except Exception:
        pass

@router.get(
    "/entities/search",
    response_model=Dict[str, Any],
    summary="Busca entidades por nome ou documento (empresa, pessoa ou advogado)"
)
async def search_entities(
    tipo: str = Query(..., description="Tipo da entidade: empresa, pessoa ou advogado"),
    query: str = Query(..., description="Termo de busca: nome, CPF, CNPJ ou OAB"),
    pagina: int = Query(1, ge=1, description="Número da página"),
    limite: int = Query(10, ge=1, le=100, description="Limite de itens por página"),
):
    cache_path = get_cache_path(tipo, query, pagina, limite)
    try:
        if is_cache_valid(cache_path):
            cached = load_cache(cache_path)
            if cached is not None:
                return cached
    except Exception:
        pass

    if tipo not in ["empresa", "pessoa", "advogado"]:
        return {"data": [], "total": 0, "pagina": pagina, "limite": limite}

    offset = (pagina - 1) * limite
    query_param = f"%{query.lower()}%"

    if tipo == "empresa":
        sql = """
            SELECT empresa_id AS id, cnpj, nome_fantasia AS nome, instagram
            FROM plataforma_stakeholders.empresa
            WHERE LOWER(cnpj) LIKE :query OR LOWER(nome_fantasia) LIKE :query
            ORDER BY nome_fantasia
            OFFSET :offset LIMIT :limit
        """
        count_sql = """
            SELECT COUNT(*) FROM plataforma_stakeholders.empresa
            WHERE LOWER(cnpj) LIKE :query OR LOWER(nome_fantasia) LIKE :query
        """
    elif tipo == "pessoa":
        sql = f"""
            SELECT pessoa_id AS id, cpf, firstname || ' ' || lastname AS nome, instagram
            FROM plataforma_stakeholders.pessoa
            WHERE LOWER(cpf) LIKE :query OR LOWER(firstname || ' ' || lastname) LIKE :query
            ORDER BY firstname, lastname
            OFFSET :offset LIMIT :limit
        """
        count_sql = f"""
            SELECT COUNT(*) FROM plataforma_stakeholders.pessoa
            WHERE LOWER(cpf) LIKE :query OR LOWER(firstname || ' ' || lastname) LIKE :query
        """
    else:  # advogado
        sql = f"""
            SELECT advogado_id AS id, cpf, oab, firstname || ' ' || lastname AS nome, instagram
            FROM plataforma_stakeholders.advogado
            WHERE LOWER(cpf) LIKE :query OR LOWER(oab) LIKE :query OR LOWER(firstname || ' ' || lastname) LIKE :query
            ORDER BY firstname, lastname
            OFFSET :offset LIMIT :limit
        """
        count_sql = f"""
            SELECT COUNT(*) FROM plataforma_stakeholders.advogado
            WHERE LOWER(cpf) LIKE :query OR LOWER(oab) LIKE :query OR LOWER(firstname || ' ' || lastname) LIKE :query
        """

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text(sql),
            {"query": query_param, "offset": offset, "limit": limite}
        )
        rows = result.fetchall()
        data = []
        for row in rows:
            status = "Encontrado" if row.instagram else "Não encontrado"
            entidade = {
                "id": str(row.id),
                "nome": row.nome or "",
                "instagram": row.instagram,
                "status": status
            }
            if tipo == "empresa":
                entidade["cnpj"] = row.cnpj
            elif tipo == "pessoa":
                entidade["cpf"] = row.cpf
            else:  # advogado
                entidade["cpf"] = row.cpf
                entidade["oab"] = row.oab
            data.append(entidade)

        total = await session.scalar(text(count_sql), {"query": query_param})

        result_dict = {
            "data": data,
            "total": total,
            "pagina": pagina,
            "limite": limite
        }
        try:
            save_cache(cache_path, result_dict)
        except Exception:
            pass
        return result_dict

@router.get("/proxy/instagram-image")
async def proxy_instagram_image(url: str = Query(..., description="URL da imagem do Instagram")):
    """
    Proxy para imagens do Instagram, resolvendo problemas de CORS.
    """
    try:
        if not url.startswith("http") or "instagram" not in url:
            raise HTTPException(status_code=400, detail="URL inválida ou não permitida.")

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        }
        resp = requests.get(url, timeout=10, headers=headers)
        content_type = resp.headers.get("Content-Type", "image/jpeg")
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail="Erro ao buscar imagem do Instagram.")
        return Response(content=resp.content, media_type=content_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao fazer proxy da imagem: {str(e)}")

@router.get(
    "/entities/{entity_type}/related",
    response_model=Dict[str, Any],
    summary="Busca entidades relacionadas a uma entidade (empresa, pessoa ou advogado) usando CNPJ ou CPF"
)
async def find_related_entities_by_identifier(
    entity_type: str = Path(..., description="Tipo da entidade de origem (empresa, pessoa, advogado)"),
    identifier: str = Query(..., description="CNPJ ou CPF da entidade de origem"),
    postgres_repo: PostgresRepository = Depends(get_postgres_repository)
):
    """
    Busca pessoas e advogados relacionados a uma entidade (empresa, pessoa ou advogado) que ainda não possuem Instagram.
    Recebe CNPJ (empresa) ou CPF (pessoa/advogado) como parâmetro.
    """
    tipo_map = {"pessoa": 1, "empresa": 3, "advogado": 4}
    if entity_type not in tipo_map:
        raise HTTPException(status_code=400, detail="Tipo de entidade inválido. Use 'empresa', 'pessoa' ou 'advogado'.")
    origin_type_id = tipo_map[entity_type]
    # Buscar o id da entidade pelo identificador
    entity_id = await postgres_repo.get_entity_id_by_cpf_cnpj(entity_type, identifier)
    if not entity_id:
        registrar_busca(identifier, entity_type, 'erro')
        raise HTTPException(status_code=404, detail=f"Entidade '{entity_type}' com identificador '{identifier}' não encontrada.")
    related = await postgres_repo.get_related_entities(entity_id, origin_type_id)
    registrar_busca(identifier, entity_type, 'concluida')
    return {"related_entities": related}

@router.get(
    "/caminhos/bfs",
    summary="Busca todos os menores caminhos (BFS) entre dois usuários"
)
async def buscar_caminhos_bfs(
    username_origem: str = Query(..., description="Username de origem"),
    username_alvo: str = Query(..., description="Username de destino"),
    max_search_depth: int = Query(5, description="Profundidade máxima da busca")
):
    try:
        manager = get_supabase_manager()
        
        # Busca IDs com retry
        start_id = None
        target_id = None
        max_retries = 3
        retry_delay = 1

        for attempt in range(max_retries):
            try:
                # Aguardar as operações do Supabase
                start_id = await asyncio.to_thread(manager.get_id_from_username, username_origem)
                target_id = await asyncio.to_thread(manager.get_id_from_username, username_alvo)
                if start_id and target_id:
                    break
                await asyncio.sleep(retry_delay)
                retry_delay *= 2
            except Exception as e:
                if attempt == max_retries - 1:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Erro ao buscar IDs dos usuários após {max_retries} tentativas: {str(e)}"
                    )

        if not start_id or not target_id:
            return {
                "origem": username_origem,
                "alvo": username_alvo,
                "caminhos": [],
                "quantidade": 0,
                "erro": "Usuário(s) não encontrado(s)."
            }

        # Busca caminhos com retry
        paths = None
        retry_delay = 1
        for attempt in range(max_retries):
            try:
                # Aguardar a operação do Supabase
                paths = await asyncio.to_thread(manager.find_all_shortest_paths_bfs, start_id, target_id, max_search_depth)
                if paths is not None:
                    break
                await asyncio.sleep(retry_delay)
                retry_delay *= 2
            except Exception as e:
                if attempt == max_retries - 1:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Erro ao buscar caminhos após {max_retries} tentativas: {str(e)}"
                    )

        caminhos = []
        if paths:
            for path in paths:
                usernames = []
                for uid in path:
                    # Aguardar a operação do Supabase
                    username = await asyncio.to_thread(manager.get_username_from_id, uid)
                    if username:
                        usernames.append(username)
                if len(usernames) == len(path):
                    caminhos.append(usernames)

        return {
            "origem": username_origem,
            "alvo": username_alvo,
            "caminhos": caminhos,
            "quantidade": len(caminhos)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao processar a busca de caminhos: {str(e)}"
        )

@router.get(
    "/caminhos/dfs",
    summary="Busca todos os caminhos (DFS) entre dois usuários até a profundidade máxima"
)
async def buscar_caminhos_dfs(
    username_origem: str = Query(..., description="Username de origem"),
    username_alvo: str = Query(..., description="Username de destino"),
    max_search_depth: int = Query(5, description="Profundidade máxima da busca")
):
    try:
        manager = get_supabase_manager()
        
        # Busca IDs com retry
        start_id = None
        target_id = None
        max_retries = 3
        retry_delay = 1

        for attempt in range(max_retries):
            try:
                # Aguardar as operações do Supabase
                start_id = await asyncio.to_thread(manager.get_id_from_username, username_origem)
                target_id = await asyncio.to_thread(manager.get_id_from_username, username_alvo)
                if start_id and target_id:
                    break
                await asyncio.sleep(retry_delay)
                retry_delay *= 2
            except Exception as e:
                if attempt == max_retries - 1:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Erro ao buscar IDs dos usuários após {max_retries} tentativas: {str(e)}"
                    )

        if not start_id or not target_id:
            return {"erro": "Usuário(s) não encontrado(s)."}

        # Busca caminhos com retry
        all_paths = []
        retry_delay = 1
        for attempt in range(max_retries):
            try:
                # Aguardar a operação do Supabase
                await asyncio.to_thread(
                    manager.find_all_paths_dfs_recursive,
                    start_id,
                    target_id,
                    [start_id],
                    set(),
                    all_paths,
                    max_search_depth
                )
                if all_paths is not None:
                    break
                await asyncio.sleep(retry_delay)
                retry_delay *= 2
            except Exception as e:
                if attempt == max_retries - 1:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Erro ao buscar caminhos após {max_retries} tentativas: {str(e)}"
                    )

        caminhos = []
        if all_paths:
            for path in all_paths:
                usernames = []
                for uid in path:
                    # Aguardar a operação do Supabase
                    username = await asyncio.to_thread(manager.get_username_from_id, uid)
                    if username:
                        usernames.append(username)
                if len(usernames) == len(path):
                    caminhos.append(usernames)

        return {
            "origem": username_origem,
            "alvo": username_alvo,
            "caminhos": caminhos,
            "quantidade": len(caminhos)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao processar a busca de caminhos: {str(e)}"
        )

# Adicionar endpoints para busca por nome/cnpj/cpf aqui futuramente 