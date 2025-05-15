import os
import time
from dotenv import load_dotenv
from src.config.supabase_config import get_supabase_table
from src.services.find_path_refatorado import SupabaseManager, RedisManager

load_dotenv()

def test_parallel_bfs():
    # Inicializa o Redis Manager
    redis_manager = RedisManager(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        db=int(os.getenv('REDIS_DB', 0)),
        password=os.getenv('REDIS_PASSWORD', None)
    )

    # Inicializa o Supabase Manager
    supabase_manager = SupabaseManager(redis_manager)

    # Exemplo de busca
    start_username = "waltaganlopes"
    target_username = "alexandrebononi"

    print(f"Buscando caminhos entre {start_username} e {target_username}...")

    # Obtém os IDs dos usuários
    start_id = supabase_manager.get_id_from_username(start_username)
    target_id = supabase_manager.get_id_from_username(target_username)

    if not start_id or not target_id:
        print("Erro: Não foi possível encontrar os IDs dos usuários.")
        return

    print(f"Usuário origem: {start_username} (id: {start_id})")
    print(f"Usuário alvo: {target_username} (id: {target_id})")

    # Executa a BFS paralela
    start_time = time.time()
    paths = supabase_manager.level_parallel_bfs(
        start_id=start_id,
        target_id=target_id,
        max_depth=4,
        num_processes=4  # Ajuste conforme o número de CPUs disponíveis
    )
    end_time = time.time()

    # Exibe os resultados
    print("\n--- Resultados da BFS Paralela ---")
    print(f"Tempo total: {end_time - start_time:.2f} segundos")
    print(f"Total de caminhos encontrados: {len(paths)}")
    
    if paths:
        print("\nCaminhos encontrados:")
        for path in paths:
            # Converte IDs para usernames
            path_usernames = []
            for user_id in path:
                username = supabase_manager.get_username_from_id(user_id)
                path_usernames.append(username if username else f"ID:{user_id}")
            print(" -> ".join(path_usernames))
    else:
        print("Nenhum caminho encontrado.")

if __name__ == "__main__":
    test_parallel_bfs() 