from sqlalchemy import text
from typing import List, Dict, Any, Optional
# Importar a fábrica de sessões assíncronas e a classe AsyncSession
from src.config.database import AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession

class PostgresRepository:
    def __init__(self):
        # A sessão será obtida por método ou contexto, não no init diretamente
        # para melhor gerenciamento no async.
        # self.session = AsyncSessionLocal() # Removido daqui
        pass

    # Usar um gerenciador de contexto ou passar a sessão para os métodos
    # Abordagem: Passar a sessão (requer mudança no ProfileFinderService)
    # Abordagem alternativa: Criar sessão dentro de cada método (menos eficiente)
    # Abordagem preferida (para simplificar aqui): Usar AsyncSessionLocal diretamente no método
    # (Nota: para aplicações maiores, injeção de dependência ou contexto seria melhor)

    async def get_entity(self, entity_type: str, entity_id: int) -> Dict[str, Any]:
        """
        Busca uma entidade genérica (empresa, pessoa, advogado) pelo ID.
        """
        async with AsyncSessionLocal() as session:
            if entity_type == "empresa":
                return await self.buscar_empresa_por_id(session, entity_id)
            elif entity_type == "pessoa":
                return await self.buscar_pessoa_por_id(session, entity_id)
            elif entity_type == "advogado":
                return await self.buscar_advogado_por_id(session, entity_id)
            else:
                print(f"Tipo de entidade desconhecido: {entity_type}")
                return None

    # Métodos auxiliares agora recebem a sessão e são async
    async def buscar_empresa_por_id(self, session: AsyncSession, empresa_id: int):
        query = text("""
            SELECT *, empresa_id as id FROM plataforma_stakeholders.empresa
            WHERE empresa_id = :empresa_id
        """)
        result = await session.execute(query, {"empresa_id": empresa_id})
        row = result.fetchone()
        return dict(row._mapping) if row else None

    async def buscar_pessoa_por_id(self, session: AsyncSession, pessoa_id: int):
        query = text("""
            SELECT *, pessoa_id as id FROM plataforma_stakeholders.pessoa
            WHERE pessoa_id = :pessoa_id
        """)
        result = await session.execute(query, {"pessoa_id": pessoa_id})
        row = result.fetchone()
        return dict(row._mapping) if row else None

    async def buscar_advogado_por_id(self, session: AsyncSession, advogado_id: int):
        query = text("""
            SELECT *, advogado_id as id FROM plataforma_stakeholders.advogado
            WHERE advogado_id = :advogado_id
        """)
        result = await session.execute(query, {"advogado_id": advogado_id})
        row = result.fetchone()
        return dict(row._mapping) if row else None

    async def get_entities_without_instagram(self, entity_type: str) -> List[Dict[str, Any]]:
        """
        Busca entidades de um tipo específico que não possuem Instagram cadastrado.
        Para Empresas, busca todas que atendem aos critérios básicos, a desduplicação será feita no serviço.
        Para outros tipos, aplica DISTINCT ON no nome completo.
        """
        async with AsyncSessionLocal() as session:
            query = None # Inicializa query

            if entity_type == "empresa":
                # Seleciona ID, nome_fantasia (como name), e razao_social. Remove DISTINCT ON.
                select_columns = "empresa_id as id, nome_fantasia as name, razao_social"
                where_clause = "(instagram IS NULL OR instagram = '') AND nome_fantasia IS NOT NULL AND nome_fantasia <> ''"
                order_by_clause = "nome_fantasia, empresa_id" # Manter ordem para consistência
                query = text(f"""
                    SELECT {select_columns}
                    FROM plataforma_stakeholders.empresa
                    WHERE {where_clause}
                    ORDER BY {order_by_clause}
                """)
            elif entity_type in ["pessoa", "advogado"]:
                name_column = "firstname || ' ' || lastname"
                id_column = f"{entity_type}_id"
                table_name = f"plataforma_stakeholders.{entity_type}"
                where_clause = "(instagram IS NULL OR instagram = '') AND firstname IS NOT NULL AND firstname <> '' AND lastname IS NOT NULL AND lastname <> ''"
                # Mantém DISTINCT ON para pessoa/advogado
                distinct_clause = f"DISTINCT ON ({name_column}) {name_column} as name, {id_column} as id"
                order_by_clause = f"{name_column}, {id_column}"
                query = text(f"""
                    SELECT {distinct_clause}
                    FROM {table_name}
                    WHERE {where_clause}
                    ORDER BY {order_by_clause}
                """)
            else:
                print(f"Erro: Tipo de entidade inválido para busca sem instagram: {entity_type}")
                return []

            try:
                result = await session.execute(query)
                entities = result.fetchall()
                return [dict(row._mapping) for row in entities]
            except Exception as e:
                print(f"Erro ao buscar {entity_type}s sem Instagram: {str(e)}")
                await session.rollback()
                return []

    async def get_related_entities(self, origin_id: int, origin_type_id: int) -> List[Dict[str, Any]]:
        """
        Busca entidades (pessoas, advogados) relacionadas a uma entidade de qualquer tipo
        que ainda NÃO possuem um perfil do Instagram cadastrado.
        Retorna cpf (pessoa/advogado) ou cnpj (empresa) como identificador público.
        """
        async with AsyncSessionLocal() as session:
            query = text("""
                WITH RelatedEntities AS (
                    SELECT 
                        r.entidade_destino_id AS related_id,
                        r.tipo_destino_id AS related_type_id,
                        ted.descricao AS tipo_destino_str
                    FROM plataforma_stakeholders.relacionamentos r
                    JOIN plataforma_stakeholders.tipo_entidade ted 
                        ON r.tipo_destino_id = ted.tipo_entidade_id
                    WHERE r.entidade_origem_id = :entity_id
                      AND r.tipo_origem_id = :entity_type_id
                    UNION
                    SELECT 
                        r.entidade_origem_id AS related_id,
                        r.tipo_origem_id AS related_type_id,
                        teo.descricao AS tipo_origem_str
                    FROM plataforma_stakeholders.relacionamentos r
                    JOIN plataforma_stakeholders.tipo_entidade teo 
                        ON r.tipo_origem_id = teo.tipo_entidade_id
                    WHERE r.entidade_destino_id = :entity_id
                      AND r.tipo_destino_id = :entity_type_id
                )
                SELECT 
                    re.related_id AS id,
                    CASE 
                        WHEN p.pessoa_id IS NOT NULL THEN 'pessoa'
                        WHEN a.advogado_id IS NOT NULL THEN 'advogado'
                    END AS type,
                    COALESCE(p.firstname, a.firstname) AS firstname,
                    COALESCE(p.lastname, a.lastname) AS lastname,
                    a.oab,
                    COALESCE(p.instagram, a.instagram) AS instagram_db
                FROM RelatedEntities re
                LEFT JOIN plataforma_stakeholders.pessoa p 
                    ON re.related_id = p.pessoa_id
                LEFT JOIN plataforma_stakeholders.advogado a 
                    ON re.related_id = a.advogado_id
                WHERE p.pessoa_id IS NOT NULL OR a.advogado_id IS NOT NULL;
            """)
            try:
                result = await session.execute(query, {"entity_id": origin_id, "entity_type_id": origin_type_id})
                entities = result.fetchall()
                return [dict(row._mapping) for row in entities]
            except Exception as e:
                print(f"Erro ao buscar entidades relacionadas: {str(e)}")
                await session.rollback()
                return []

    async def get_entity_id_by_cpf_cnpj(self, entity_type: str, identifier: str) -> Optional[int]:
        """
        Busca ID da entidade por CPF/CNPJ/OAB.
        Para advogados, tenta primeiro por CPF e depois por OAB.
        """
        table_map = {
            "empresa": ("plataforma_stakeholders.empresa", "cnpj", "empresa_id"),
            "pessoa": ("plataforma_stakeholders.pessoa", "cpf", "pessoa_id"),
            "advogado": ("plataforma_stakeholders.advogado", "cpf", "advogado_id"),
        }

        if entity_type not in table_map:
            print(f"Tipo de entidade desconhecido: {entity_type}")
            return None

        table_name, identifier_col, id_col = table_map[entity_type]
        
        async with AsyncSessionLocal() as session:
            try:
                if entity_type == "advogado":
                    # Tenta primeiro por CPF (se for numérico)
                    clean_identifier = ''.join(filter(str.isdigit, identifier))
                    if clean_identifier:
                        query = text(f"SELECT {id_col} FROM {table_name} WHERE {identifier_col} = :identifier")
                        result = await session.execute(query, {"identifier": clean_identifier})
                        entity_row = result.fetchone()
                        if entity_row:
                            return entity_row[0]
                    
                    # Se não encontrou por CPF, tenta por OAB
                    query = text(f"SELECT {id_col} FROM {table_name} WHERE oab = :identifier")
                    result = await session.execute(query, {"identifier": identifier})
                    entity_row = result.fetchone()
                    if entity_row:
                        return entity_row[0]
                    
                    print(f"Nenhum advogado encontrado com CPF ou OAB = {identifier}")
                    return None
                else:
                    # Para empresa e pessoa, limpa o identificador e busca normalmente
                    clean_identifier = ''.join(filter(str.isdigit, identifier))
                    if not clean_identifier:
                        print(f"Identificador inválido após limpeza: {identifier}")
                        return None
                        
                    query = text(f"SELECT {id_col} FROM {table_name} WHERE {identifier_col} = :identifier")
                    result = await session.execute(query, {"identifier": clean_identifier})
                    entity_row = result.fetchone()
                    if entity_row:
                        return entity_row[0]
                    
                    print(f"Nenhuma entidade '{entity_type}' encontrada com identificador={identifier}")
                    return None
                    
            except Exception as e:
                print(f"Erro ao buscar ID para {entity_type} com identificador={identifier}: {str(e)}")
                await session.rollback()
                return None

    # Métodos save_profile, get_profile, list_profiles não foram incluídos na edição anterior,
    # precisariam ser ajustados para async também se fossem usados pelo serviço.

    # A função close() não é mais necessária da mesma forma, pois as sessões são gerenciadas por método.
    # def close(self):
    #     pass 

    async def get_dashboard_stats(self):
        async with AsyncSessionLocal() as session:
            # Empresas (deduplicadas por nome_fantasia)
            empresas_sem = await session.scalar(text(
                """SELECT COUNT(DISTINCT nome_fantasia) FROM plataforma_stakeholders.empresa WHERE instagram IS NULL OR instagram = ''"""
            ))
            empresas_com = await session.scalar(text(
                """SELECT COUNT(DISTINCT nome_fantasia) FROM plataforma_stakeholders.empresa WHERE instagram IS NOT NULL AND instagram <> ''"""
            ))
            # Pessoas
            pessoas_sem = await session.scalar(text(
                """SELECT COUNT(*) FROM plataforma_stakeholders.pessoa WHERE instagram IS NULL OR instagram = ''"""
            ))
            pessoas_com = await session.scalar(text(
                """SELECT COUNT(*) FROM plataforma_stakeholders.pessoa WHERE instagram IS NOT NULL AND instagram <> ''"""
            ))
            # Advogados
            advogados_sem = await session.scalar(text(
                """SELECT COUNT(*) FROM plataforma_stakeholders.advogado WHERE instagram IS NULL OR instagram = ''"""
            ))
            advogados_com = await session.scalar(text(
                """SELECT COUNT(*) FROM plataforma_stakeholders.advogado WHERE instagram IS NOT NULL AND instagram <> ''"""
            ))
            return [
                {"tipo": "empresa", "quantidade_sem_instagram": empresas_sem, "quantidade_com_instagram": empresas_com},
                {"tipo": "pessoa", "quantidade_sem_instagram": pessoas_sem, "quantidade_com_instagram": pessoas_com},
                {"tipo": "advogado", "quantidade_sem_instagram": advogados_sem, "quantidade_com_instagram": advogados_com},
            ] 