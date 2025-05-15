from src.services.profile_finder_service import ProfileFinderService
from src.repositories.hiker_repository import HikerRepository
from src.repositories.postgres_repository import PostgresRepository

# Estas instâncias poderiam ser gerenciadas de forma mais sofisticada
# com um container de injeção de dependência em projetos maiores,
# ou configuradas para serem criadas por request se necessário.
# Por simplicidade, vamos criar instâncias globais aqui.

# Assume que as variáveis de ambiente para os repositórios são carregadas
# quando ProfileFinderService é importado ou nos próprios repositórios.

hiker_repo = HikerRepository()
postgres_repo = PostgresRepository()

profile_finder_service_instance = ProfileFinderService(
    hiker_repository=hiker_repo,
    postgres_repository=postgres_repo
)

def get_profile_finder_service() -> ProfileFinderService:
    return profile_finder_service_instance 