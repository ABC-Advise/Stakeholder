from typing import List, Dict, Any
from ..repositories.postgres_repository import PostgresRepository
from ..repositories.hiker_repository import HikerRepository
import json
from datetime import datetime

class CompanyProfileFinder:
    def __init__(self, postgres_repository: PostgresRepository, hiker_repository: HikerRepository):
        self.postgres_repository = postgres_repository
        self.hiker_repository = hiker_repository
        self.fallback_file = "fallback_companies.json"

    async def find_companies_without_instagram(self) -> List[Dict[str, Any]]:
        """
        Busca empresas que não possuem Instagram cadastrado
        """
        # Buscar empresas sem Instagram
        companies = await self.postgres_repository.get_companies_without_instagram()
        
        # Filtrar empresas com nome_fantasia vazio
        companies = [c for c in companies if c.get("nome_fantasia")]
        
        # Remover duplicações baseado no nome_fantasia
        seen_names = set()
        unique_companies = []
        for company in companies:
            name = company["nome_fantasia"].lower().strip()
            if name not in seen_names:
                seen_names.add(name)
                unique_companies.append(company)
        
        return unique_companies

    async def find_instagram_profiles(self, companies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Busca perfis do Instagram para as empresas fornecidas
        """
        results = {
            "found": [],
            "not_found": []
        }

        for company in companies:
            try:
                # Buscar perfil por nome_fantasia
                search_result = await self.hiker_repository.buscar_perfis_por_nome(company["nome_fantasia"])
                
                if "error" in search_result:
                    self._add_to_fallback(company, f"Erro na busca: {search_result['error']}")
                    results["not_found"].append(company)
                    continue

                # Validar e processar resultados
                if "users" in search_result and search_result["users"]:
                    # TODO: Implementar validação do perfil encontrado
                    profile = search_result["users"][0]  # Pegar primeiro resultado por enquanto
                    results["found"].append({
                        "company_id": company["id"],
                        "nome_fantasia": company["nome_fantasia"],
                        "instagram": profile["username"]
                    })
                else:
                    self._add_to_fallback(company, "Nenhum perfil encontrado")
                    results["not_found"].append(company)

            except Exception as e:
                self._add_to_fallback(company, f"Erro inesperado: {str(e)}")
                results["not_found"].append(company)

        return results

    def _add_to_fallback(self, company: Dict[str, Any], reason: str):
        """
        Adiciona empresa ao arquivo de fallback
        """
        try:
            # Carregar fallback existente
            fallback_data = []
            try:
                with open(self.fallback_file, 'r', encoding='utf-8') as f:
                    fallback_data = json.load(f)
            except FileNotFoundError:
                pass

            # Adicionar nova entrada
            fallback_data.append({
                "id": company["id"],
                "nome_fantasia": company["nome_fantasia"],
                "reason": reason,
                "timestamp": datetime.now().isoformat()
            })

            # Salvar arquivo
            with open(self.fallback_file, 'w', encoding='utf-8') as f:
                json.dump(fallback_data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"Erro ao adicionar ao fallback: {str(e)}")

    async def process_companies(self) -> Dict[str, Any]:
        """
        Processa todas as empresas sem Instagram
        """
        # Buscar empresas sem Instagram
        companies = await self.find_companies_without_instagram()
        
        # Buscar perfis do Instagram
        results = await self.find_instagram_profiles(companies)
        
        return {
            "total_companies": len(companies),
            "profiles_found": len(results["found"]),
            "profiles_not_found": len(results["not_found"]),
            "results": results
        } 