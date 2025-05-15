from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from src.config.database import AsyncSessionLocal
import os
import unicodedata
import re

STOPWORDS_PT = {
    "a", "o", "as", "os", "um", "uma", "uns", "umas",
    "de", "do", "da", "dos", "das", "em", "no", "na", "nos", "nas",
    "por", "para", "com", "sem", "sob", "sobre", "ante", "após", "até", "desde", "entre",
    "e", "ou", "mas", "nem", "que", "se", "porque", "pois", "quando", "onde", "como", "qual", "quais",
    "este", "esta", "estes", "estas", "esse", "essa", "esses", "essas", "aquele", "aquela", "aqueles", "aquelas",
    "isto", "isso", "aquilo",
    "ser", "estar", "ter", "haver",
    "meu", "minha", "meus", "minhas", "teu", "tua", "teus", "tuas", "seu", "sua", "seus", "suas",
    "nosso", "nossa", "nossos", "nossas", "vosso", "vossa", "vossos", "vossas",
    "ele", "ela", "eles", "elas", "eu", "tu", "nós", "vós",
    "já", "ainda", "também", "apenas", "somente", "muito", "pouco", "mais", "menos",
    "sim", "não", "talvez", "sempre", "nunca", "agora", "hoje", "ontem", "amanhã",
    "coisas", "coisa", "parte", "partes", "tipo", "tipos", "forma", "formas", "meio", "meios",
    "serviços", "serviço", "atividades", "atividade", "produtos", "produto", "outros", "outras",
    "relacionados", "relacionadas", "exceto", "inclusive", "conforme", "mediante", "principalmente",
    "especificados", "especificadas", "nao", "anteriormente"
}

# Funções de normalização globais (para uso em carregamento de arquivos e constantes)
def _global_normalizar_leve_com_espacos(texto: str) -> str:
    if not texto:
        return ""
    texto = texto.lower()
    texto = re.sub(r'\\b(jr|j R|j r)\\.?\\b', 'junior', texto, flags=re.IGNORECASE)
    texto = unicodedata.normalize('NFKD', texto)
    texto = ''.join([c for c in texto if not unicodedata.combining(c)])
    texto = re.sub(r'[^a-z0-9\\s]+', ' ', texto) 
    texto = re.sub(r'\\s+', ' ', texto).strip() 
    return texto

def _global_normalizar_agressiva_sem_espacos(texto: str) -> str:
    if not texto:
        return ""
    texto = _global_normalizar_leve_com_espacos(texto)
    texto = re.sub(r'[^a-z0-9]', '', texto)
    return texto

class ProfileValidator:
    def __init__(self):
        self.sobrenomes_comuns_set = self._carregar_set_de_arquivo('sobrenomes_comuns.txt')
        self.segundos_nomes_comuns_set = self._carregar_set_de_arquivo('segundos_nomes_comuns.txt')
        self.negative_words_set = self._carregar_set_de_arquivo('negative_words.txt')

    def _carregar_set_de_arquivo(self, filename: str) -> set:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, filename)
        try:
            with open(file_path, encoding='utf-8') as f:
                return set(_global_normalizar_agressiva_sem_espacos(l.strip()) for l in f if l.strip())
        except FileNotFoundError:
            print(f"Arquivo {filename} não encontrado em: {file_path}")
            return set()

    def normalizar_leve_com_espacos(self, texto: str) -> str:
        if not texto:
            return ""
        texto = texto.lower()
        texto = re.sub(r'\\b(jr|j R|j r)\\.?\\b', 'junior', texto, flags=re.IGNORECASE)
        texto = unicodedata.normalize('NFKD', texto)
        texto = ''.join([c for c in texto if not unicodedata.combining(c)])
        texto = re.sub(r'[^a-z0-9\\s]+', ' ', texto) 
        texto = re.sub(r'\\s+', ' ', texto).strip() 
        return texto

    def normalizar_agressiva_sem_espacos(self, texto: str) -> str:
        if not texto:
            return ""
        texto = self.normalizar_leve_com_espacos(texto)
        texto = re.sub(r'[^a-z0-9]', '', texto)
        return texto

    def normalizar(self, texto: str) -> str: # Alias
        return self.normalizar_agressiva_sem_espacos(texto)

    def validar_nome_empresa(self, nome_fantasia: str, nome_perfil: str) -> float:
        nome_fantasia_norm_leve = self.normalizar_leve_com_espacos(nome_fantasia)
        nome_perfil_norm_leve = self.normalizar_leve_com_espacos(nome_perfil)

        if not nome_fantasia_norm_leve or not nome_perfil_norm_leve:
            return 0.0
        if nome_fantasia_norm_leve == nome_perfil_norm_leve:
             return 1.0

        tokens_fantasia = set(nome_fantasia_norm_leve.split())
        tokens_perfil = set(nome_perfil_norm_leve.split())

        if not tokens_fantasia or not tokens_perfil:
            return 0.0
        if not tokens_fantasia.issubset(tokens_perfil):
                 return 0.0

        extra_tokens = tokens_perfil.difference(tokens_fantasia)
        num_extra = len(extra_tokens)
        penalty = num_extra * 0.1
        final_score = max(0.0, 1.0 - penalty)
        return final_score

    async def validar_segmento(self, segmento_id: int, bio: str) -> bool:
        query = text(
            "SELECT descricao "
            "FROM plataforma_stakeholders.segmento_empresa "
            "WHERE segmento_id = :segmento_id"
        )
        async with AsyncSessionLocal() as session:
            result = await session.execute(query, {"segmento_id": segmento_id})
            segmento_row = result.fetchone()
        
        if not segmento_row: return False
        segmento = dict(segmento_row._mapping)
        descricao_segmento_original = segmento.get("descricao")
        if not descricao_segmento_original or not descricao_segmento_original.strip(): return False
        
        desc_pre_processed = self.normalizar_leve_com_espacos(descricao_segmento_original)
        palavras_descricao = desc_pre_processed.split(' ')
        chunks_apos_stopwords = [p for p in palavras_descricao if p not in STOPWORDS_PT and p.strip()]
        if not chunks_apos_stopwords and palavras_descricao:
            chunks_apos_stopwords = [p for p in palavras_descricao if p.strip()] 
        if not chunks_apos_stopwords: return False
            
        chunks_finais_normalizados_agressivo = [self.normalizar_agressiva_sem_espacos(chunk) for chunk in chunks_apos_stopwords if self.normalizar_agressiva_sem_espacos(chunk)]
        if not chunks_finais_normalizados_agressivo: return False

        bio_normalizada_agressivo = self.normalizar_agressiva_sem_espacos(bio)
        if not bio_normalizada_agressivo: return False
            
        for chunk_norm_agressivo in chunks_finais_normalizados_agressivo:
            if chunk_norm_agressivo in bio_normalizada_agressivo:
                return True
        return False

    async def validar_perfil_empresa(self, empresa: Dict[str, Any], perfis_instagram: List[Dict[str, Any]]) -> Tuple[Optional[Dict[str, Any]], List[Dict[str, Any]]]:
        perfis_validados = []
        all_scored_candidates = []

        for perfil in perfis_instagram:
            if perfil.get("is_private", False): # EMPRESA: Perfis privados SÃO DESCARTADOS
                current_scored_candidate = {
                    "perfil": perfil, "score": 0,
                    "is_business_profile": perfil.get("is_business", False), 
                    "empresa": empresa,
                    "detalhes_validacao": {
                        "excluido_por": "Perfil Privado", "nome_pontos": 0, "bio_pontos": 0,
                        "username_pontos": 0, "is_business_bonus": 0, "segmento_encontrado": False 
                    }
                }
                all_scored_candidates.append(current_scored_candidate)
                continue 

            pontos_nome = 0
            nome_score = self.validar_nome_empresa(empresa["nome_fantasia"], perfil.get("full_name", ""))
            if nome_score == 0:
                pontos_nome = 0
                segmento_validado = False 
                pontos_bio = 0
                pontos_username = -5 
                pontos_is_business = 5 if perfil.get("is_business", False) else 0
            else:
                pontos_nome = nome_score * 60
            
            pontos_bio = 0
            segmento_validado = await self.validar_segmento(empresa["segmento_id"], perfil.get("bio", ""))
            if segmento_validado:
                pontos_bio = 10
                
            pontos_username = 0
            username_validacao_score = self.validar_nome_empresa(empresa["nome_fantasia"], perfil.get("username", ""))
            if username_validacao_score == 0: 
                pontos_username = -5
            else:
                pontos_username = username_validacao_score * 10
            
            pontos_is_business = 0
            is_business_profile = perfil.get("is_business", False)
            if is_business_profile:
                pontos_is_business = 5

            score_total = pontos_nome + pontos_bio + pontos_username + pontos_is_business
            is_business_profile_bool = perfil.get("is_business", False) if isinstance(perfil.get("is_business"), bool) else False
                
            current_scored_candidate = {
                "perfil": perfil, "score": score_total, "is_business_profile": is_business_profile_bool,
                    "empresa": empresa, 
                    "detalhes_validacao": {
                        "nome_pontos": pontos_nome, "bio_pontos": pontos_bio,
                        "username_pontos": pontos_username, "is_business_bonus": pontos_is_business,
                        "segmento_encontrado": segmento_validado 
                    }
            }
            all_scored_candidates.append(current_scored_candidate)

            if nome_score > 0 and score_total >= 70:
                 perfis_validados.append(current_scored_candidate)

        best_validated = None
        if perfis_validados:
            best_validated = max(perfis_validados, key=lambda x: (x["score"], x["is_business_profile"]))
            if best_validated:
                 best_validated["is_business_profile"] = best_validated.get("is_business_profile", False)
        return best_validated, all_scored_candidates

    async def validar_perfil_pessoa(self, pessoa_info: Dict[str, str], perfis_instagram: List[Dict[str, Any]]) -> Tuple[Optional[Dict[str, Any]], List[Dict[str, Any]]]:
        # PESSOA: Perfis privados NÃO são descartados
        firstname_leve = self.normalizar_leve_com_espacos(pessoa_info.get("firstname", ""))
        lastname_leve = self.normalizar_leve_com_espacos(pessoa_info.get("lastname", ""))

        if not firstname_leve or not lastname_leve: 
            return None, []

        nome_completo_original_leve = f"{firstname_leve} {lastname_leve}".strip()
        nome_completo_original_agressivo = self.normalizar_agressiva_sem_espacos(nome_completo_original_leve)
        
        variacoes_nome_raw = _global_gerar_variacoes_nome( # Usa a versão global
            firstname_leve, 
            lastname_leve, 
            self.sobrenomes_comuns_set,
            self.segundos_nomes_comuns_set
        )
        
        variacoes_agressivas = {self.normalizar_agressiva_sem_espacos(v) for v in variacoes_nome_raw if v}
        variacoes_agressivas.add(nome_completo_original_agressivo)
        variacoes_leves_tokenizaveis = {self.normalizar_leve_com_espacos(v) for v in variacoes_nome_raw if v}
        variacoes_leves_tokenizaveis.add(nome_completo_original_leve)

        perfis_validados = []
        all_scored_candidates = []

        for perfil in perfis_instagram:
            perfil_full_name_str = perfil.get("full_name", "")
            if not perfil_full_name_str: 
                continue
            
            perfil_full_name_leve = self.normalizar_leve_com_espacos(perfil_full_name_str)
            perfil_full_name_agressivo = self.normalizar_agressiva_sem_espacos(perfil_full_name_leve)
            
            score_nome = 0.0
            match_type = "Nenhum"

            if perfil_full_name_agressivo == nome_completo_original_agressivo:
                score_nome = 100.0
                match_type = "Exato (Agressivo)"
            else:
                 set_tokens_original_agressivo_significativos = {
                     self.normalizar_agressiva_sem_espacos(t) 
                     for t in nome_completo_original_leve.split() 
                     if len(self.normalizar_agressiva_sem_espacos(t)) > 1
                 }
                 set_tokens_perfil_agressivo = {
                     self.normalizar_agressiva_sem_espacos(t) 
                     for t in perfil_full_name_leve.split()
                 }
                 num_tokens_originais_total = len(set_tokens_original_agressivo_significativos)
                 if num_tokens_originais_total == 2:
                     score_nome = 0.0 
                     match_type = "Descartado (Original 2 Tokens / Não Exato)"
                 elif not set_tokens_original_agressivo_significativos: 
                     score_nome = 0.0
                     match_type = "Erro Tokens Originais"
                 else:
                     tokens_originais_encontrados_no_perfil = set_tokens_original_agressivo_significativos.intersection(set_tokens_perfil_agressivo)
                     num_tokens_originais_encontrados = len(tokens_originais_encontrados_no_perfil)
                     proporcao_tokens_encontrados = num_tokens_originais_encontrados / num_tokens_originais_total
                     score_nome = proporcao_tokens_encontrados * 100
                     match_type = "Tokens Originais Proporcionais"

            discarded_for_common_name = False
            original_tokens_leve_list_sig = [] 
            if nome_completo_original_leve:
                 original_tokens_leve_list_sig = [t for t in nome_completo_original_leve.split() if len(self.normalizar_agressiva_sem_espacos(t)) > 1]
                 
            if len(original_tokens_leve_list_sig) > 0 and round(score_nome) == 50: 
                 num_original_tokens_sig_check = len(original_tokens_leve_list_sig)
                 
                 if 'tokens_originais_encontrados_no_perfil' in locals() and len(tokens_originais_encontrados_no_perfil) * 2 == num_original_tokens_sig_check:
                     if num_original_tokens_sig_check >= 2:
                         first_orig_agg = self.normalizar_agressiva_sem_espacos(original_tokens_leve_list_sig[0])
                         second_orig_agg = self.normalizar_agressiva_sem_espacos(original_tokens_leve_list_sig[1])
                         if tokens_originais_encontrados_no_perfil == {first_orig_agg, second_orig_agg}:
                             if second_orig_agg in self.segundos_nomes_comuns_set:
                                 score_nome = 0.0 
                                 match_type += " / Descartado (Segundo Nome Comum 50%)"
                                 discarded_for_common_name = True
                                 
                     if not discarded_for_common_name and num_original_tokens_sig_check >= 2:
                         first_orig_agg = self.normalizar_agressiva_sem_espacos(original_tokens_leve_list_sig[0])
                         last_orig_agg = self.normalizar_agressiva_sem_espacos(original_tokens_leve_list_sig[-1])
                         if tokens_originais_encontrados_no_perfil == {first_orig_agg, last_orig_agg}:
                             if last_orig_agg in self.sobrenomes_comuns_set:
                                 score_nome = 0.0 
                                 match_type += " / Descartado (Sobrenome Comum 50%)"
                                 discarded_for_common_name = True
            current_scored_candidate = {
                "perfil": perfil, "score": round(score_nome), "pessoa_info": pessoa_info,
                "detalhes_validacao": {
                    "match_type": match_type, "nome_score_bruto": score_nome,
                    "discarded_for_common_name_50_percent": discarded_for_common_name,
                    "nome_completo_original_normalizado_agressivo": nome_completo_original_agressivo,
                    "perfil_full_name_normalizado_agressivo": perfil_full_name_agressivo,
                    "tokens_originais_sig": list(set_tokens_original_agressivo_significativos) if 'set_tokens_original_agressivo_significativos' in locals() else [],
                    "tokens_perfil_sig": list(set_tokens_perfil_agressivo) if 'set_tokens_perfil_agressivo' in locals() else [],
                    "tokens_originais_encontrados": list(tokens_originais_encontrados_no_perfil) if 'tokens_originais_encontrados_no_perfil' in locals() else []
                }
            }
            all_scored_candidates.append(current_scored_candidate)
            if score_nome >= 65: 
                perfis_validados.append(current_scored_candidate)
        best_validated = max(perfis_validados, key=lambda x: x["score"]) if perfis_validados else None
        return best_validated, all_scored_candidates

    def _checar_descarte_50_porcento(
        self, score: float, tokens_encontrados: set,
        nome_referencia_tokens_sig_list: list, segundos_nomes_comuns: set, sobrenomes_comuns: set
    ) -> tuple[float, str, bool]:
        if round(score) != 50: return score, "", False
        if not nome_referencia_tokens_sig_list or not tokens_encontrados: return score, "", False
        num_ref_tokens = len(nome_referencia_tokens_sig_list)
        if len(tokens_encontrados) * 2 != num_ref_tokens: return score, "", False 

        match_type_descarte = ""
        score_final = score
        descartado = False

        if num_ref_tokens >= 2:
            first_ref_agg = self.normalizar_agressiva_sem_espacos(nome_referencia_tokens_sig_list[0])
            second_ref_agg = self.normalizar_agressiva_sem_espacos(nome_referencia_tokens_sig_list[1])
            if tokens_encontrados == {first_ref_agg, second_ref_agg}:
                if second_ref_agg in segundos_nomes_comuns:
                    score_final = 0.0
                    match_type_descarte = " / Descartado (Segundo Nome Comum 50%)"
                    descartado = True
            if not descartado and num_ref_tokens >= 1: 
                 last_ref_agg = self.normalizar_agressiva_sem_espacos(nome_referencia_tokens_sig_list[-1])
                 if tokens_encontrados == {first_ref_agg, last_ref_agg}:
                      if last_ref_agg in sobrenomes_comuns:
                          score_final = 0.0
                          match_type_descarte = " / Descartado (Sobrenome Comum 50%)"
                          descartado = True
        return score_final, match_type_descarte, descartado

    async def validar_perfil_advogado(self, advogado: Dict[str, Any], perfis_instagram: List[Dict[str, Any]]) -> Tuple[Optional[Dict[str, Any]], List[Dict[str, Any]]]:
        # ADVOGADO: Perfis privados NÃO são descartados por serem privados
        # LOG DE ENTRADA:

        advogado_id = advogado.get('id', 'N/A') 
        advogado_nome_completo = f"{advogado.get('firstname', '')} {advogado.get('lastname', '')}".strip()
        if not advogado_nome_completo:
             return None, [] 
        
        adv_nome_completo_leve = self.normalizar_leve_com_espacos(advogado_nome_completo)
        adv_nome_completo_agressivo = self.normalizar_agressiva_sem_espacos(adv_nome_completo_leve)
        adv_nomes_parts = adv_nome_completo_leve.split()
        adv_primeiro_ultimo_leve = f"{adv_nomes_parts[0]} {adv_nomes_parts[-1]}".strip() if len(adv_nomes_parts) >= 2 else None
        adv_primeiro_segundo_leve = f"{adv_nomes_parts[0]} {adv_nomes_parts[1]}".strip() if len(adv_nomes_parts) >= 2 else None
        adv_primeiro_ultimo_agressivo = self.normalizar_agressiva_sem_espacos(adv_primeiro_ultimo_leve) if adv_primeiro_ultimo_leve else None

        all_scored_candidates = [] 
        melhores_resultados = [] 

        BIO_TERMS_20 = {self.normalizar_agressiva_sem_espacos(t) for t in ["advogado", "advocacia", "oab"]}
        BIO_TERMS_10 = {self.normalizar_agressiva_sem_espacos(t) for t in ["direito", "juridico", "escritorio", "advocacia", "jurista", "lawyer", "law", "attorney"]}
        
        for perfil in perfis_instagram:
            score_total = 0; score_nome = 0; score_bio = 0; score_username = 0
            
            perfil_pk = perfil.get('pk'); perfil_username = perfil.get("username", ""); perfil_full_name = perfil.get("full_name", "")
            perfil_bio = perfil.get("bio", ""); perfil_is_private = perfil.get("is_private", False) # Não usado para exclusão direta de advogados

            perfil_username_agressivo = self.normalizar_agressiva_sem_espacos(perfil_username)
            perfil_fullname_leve = self.normalizar_leve_com_espacos(perfil_full_name)
            perfil_fullname_agressivo = self.normalizar_agressiva_sem_espacos(perfil_fullname_leve)
            perfil_bio_agressiva = self.normalizar_agressiva_sem_espacos(perfil_bio)

            detalhes_pontuacao = {}
            if perfil_fullname_leve == adv_nome_completo_leve:
                score_nome = 70; detalhes_pontuacao["nome_match"] = "Exato"
            elif adv_primeiro_ultimo_leve and perfil_fullname_leve == adv_primeiro_ultimo_leve:
                score_nome = 50; detalhes_pontuacao["nome_match"] = "Primeiro+Último"
            elif adv_primeiro_segundo_leve and perfil_fullname_leve == adv_primeiro_segundo_leve:
                score_nome = 40; detalhes_pontuacao["nome_match"] = "Primeiro+Segundo"
            else:
                score_nome = 0; detalhes_pontuacao["nome_match"] = "Nenhum"
            detalhes_pontuacao["score_nome"] = score_nome

            termos_20_encontrados = {term for term in BIO_TERMS_20 if term in perfil_bio_agressiva}
            termos_10_encontrados = {term for term in BIO_TERMS_10 if term in perfil_bio_agressiva}
            pontos_bio_bruto = (len(termos_20_encontrados) * 20) + (len(termos_10_encontrados) * 10)
            score_bio = min(pontos_bio_bruto, 50)
            detalhes_pontuacao["score_bio"] = score_bio; detalhes_pontuacao["termos_bio_20"] = list(termos_20_encontrados); detalhes_pontuacao["termos_bio_10"] = list(termos_10_encontrados)

            if perfil_username_agressivo == adv_nome_completo_agressivo:
                score_username = 30; detalhes_pontuacao["username_match"] = "Exato/Derivado"
            elif adv_primeiro_ultimo_agressivo and perfil_username_agressivo == adv_primeiro_ultimo_agressivo:
                 score_username = 15; detalhes_pontuacao["username_match"] = "Parcial (P+U)"
            else:
                 score_username = 0; detalhes_pontuacao["username_match"] = "Nenhum"
            detalhes_pontuacao["score_username"] = score_username

            adv_nome_completo_tokens_leve = set(adv_nome_completo_leve.split()) if adv_nome_completo_leve else set()
            perfil_fullname_tokens_leve = set(perfil_fullname_leve.split()) if perfil_fullname_leve else set()

            motivo_exclusao = None
            is_subset_check = perfil_fullname_tokens_leve.issubset(adv_nome_completo_tokens_leve) if perfil_fullname_tokens_leve else True

            if perfil_fullname_tokens_leve and not is_subset_check: # REGRA: Nome do perfil com termos alheios
                motivo_exclusao = "Nome do perfil com termos alheios ao nome do advogado"
            elif any(term in perfil_username_agressivo for term in _USERNAME_EXCLUSION_TERMS):
                 motivo_exclusao = "Username com termo de exclusão"
            elif any(term in perfil_fullname_agressivo for term in _INCOMPATIBLE_PROFESSION_TERMS):
                 motivo_exclusao = "Fullname indica profissão incompatível"
            elif any(term in perfil_bio_agressiva for term in _INCOMPATIBLE_PROFESSION_TERMS):
                 motivo_exclusao = "Bio indica profissão incompatível"

            if motivo_exclusao:
                score_total = 0 
                detalhes_pontuacao["excluido_por"] = motivo_exclusao
                current_scored_candidate = {"perfil": perfil, "score": score_total, "advogado_info": advogado, "detalhes_validacao": detalhes_pontuacao}
                all_scored_candidates.append(current_scored_candidate)
                continue 
            
            score_total = score_nome + score_bio + score_username
            current_scored_candidate = {"perfil": perfil, "score": score_total, "advogado_info": advogado, "detalhes_validacao": detalhes_pontuacao}
            all_scored_candidates.append(current_scored_candidate)

            if score_total >= 70:
                melhores_resultados.append(current_scored_candidate)

        melhores_resultados.sort(key=lambda x: x["score"], reverse=True)
        best_validated = melhores_resultados[0] if melhores_resultados else None
        return best_validated, all_scored_candidates

# --- Funções Globais Auxiliares e Constantes ---
def _global_gerar_variacoes_nome(firstname: str, lastname: str, 
                           sobrenomes_comuns: set = None, 
                           segundos_nomes_comuns: set = None) -> list:
    nome_completo_orig = f"{firstname} {lastname}".strip()
    if not nome_completo_orig: return []
    variacoes_sufixo_set = {nome_completo_orig}
    nome_agressivo_para_sufixo_check = _global_normalizar_agressiva_sem_espacos(nome_completo_orig)
    if "junior" in nome_agressivo_para_sufixo_check:
        variacoes_sufixo_set.add(re.sub(r'\\bjunior\\b', 'jr', nome_completo_orig, flags=re.IGNORECASE))
    elif "jr" in nome_agressivo_para_sufixo_check:
        variacoes_sufixo_set.add(re.sub(r'\\b(jr|j\\s*r)\\b', 'junior', nome_completo_orig, flags=re.IGNORECASE))

    variacoes_finais = set()
    for nome_base in variacoes_sufixo_set: 
        nomes = nome_base.split() 
        if not nomes: continue
        variacoes_finais.add(nome_base) 
        if len(nomes) > 1:
            variacoes_finais.add(f"{_global_normalizar_agressiva_sem_espacos(nomes[0][0])}. {' '.join(nomes[1:])}")
            variacoes_finais.add(f"{_global_normalizar_agressiva_sem_espacos(nomes[0][0])}{' '.join(nomes[1:])}")
        if len(nomes) >= 2:
            ultimo_nome_norm_agg = _global_normalizar_agressiva_sem_espacos(nomes[-1])
            if sobrenomes_comuns is None or ultimo_nome_norm_agg not in sobrenomes_comuns:
                is_segundo_comum = segundos_nomes_comuns and ultimo_nome_norm_agg in segundos_nomes_comuns
                if not (is_segundo_comum and len(nomes) > 2):
                    variacoes_finais.add(f"{nomes[0]} {nomes[-1]}")
            if len(nomes) > 2: 
                segundo_nome_norm_agg = _global_normalizar_agressiva_sem_espacos(nomes[1])
                is_sobrenome_comum = sobrenomes_comuns and segundo_nome_norm_agg in sobrenomes_comuns
                is_segundo_nome_comum = segundos_nomes_comuns and segundo_nome_norm_agg in segundos_nomes_comuns
                if not is_sobrenome_comum and not is_segundo_nome_comum:
                    variacoes_finais.add(f"{nomes[0]} {nomes[1]}")
            if len(nomes) > 1 and len(nomes[1]) > 0:
                variacoes_finais.add(f"{nomes[0]} {_global_normalizar_agressiva_sem_espacos(nomes[1][0])}") 
            if len(nomes) > 2:
                iniciais_dois_primeiros_agg = _global_normalizar_agressiva_sem_espacos(nomes[0][0]) + _global_normalizar_agressiva_sem_espacos(nomes[1][0])
                variacoes_finais.add(f"{iniciais_dois_primeiros_agg} {' '.join(nomes[2:])}")
                iniciais_com_ponto = f"{_global_normalizar_agressiva_sem_espacos(nomes[0][0])}.{_global_normalizar_agressiva_sem_espacos(nomes[1][0])}." 
                variacoes_finais.add(f"{iniciais_com_ponto} {' '.join(nomes[2:])}")
            iniciais_concatenadas_agg = "".join(_global_normalizar_agressiva_sem_espacos(p[0]) for p in nomes if p)
            if len(iniciais_concatenadas_agg) >= 2:
                variacoes_finais.add(iniciais_concatenadas_agg) 
            ultimo_nome_norm_agg = _global_normalizar_agressiva_sem_espacos(nomes[-1])
            if sobrenomes_comuns is None or ultimo_nome_norm_agg not in sobrenomes_comuns:
                is_segundo_comum = segundos_nomes_comuns and ultimo_nome_norm_agg in segundos_nomes_comuns
                if not is_segundo_comum:
                    variacoes_finais.add(f"{nomes[-1]} {nomes[0]}")
    return list(filter(None, variacoes_finais))

_USERNAME_EXCLUSION_TERMS = {
    _global_normalizar_agressiva_sem_espacos(term) for term in [
        "fanpage", "fã clube", "parodia", "parody", "meme", "memes", 
        "fake", "cover", "homenagem", "tributo", "naooficial", "notofficial"
    ]
}
_INCOMPATIBLE_PROFESSION_TERMS = {
    _global_normalizar_agressiva_sem_espacos(term) for term in [
        "fotografo", "fotografia", "photographer", "photography", 
        "musico", "musicista", "cantor", "banda", "dj", 
        "artista", "artist", "ilustrador", "illustrator", "desenhista", "designer",
        "modelo", "model", "ator", "atriz", "actor", "actress", "cinema", "filme", "tv",
        "influencer", "digitalinfluencer", "blogueiro", "blogger", "youtuber", "gamer", "streamer",
        "escritor", "poeta", "chef", "cozinheiro", "culinaria", 
        "medico", "doctor", "enfermeiro", "nurse", "dentista", "odontologia", "psicologo", "terapeuta",
        "engenheiro", "arquiteto", "personal trainer", "educador fisico", "atleta", "esportista",
        "jornalista", "reporter", "estudante"
    ]
}
TERMS_JURIDICOS = [
    "advogado", "advocacia", "oab", "direito", "jurídico", "lawyer", "law", "escritório", "criminalista", "cível", "trabalhista", "previdenciário",
    "⚖", "⚖️", "📚", "👩‍⚖️", "👨‍⚖️", "🧑‍⚖️", "📖", "📝", "��", "🏛", "🏛️"
]