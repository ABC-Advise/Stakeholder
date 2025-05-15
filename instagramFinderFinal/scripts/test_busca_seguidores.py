import asyncio
from src.repositories.hiker_repository import HikerRepository
from src.services.profile_finder_service import ProfileFinderService
from src.repositories.postgres_repository import PostgresRepository

async def main():
    hiker_repo = HikerRepository()
    postgres_repo = PostgresRepository()
    service = ProfileFinderService(hiker_repo, postgres_repo)

    target_username = 'victordavi_oc'
    names_to_find = ["Julia Cunha", "Susanna Cunha"]
    similarity_threshold = 0.8

    resultado = await service.find_names_in_followers(
        target_username=target_username,
        names_to_find=names_to_find,
        similarity_threshold=similarity_threshold
    )

    print("\n==== RESULTADO DO TESTE ====")
    print(f"Total de seguidores processados: {resultado.get('total_followers')}")
    print("Nomes encontrados:")
    for match in resultado.get('found_names', []):
        print(f"- Procurado: {match['searched_name']} | Encontrado: {match['matched_name']} | Usuário: {match['username']} | Similaridade: {match['similarity']}%")
    if resultado.get('error'):
        print(f"Erro: {resultado['error']}")

if __name__ == "__main__":
    asyncio.run(main()) 