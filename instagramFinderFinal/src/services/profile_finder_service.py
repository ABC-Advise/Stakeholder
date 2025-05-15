from typing import Dict, Any, List, Optional
import asyncio # Importar asyncio
from ..repositories.hiker_repository import HikerRepository
from ..repositories.postgres_repository import PostgresRepository
from .profile_validator import ProfileValidator
# Adicionar importação direta da função de normalização global
from ..services.profile_validator import _global_normalizar_leve_com_espacos as global_normalizar_leve_com_espacos
from difflib import SequenceMatcher

class ProfileFinderService:
    def __init__(self, hiker_repository: HikerRepository, postgres_repository: PostgresRepository):
        self.hiker_repository = hiker_repository
        self.postgres_repository = postgres_repository
        self.validator = ProfileValidator()

    async def find_profiles_for_entity(self, entity_type: str, entity_id: int) -> Dict[str, Any]:
        """
        Busca perfis Instagram para uma entidade específica (empresa, pessoa ou advogado)
        """
        # Buscar informações da entidade
        entity = await self.postgres_repository.get_entity(entity_type, entity_id)
        if not entity:
            raise ValueError(f"Entidade {entity_type} com ID {entity_id} não encontrada")

        # Padronizar campos obrigatórios no objeto entity
        entity_out = {}
        if entity_type == "empresa":
            entity_out["id"] = entity.get("id")
            entity_out["razao_social"] = entity.get("razao_social")
            entity_out["nome_fantasia"] = entity.get("nome_fantasia")
            entity_out["cnpj"] = entity.get("cnpj")
        elif entity_type == "advogado":
            entity_out["id"] = entity.get("id")
            entity_out["firstname"] = entity.get("firstname")
            entity_out["lastname"] = entity.get("lastname")
            entity_out["nome"] = f"{entity.get('firstname', '')} {entity.get('lastname', '')}".strip()
            entity_out["oab"] = entity.get("oab")
            entity_out["cpf"] = entity.get("cpf")
        elif entity_type == "pessoa":
            entity_out["id"] = entity.get("id")
            entity_out["firstname"] = entity.get("firstname")
            entity_out["lastname"] = entity.get("lastname")
            entity_out["nome"] = f"{entity.get('firstname', '')} {entity.get('lastname', '')}".strip()
            entity_out["cpf"] = entity.get("cpf")
        else:
            entity_out = entity.copy()  # fallback para tipos desconhecidos

        # Buscar perfis candidatos (lista já enriquecida)
        candidates = await self._search_candidates(entity_type, entity)
        
        validated_profile = None # Initialize validated_profile
        scored_candidates = [] # Initialize list for scored candidates returned by validator

        try:
            if entity_type == "empresa":
                # Unpack the tuple returned by the validator
                validated_profile, scored_candidates = await self.validator.validar_perfil_empresa(entity, candidates)
            elif entity_type == "advogado":
                validated_profile, scored_candidates = await self.validator.validar_perfil_advogado(entity, candidates)
            elif entity_type == "pessoa":
                validated_profile, scored_candidates = await self.validator.validar_perfil_pessoa(entity, candidates)
        except Exception as e:
            print(f"ERRO ao validar perfis para {entity_type} {entity_id}: {str(e)}")
            import traceback
            print(traceback.format_exc())
            validated_profile = None
            scored_candidates = []

        # Ajustar o dicionário validated_profile se ele existir (manter is_business_profile bool)
        if validated_profile:
             profile_data = validated_profile.get("perfil")
             is_business_value = validated_profile.get("is_business_profile") if profile_data else None
             validated_profile["is_business_profile"] = is_business_value if isinstance(is_business_value, bool) else False
             if profile_data:
                 profile_data['is_business'] = validated_profile["is_business_profile"]

        response_data = {
            "entity": entity_out,
            "validated_profile": validated_profile, 
            "possible_profiles": None,
            "candidates": candidates if candidates else None,
            "error": None
        }

        # Sempre tentar incluir possible_profiles se houver candidatos
        possible_usernames = []
        if scored_candidates:
            scored_candidates.sort(
                key=lambda x: (
                    x.get("score") if x.get("score") is not None else -1,
                    x.get("detalhes_validacao", {}).get("score_nome", -1) if isinstance(x.get("detalhes_validacao"), dict) else -1
                ),
                reverse=True
            )
            possible_usernames = [
                cand.get("perfil", {}).get("username") 
                for cand in scored_candidates[:2] 
                if cand.get("perfil", {}).get("username")
            ]
        
        if not possible_usernames and candidates:
            possible_usernames = [
                c.get("username") 
                for c in candidates[:2] 
                if c.get("username")
            ]

        if possible_usernames:
            response_data["possible_profiles"] = possible_usernames

        return response_data

    async def find_profiles_for_all_entities(self, entity_type: str) -> List[Dict[str, Any]]:
        """
        Busca perfis Instagram para todas as entidades de um tipo específico
        """
        entities_from_db = await self.postgres_repository.get_entities_without_instagram(entity_type)
        initial_count = len(entities_from_db)

        entities_to_process = []
        seen_nome_fantasia = set()
        seen_razao_social = set()

        if entity_type == "empresa":
            for entity in entities_from_db:
                nome_f = entity.get("name") 
                razao_s = entity.get("razao_social")
                
                is_duplicate = False
                if nome_f and nome_f.strip():
                    if nome_f in seen_nome_fantasia:
                        is_duplicate = True
                    else:
                        seen_nome_fantasia.add(nome_f)
                
                if not is_duplicate and razao_s and razao_s.strip():
                    if razao_s in seen_razao_social:
                        is_duplicate = True
                    else:
                        seen_razao_social.add(razao_s)
                
                if not is_duplicate:
                    entities_to_process.append(entity)
        else:
            entities_to_process = entities_from_db
        
        total_entities = len(entities_to_process)
        print(f"  -> Encontradas {initial_count} entidades no DB. Após filtro de duplicação, {total_entities} entidades do tipo '{entity_type}' serão processadas...")

        semaphore = asyncio.Semaphore(11)
        tasks = []
        completed_count = 0
        counter_lock = asyncio.Lock()

        async def process_entity_task(entity_dict):
            nonlocal completed_count 
            entity_id = entity_dict.get("id")
            entity_name = entity_dict.get("name", f"ID {entity_id}")
            result_message = ""
            result_data = None
            try:
                result_data = await self.find_profiles_for_entity(entity_type, entity_id)
                if result_data.get("validated_profile"):
                    result_message = f"Perfil encontrado e validado para {entity_name} (ID: {entity_id})!"
                else:
                    result_message = f"Nenhum perfil validado encontrado para {entity_name} (ID: {entity_id})."
            except Exception as e:
                result_message = f"ERRO ao processar {entity_type} {entity_id} ({entity_name}): {str(e)}"
                result_data = {
                    "entity": entity_dict, 
                    "error": str(e),
                    "candidates": None,
                    "validated_profile": None,
                    "possible_profiles": None
                }
            finally:
                async with counter_lock:
                    completed_count += 1
                    print(f"  [{completed_count}/{total_entities}] {result_message}")
                return result_data 

        for entity in entities_to_process:
            task = asyncio.create_task(process_entity_task(entity))
            tasks.append(task)
            await asyncio.sleep(1 / 11) 
        
        print(f"\n  -> Aguardando conclusão de {len(tasks)} tarefas...")
        results = await asyncio.gather(*tasks)

        print(f"\n  -> Processamento paralelo de '{entity_type}' concluído.")
        
        # Calcular estatísticas
        total_entities = len(results)
        perfis_encontrados = sum(1 for r in results if r.get("validated_profile") is not None)
        perfis_com_possibilidades = sum(1 for r in results if r.get("possible_profiles") is not None and len(r.get("possible_profiles", [])) > 0)
        perfis_sem_resultados = sum(1 for r in results if r.get("validated_profile") is None and (r.get("possible_profiles") is None or len(r.get("possible_profiles", [])) == 0))
        
        # Adicionar estatísticas ao retorno
        stats = {
            "total_entities": total_entities,
            "perfis_validados": perfis_encontrados,
            "perfis_com_possibilidades": perfis_com_possibilidades,
            "perfis_sem_resultados": perfis_sem_resultados,
            "taxa_validacao": f"{(perfis_encontrados/total_entities)*100:.1f}%" if total_entities > 0 else "0%",
            "taxa_possibilidades": f"{(perfis_com_possibilidades/total_entities)*100:.1f}%" if total_entities > 0 else "0%"
        }
        
        return {
            "results": results,
            "statistics": stats
        }

    async def find_profiles_for_company_and_related(self, company_id: int) -> Dict[str, Any]:
        """
        Busca perfis Instagram para uma empresa e suas entidades relacionadas
        """
        company_result = None
        try:
            company_result = await self.find_profiles_for_entity("empresa", company_id)
        except ValueError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": f"Erro ao buscar perfil da empresa principal {company_id}: {str(e)}"}

        related_entities = await self.postgres_repository.get_related_entities(company_id)
        
        related_results = []
        for related_entity in related_entities: 
            entity_type = related_entity.get("type")
            entity_id = related_entity.get("id")
            
            if not entity_type or not entity_id:
                 related_results.append({
                     "entity": related_entity,
                     "error": "Tipo ou ID da entidade relacionada inválido"
                 })
                 continue 

            try:
                result = await self.find_profiles_for_entity(entity_type, entity_id)
                related_results.append(result)
            except ValueError as e: 
                 related_results.append({
                     "entity": related_entity, 
                     "error": str(e)
                 })
            except Exception as e:
                related_results.append({
                    "entity": related_entity, 
                    "error": f"Erro ao buscar perfil para {entity_type} {entity_id}: {str(e)}"
                })

        return {
            "company": company_result,
            "related_entities": related_results
        }

    async def _search_candidates(self, entity_type: str, entity: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Busca candidatos de perfil usando diferentes estratégias e enriquece com detalhes.
        Aplica um pré-filtro para reduzir chamadas à API de detalhamento.
        *Otimização*: Pula o enriquecimento detalhado para entity_type='pessoa'.
        """
        try:
            initial_candidates_data = []

            def normalize_and_tokenize(text: Optional[str]) -> set[str]:
                if not text:
                    return set()
                return set(text.lower().split())

            search_name = ""
            if entity_type == "empresa":
                search_name = entity.get("nome_fantasia", "")
            elif entity_type in ["pessoa", "advogado"]:
                firstname = entity.get("firstname", "")
                lastname = entity.get("lastname", "")
                search_name = f"{firstname} {lastname}".strip() if firstname or lastname else ""
            
            entity_name_tokens = normalize_and_tokenize(search_name)
            search_name_leve = global_normalizar_leve_com_espacos(search_name)

            perfect_match_found = False
            perfect_matches_candidates = [] 
            seen_candidate_pks = set() 

            if search_name:
                search_results = await self.hiker_repository.buscar_perfis_por_nome(search_name)
                
                if isinstance(search_results, dict) and "error" not in search_results:
                    users_found_all = search_results.get("users", [])
                    users_to_check = users_found_all[:5] 
                    for user_data in users_to_check:
                        pk = user_data.get('pk')
                        if pk is None or pk in seen_candidate_pks: continue 
                        
                        profile_full_name_leve = global_normalizar_leve_com_espacos(user_data.get("full_name", ""))
                        if profile_full_name_leve and search_name_leve and profile_full_name_leve == search_name_leve:
                            perfect_matches_candidates.append(user_data)
                            perfect_match_found = True
                            seen_candidate_pks.add(pk) 
                        else:
                            initial_candidates_data.append(user_data)
                            seen_candidate_pks.add(pk)
                
                if perfect_match_found:
                    initial_candidates_data = perfect_matches_candidates 
                
            if not perfect_match_found and entity_type in ["pessoa", "advogado"]:
                variation_terms = []
                firstname = entity.get("firstname", "")
                lastname = entity.get("lastname", "")
                if firstname and lastname:
                    name_parts = lastname.split()
                    if len(name_parts) > 0:
                        first_last_name = f"{firstname} {name_parts[-1]}".strip()
                        if first_last_name.lower() != search_name.lower(): 
                             variation_terms.append(first_last_name)
                    
                    if len(name_parts) > 0: 
                        first_lastname_part = name_parts[0]
                        fn_plus_first_ln = f"{firstname} {first_lastname_part}".strip()
                        if fn_plus_first_ln.lower() != search_name.lower() and \
                           fn_plus_first_ln.lower() != (first_last_name.lower() if 'first_last_name' in locals() else ''): # check against first_last_name if it was created
                            variation_terms.append(fn_plus_first_ln)

                    original_full_name_parts = search_name.split() 
                    if len(original_full_name_parts) >= 3:
                         second_name = original_full_name_parts[1]
                         last_name_part = original_full_name_parts[-1]
                         segundo_nome_comum = second_name.lower() in self.validator.segundos_nomes_comuns_set if hasattr(self.validator, 'segundos_nomes_comuns_set') and self.validator.segundos_nomes_comuns_set else False
                         if not segundo_nome_comum:
                             first_second_last = f"{firstname} {second_name} {last_name_part}".strip()
                             if first_second_last.lower() != search_name.lower():
                                 variation_terms.append(first_second_last)

                partial_candidates_needed = 5 
                partial_candidates_found = []
                
                for attempt_name in variation_terms:
                    if not attempt_name or partial_candidates_needed <= 0:
                        break 

                    search_results_var = await self.hiker_repository.buscar_perfis_por_nome(attempt_name) # Renamed variable
                    
                    if isinstance(search_results_var, dict) and "error" not in search_results_var: # Use renamed variable
                        users_found_all_var = search_results_var.get("users", []) # Use renamed variable
                        users_to_check_var = users_found_all_var[:5] # Use renamed variable
                        for user_data in users_to_check_var: # Use renamed variable
                            pk = user_data.get('pk')
                            if pk is None or pk in seen_candidate_pks: continue 

                            partial_candidates_found.append(user_data)
                            seen_candidate_pks.add(pk)
                            partial_candidates_needed -= 1
                            if partial_candidates_needed <= 0:
                                break 
                initial_candidates_data.extend(partial_candidates_found)

            if entity_type in ["pessoa", "advogado"] and entity.get("empresa_id"):
                company = await self.postgres_repository.get_entity("empresa", entity["empresa_id"])
                if company and company.get("instagram_username"):
                    followers = await self.hiker_repository.buscar_seguidores(company["instagram_username"])
                    num_followers = 0
                    if isinstance(followers, dict) and "error" not in followers:
                        users = followers.get("users", [])
                        num_followers = len(users)
                        for user_data in users:
                            pk = user_data.get('pk')
                            if pk is not None and pk not in seen_candidate_pks:
                                initial_candidates_data.append(user_data)
                                seen_candidate_pks.add(pk)

            processed_candidates_list = [] 
            
            if entity_type != "pessoa":
                detail_tasks = []
                detail_semaphore = asyncio.Semaphore(11) 

                async def fetch_details_task(candidate_dict_param): # Renamed parameter
                    async with detail_semaphore:
                        username_param = candidate_dict_param.get('username') # Use renamed parameter
                        if not username_param: return 
                        try:
                            detailed_info = await self.hiker_repository.buscar_perfil_por_username(username_param) # Use renamed parameter
                            if isinstance(detailed_info, dict) and "error" not in detailed_info:
                                candidate_dict_param["bio"] = detailed_info.get("biography")
                                candidate_dict_param["is_business"] = detailed_info.get("is_business")
                                candidate_dict_param["follower_count"] = detailed_info.get("follower_count")
                                candidate_dict_param["following_count"] = detailed_info.get("following_count")
                                candidate_dict_param["media_count"] = detailed_info.get("media_count")
                                candidate_dict_param["pk"] = detailed_info.get("pk", candidate_dict_param["pk"])
                                candidate_dict_param["full_name"] = detailed_info.get("full_name", candidate_dict_param["full_name"])
                                candidate_dict_param["profile_pic_url"] = detailed_info.get("profile_pic_url", candidate_dict_param["profile_pic_url"])
                                candidate_dict_param["is_private"] = detailed_info.get("is_private", candidate_dict_param["is_private"])
                                candidate_dict_param["is_verified"] = detailed_info.get("is_verified", candidate_dict_param["is_verified"])
                            else:
                                pass
                        except Exception as e_fetch: # Renamed exception variable
                            pass 

                for basic_candidate_info in initial_candidates_data:
                    username_iter = basic_candidate_info.get("username") # Renamed variable
                    if not username_iter: continue
                    
                    current_candidate_data = {
                        "pk": basic_candidate_info.get("pk"),
                        "username": username_iter, # Use renamed variable
                        "full_name": basic_candidate_info.get("full_name"),
                        "profile_pic_url": basic_candidate_info.get("profile_pic_url"),
                        "is_private": basic_candidate_info.get("is_private", False),
                        "is_verified": basic_candidate_info.get("is_verified", False),
                        "bio": None, 
                        "is_business": None,
                        "follower_count": None,
                        "following_count": None,
                        "media_count": None
                    }
                    processed_candidates_list.append(current_candidate_data) 

                    is_potentially_relevant = False
                    if not entity_name_tokens: 
                        is_potentially_relevant = True
                    else:
                        candidate_fn_tokens = normalize_and_tokenize(basic_candidate_info.get("full_name"))
                        if any(token in candidate_fn_tokens for token in entity_name_tokens):
                            is_potentially_relevant = True
                    
                    if is_potentially_relevant:
                        task = asyncio.create_task(fetch_details_task(current_candidate_data)) 
                        detail_tasks.append(task)
                
                if detail_tasks:
                    await asyncio.gather(*detail_tasks)
            
            else: 
                 for basic_candidate_info in initial_candidates_data:
                      processed_candidates_list.append({
                        "pk": basic_candidate_info.get("pk"),
                        "username": basic_candidate_info.get("username"),
                        "full_name": basic_candidate_info.get("full_name"),
                        "profile_pic_url": basic_candidate_info.get("profile_pic_url"),
                        "is_private": basic_candidate_info.get("is_private", False),
                        "is_verified": basic_candidate_info.get("is_verified", False),
                        "bio": None, 
                        "is_business": None,
                        "follower_count": None,
                        "following_count": None,
                        "media_count": None
                    })

            final_candidates_list = []
            seen_usernames = set()
            for candidate in processed_candidates_list: 
                candidate_username = candidate.get("username")
                if candidate_username and candidate_username not in seen_usernames:
                    final_candidates_list.append(candidate)
                    seen_usernames.add(candidate_username)
            
            final_candidates_summary = [
                { 
                  'username': c.get('username'), 
                  'full_name': c.get('full_name'), 
                  'bio_present': bool(c.get('bio')), 
                  'is_business': c.get('is_business') 
                } for c in final_candidates_list
            ]
            return final_candidates_list

        except Exception as e:
            return []

    def close(self):
        """
        Fecha conexões e recursos
        """
        pass 

    async def find_names_in_followers(self, target_username: str, names_to_find: List[str], similarity_threshold: float = 0.5) -> Dict[str, Any]:
        """
        Busca nomes específicos entre os seguidores de um perfil do Instagram.
        
        Args:
            target_username: Username do perfil-alvo
            names_to_find: Lista de nomes a serem buscados
            similarity_threshold: Limiar de similaridade para matching (0.0 a 1.0)
            
        Returns:
            Dict contendo:
            - found_names: Lista de nomes encontrados com seus matches
            - total_followers: Total de seguidores analisados
            - possible_profiles: Possíveis matches se não houver similarity > 0.8
            - error: Mensagem de erro, se houver
        """
        try:
            print(f"\n[DEBUG] Iniciando busca para perfil: {target_username}")
            print(f"[DEBUG] Nomes a buscar: {names_to_find}")
            
            # Primeiro, buscar o perfil-alvo para obter o ID
            profile = await self.hiker_repository.buscar_perfil_por_username(target_username)
            
            if not profile or "error" in profile:
                return {
                    "found_names": [],
                    "total_followers": 0,
                    "possible_profiles": [],
                    "error": f"Erro ao buscar perfil {target_username}: {profile.get('error', 'Perfil não encontrado')}"
                }

            profile_id = profile.get("pk")
            if not profile_id:
                return {
                    "found_names": [],
                    "total_followers": 0,
                    "possible_profiles": [],
                    "error": f"ID do perfil {target_username} não encontrado"
                }

            print(f"[DEBUG] ID do perfil encontrado: {profile_id}")
            total_followers_expected = profile.get("follower_count", 0)
            print(f"[DEBUG] Total de seguidores esperado: {total_followers_expected}\n")

            all_followers = []
            max_id = None
            last_max_id = None
            found_names_set = set()
            found_matches = []
            possible_profiles = []
            found_strong_matches = {name: None for name in names_to_find}

            normalized_names = [global_normalizar_leve_com_espacos(name) for name in names_to_find]

            while True:
                print(f"[DEBUG] Buscando página de seguidores (max_id: {max_id})")
                followers_response = await self.hiker_repository.buscar_seguidores(profile_id, max_id)
                
                if not followers_response or (isinstance(followers_response, dict) and "error" in followers_response):
                    error_msg = followers_response.get('error', 'Erro desconhecido') if isinstance(followers_response, dict) else 'Resposta inválida'
                    print(f"[DEBUG] Erro ao buscar seguidores: {error_msg}")
                    break

                # Corrigir aqui: se for lista, pode ser [seguidores, next_max_id]
                if isinstance(followers_response, list):
                    if len(followers_response) > 0 and isinstance(followers_response[0], list):
                        current_followers = followers_response[0]
                        next_max_id = followers_response[1] if len(followers_response) > 1 else None
                    else:
                        current_followers = followers_response
                        next_max_id = None
                else:
                    current_followers = followers_response.get("users", [])
                    next_max_id = followers_response.get("next_max_id")

                print(f"[DEBUG] Tipo de current_followers: {type(current_followers)} | Exemplo: {current_followers[:2] if current_followers else 'vazio'}")

                if not current_followers or (max_id and max_id == last_max_id):
                    print("[DEBUG] Não há mais seguidores para buscar")
                    break

                last_max_id = max_id

                for follower in current_followers:
                    try:
                        if isinstance(follower, (str, int)):
                            follower_details = await self.hiker_repository.buscar_perfil_por_id(str(follower))
                        elif isinstance(follower, list):
                            print(f"[DEBUG] Ignorando seguidor em formato de lista: {follower}")
                            continue
                        elif isinstance(follower, dict):
                            follower_details = follower
                        else:
                            print(f"[DEBUG] Tipo inesperado de seguidor: {type(follower)}")
                            continue

                        if follower_details and "error" not in follower_details:
                            all_followers.append(follower_details)
                            full_name = follower_details.get('full_name', '')
                            follower_username = follower_details.get('username', '')
                            if full_name:
                                print(f"[DEBUG] Processando seguidor: {full_name}")
                            for idx, (original_name, normalized_name) in enumerate(zip(names_to_find, normalized_names)):
                                normalized_follower_name = global_normalizar_leve_com_espacos(full_name)
                                similarity = SequenceMatcher(None, normalized_follower_name, normalized_name).ratio()
                                if similarity >= 0.8 and found_strong_matches[original_name] is None:
                                    found_strong_matches[original_name] = {
                                        "searched_name": original_name,
                                        "matched_name": full_name,
                                        "username": follower_username,
                                        "similarity": round(similarity * 100, 2),
                                        "profile_url": f"https://instagram.com/{follower_username}"
                                    }
                                    print(f"[DEBUG] MATCH FORTE ENCONTRADO! '{original_name}' corresponde a '{full_name}' ({similarity * 100:.2f}% similar)")
                                elif similarity >= similarity_threshold:
                                    possible_profiles.append({
                                        "searched_name": original_name,
                                        "matched_name": full_name,
                                        "username": follower_username,
                                        "similarity": round(similarity * 100, 2),
                                        "profile_url": f"https://instagram.com/{follower_username}"
                                    })
                    except Exception as e:
                        print(f"[DEBUG] Erro ao processar seguidor: {str(e)}")
                        continue
                print(f"[DEBUG] Progresso: {len(all_followers)} seguidores processados")
                print(f"[DEBUG] Status da busca: {sum(1 for v in found_strong_matches.values() if v is not None)}/{len(names_to_find)} nomes encontrados com match forte\n")

                # Só encerra se TODOS os nomes tiverem match forte
                if all(v is not None for v in found_strong_matches.values()):
                    print("[DEBUG] Encerrando busca de seguidores por todos os matches fortes encontrados")
                    break
                max_id = next_max_id

            total_followers = len(all_followers)
            print(f"\n[DEBUG] Total final de seguidores processados: {total_followers}")

            strong_matches_list = [v for v in found_strong_matches.values() if v is not None]
            if len(strong_matches_list) == len(names_to_find):
                print(f"\n[DEBUG] Total de matches fortes encontrados: {len(strong_matches_list)}")
                return {
                    "found_names": strong_matches_list,
                    "total_followers": total_followers,
                    "possible_profiles": [],
                    "error": None
                }
            else:
                print(f"\n[DEBUG] Nem todos os nomes tiveram match forte. Retornando possíveis perfis.")
                return {
                    "found_names": [],
                    "total_followers": total_followers,
                    "possible_profiles": possible_profiles,
                    "error": None
                }
        except Exception as e:
            print(f"[DEBUG] Erro durante o processamento: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return {
                "found_names": [],
                "total_followers": 0,
                "possible_profiles": [],
                "error": f"Erro ao processar busca: {str(e)}"
            } 