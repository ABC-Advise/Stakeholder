import asyncio
import os
from dotenv import load_dotenv
import json
import csv # Importar módulo csv
import datetime # Para timestamp no nome do arquivo

# Ajuste os imports com base na estrutura do seu projeto (se o script estiver em /scripts)
from src.repositories.hiker_repository import HikerRepository
from src.repositories.postgres_repository import PostgresRepository
from src.services.profile_finder_service import ProfileFinderService

async def main():
    # Carrega variáveis de ambiente do arquivo .env
    # O PostgresRepository agora deve ler a config diretamente (provavelmente via src/config/database.py)
    load_dotenv() 

    # Obtém apenas a chave da Hiker API, pois o repo do banco pega a config internamente
    hiker_api_key = os.getenv("HIKER_API_KEY")

    # Verifica se a chave da API foi carregada
    if not hiker_api_key:
        print("Erro: Variável de ambiente HIKER_API_KEY não definida.")
        return

    # Instancia os repositórios reais
    # O PostgresRepository não precisa mais da URL aqui
    postgres_repo = PostgresRepository()
    # O HikerRepository também não precisa mais da API key aqui
    hiker_repo = HikerRepository()

    # Instancia o serviço com os repositórios reais
    profile_finder = ProfileFinderService(hiker_repository=hiker_repo, postgres_repository=postgres_repo)

    print("Serviço de busca de perfis inicializado com conexões reais.")

    # Listas para guardar os dados que irão para os CSVs
    csv_data_found = []
    csv_header_found = [
        'entity_type', 'entity_id', 'entity_name',
        'validated_username', 'validated_full_name', 'validated_score'
    ]
    csv_data_not_found = []
    csv_header_not_found = [
        'entity_type', 'entity_id', 'entity_name', 'candidate_count',
        'first_candidate_full_name', 'first_candidate_username', 'error_message', 'reason_for_no_validation'
    ]

    try:
        # --- Exemplos de Chamadas ---
        # Descomente e ajuste as chamadas que deseja testar

        # 1. Buscar perfil para uma entidade específica
        entity_type_to_test = "empresa"  # ou "pessoa", "advogado"
        entity_id_to_test = 30       # Substitua pelo ID real que deseja testar
        print(f"\n--- Testando find_profiles_for_entity ({entity_type_to_test}/{entity_id_to_test}) ---")
        result_single = await profile_finder.find_profiles_for_entity(entity_type_to_test, entity_id_to_test)
        print(json.dumps(result_single, indent=2, default=str)) # Usar json.dumps para melhor visualização

        # 2. Buscar perfis para todas as entidades de um tipo sem Instagram
        entity_type_all = "empresa" # ou "pessoa", "advogado"
        print(f"\n--- Testando find_profiles_for_all_entities ({entity_type_all}) ---")
        results_all = await profile_finder.find_profiles_for_all_entities(entity_type_all)
        print(f"Encontrados {len(results_all)} resultados para processamento.")
        
        # Processar resultados para os CSVs
        for res in results_all:
            entity_data = res.get('entity', {})
            candidates = res.get('candidates', [])
            validated_profile = res.get('validated_profile')
            error = res.get('error')

            # Obter o nome correto da entidade dependendo do tipo
            entity_name_for_csv = ''
            if entity_type_all == 'empresa':
                entity_name_for_csv = entity_data.get('nome_fantasia', '')
            elif entity_type_all in ['pessoa', 'advogado']:
                fname = entity_data.get('firstname', '')
                lname = entity_data.get('lastname', '')
                entity_name_for_csv = f"{fname} {lname}".strip()

            if validated_profile:
                row_found = {
                    'entity_type': entity_type_all,
                    'entity_id': entity_data.get('id', ''),
                    'entity_name': entity_name_for_csv, # Usar a variável correta
                    'validated_username': validated_profile.get('perfil', {}).get('username', ''),
                    'validated_full_name': validated_profile.get('perfil', {}).get('full_name', ''),
                    'validated_score': validated_profile.get('score', '')
                }
                csv_data_found.append(row_found)
            else:
                row_not_found = {
                    'entity_type': entity_type_all,
                    'entity_id': entity_data.get('id', ''),
                    'entity_name': entity_name_for_csv, # Usar a variável correta
                    'candidate_count': len(candidates),
                    'first_candidate_full_name': candidates[0].get('full_name', '') if candidates else None,
                    'first_candidate_username': candidates[0].get('username', '') if candidates else None,
                    'error_message': error,
                    'reason_for_no_validation': 'Erro no processamento' if error else (
                        'Sem candidatos da API' if not candidates else 'Nenhum candidato passou na validação'
                    )
                }
                csv_data_not_found.append(row_not_found)

        # Imprime apenas os primeiros N resultados para não poluir muito o terminal
        max_results_to_print = 2 # Reduzido para não poluir muito, já que salvaremos em CSV
        for i, res in enumerate(results_all):
            if i >= max_results_to_print:
                print(f"... (e mais {len(results_all) - max_results_to_print} resultados)")
                break
            print(json.dumps(res, indent=2, default=str)) 
            print("-" * 20)

        # 3. Buscar perfil para uma empresa e suas entidades relacionadas
        company_id_related_test = 30 # Substitua pelo ID real da empresa que deseja testar
        print(f"\n--- Testando find_profiles_for_company_and_related ({company_id_related_test}) ---")
        result_related = await profile_finder.find_profiles_for_company_and_related(company_id_related_test)
        print(json.dumps(result_related, indent=2, default=str))

        print("\n--- Fim dos testes ---")

    except Exception as e:
        print(f"\nOcorreu um erro durante a execução: {e}")
    finally:
        # Garante que os recursos sejam fechados (ex: conexões do validador se houver)
        print("\nFechando recursos...")
        # profile_finder.close() # close() foi removido do service
        print("Recursos fechados.")

    # Salvar resultados em CSV
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    base_path = os.path.dirname(__file__)

    if csv_data_found:
        csv_filename_found = f"found_results_{timestamp}.csv"
        csv_filepath_found = os.path.join(base_path, csv_filename_found)
        print(f"\nSalvando {len(csv_data_found)} resultados encontrados em {csv_filepath_found}...")
        try:
            with open(csv_filepath_found, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=csv_header_found)
                writer.writeheader()
                writer.writerows(csv_data_found)
            print("Resultados encontrados salvos com sucesso!")
        except Exception as e:
            print(f"Erro ao salvar CSV de encontrados: {e}")

    if csv_data_not_found:
        csv_filename_not_found = f"not_found_results_{timestamp}.csv"
        csv_filepath_not_found = os.path.join(base_path, csv_filename_not_found)
        print(f"\nSalvando {len(csv_data_not_found)} resultados não encontrados/erros em {csv_filepath_not_found}...")
        try:
            with open(csv_filepath_not_found, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=csv_header_not_found)
                writer.writeheader()
                writer.writerows(csv_data_not_found)
            print("Resultados não encontrados/erros salvos com sucesso!")
        except Exception as e:
            print(f"Erro ao salvar CSV de não encontrados/erros: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 