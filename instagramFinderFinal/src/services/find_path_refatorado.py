from collections import deque
import os
import time
import multiprocessing
from dataclasses import dataclass
from src.config.supabase_config import get_supabase_table
from dotenv import load_dotenv
from src.services.redis_manager import RedisManager
import concurrent.futures

load_dotenv()

@dataclass
class PathFinderConfig:
    db_path: str = os.getenv('DB_PATH', '/Users/waltagan/coleta_instagram/instagram_collector.db')
    target_username: str = os.getenv('TARGET_USERNAME', 'waltaganlopes')
    csv_path: str = os.getenv('CSV_PATH', 'stakeholders.csv')
    output_csv_path: str = os.getenv('OUTPUT_CSV_PATH', 'perfis_com_caminhos.csv')
    max_search_depth: int = int(os.getenv('MAX_SEARCH_DEPTH', 3))
    search_timeout_seconds: int = int(os.getenv('SEARCH_TIMEOUT_SECONDS', 2000))
    redis_host: str = os.getenv('REDIS_HOST', 'localhost')
    redis_port: int = int(os.getenv('REDIS_PORT', 6379))
    redis_db: int = int(os.getenv('REDIS_DB', 0))
    redis_password: str = os.getenv('REDIS_PASSWORD', None)
    redis_connect_timeout: int = int(os.getenv('REDIS_CONNECT_TIMEOUT', 2))

class SupabaseManager:
    def __init__(self, redis_manager=None):
        self.redis_manager = redis_manager
        self.table_perfis = get_supabase_table("perfis")
        self.table_seguidores = get_supabase_table("seguidores")
        self._neighbors_cache = {}  # Cache em memória para vizinhos
        self._batch_size = 100  # Tamanho do lote para busca de vizinhos

    def get_id_from_username(self, username):
        max_retries = 3
        retry_delay = 1  # segundos
        
        for attempt in range(max_retries):
            try:
                response = self.table_perfis.select("id").eq("username", username).execute()
                if response.data:
                    return response.data[0]["id"]
                return None
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"Erro ao buscar ID para username {username} (tentativa {attempt + 1}/{max_retries}): {str(e)}")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    print(f"Erro final ao buscar ID para username {username}: {str(e)}")
                    return None

    def get_username_from_id(self, user_id):
        max_retries = 3
        retry_delay = 1  # segundos
        
        for attempt in range(max_retries):
            try:
                response = self.table_perfis.select("username").eq("id", user_id).execute()
                if response.data:
                    return response.data[0]["username"]
                return None
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"Erro ao buscar username para ID {user_id} (tentativa {attempt + 1}/{max_retries}): {str(e)}")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    print(f"Erro final ao buscar username para ID {user_id}: {str(e)}")
                    return None

    def get_neighbors(self, current_id):
        # Verifica cache primeiro
        if current_id in self._neighbors_cache:
            return self._neighbors_cache[current_id]

        max_retries = 3
        retry_delay = 1  # segundos
        
        for attempt in range(max_retries):
            try:
                # Busca todos os perfis que o current_id segue (perfil_pai_id)
                response = self.table_seguidores.select("perfil_pai_id").eq("perfil_filho_id", current_id).execute()
                
                if response.data:
                    neighbors = [row["perfil_pai_id"] for row in response.data]
                    # Armazena no cache
                    self._neighbors_cache[current_id] = neighbors
                    return neighbors
                return []
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"Erro ao buscar vizinhos para {current_id} (tentativa {attempt + 1}/{max_retries}): {str(e)}")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    print(f"Erro final ao buscar vizinhos para {current_id}: {str(e)}")
                    return []

    def get_neighbors_batch(self, ids):
        """
        Busca vizinhos para múltiplos IDs de uma vez.
        """
        if not ids:
            return {}

        # Verifica cache primeiro
        cached_results = {}
        ids_to_fetch = []
        for id in ids:
            if id in self._neighbors_cache:
                cached_results[id] = self._neighbors_cache[id]
            else:
                ids_to_fetch.append(id)

        if not ids_to_fetch:
            return cached_results

        max_retries = 3
        retry_delay = 1  # segundos
        
        for attempt in range(max_retries):
            try:
                # Busca todos os seguidores para os IDs fornecidos
                response = self.table_seguidores.select("perfil_filho_id,perfil_pai_id").in_("perfil_filho_id", ids_to_fetch).execute()
                
                if response.data:
                    # Organiza os resultados por ID
                    neighbors_by_id = {}
                    for row in response.data:
                        child_id = row["perfil_filho_id"]
                        parent_id = row["perfil_pai_id"]
                        if child_id not in neighbors_by_id:
                            neighbors_by_id[child_id] = []
                        neighbors_by_id[child_id].append(parent_id)
                    
                    # Atualiza o cache
                    self._neighbors_cache.update(neighbors_by_id)
                    cached_results.update(neighbors_by_id)
                    return cached_results
                return cached_results
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"Erro ao buscar vizinhos em lote (tentativa {attempt + 1}/{max_retries}): {str(e)}")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    print(f"Erro final ao buscar vizinhos em lote: {str(e)}")
                    return cached_results

    def level_parallel_bfs(self, start_id, target_id, max_depth=5, num_processes=None):
        """
        Implementa BFS paralela por nível para encontrar todos os caminhos mais curtos.
        Args:
            start_id: ID do nó inicial
            target_id: ID do nó alvo
            max_depth: Profundidade máxima da busca
            num_processes: Número de threads para paralelização (default: número de CPUs)
        Returns:
            Lista de caminhos encontrados
        """
        if num_processes is None:
            num_processes = os.cpu_count()

        print(f"Iniciando BFS paralela por nível com {num_processes} threads...")
        start_time = time.time()

        queue = deque([(start_id, [start_id])])  # (node, path)
        visited = {start_id}
        found_paths = []
        current_level = 0
        total_requests = 0

        while queue and current_level < max_depth:
            current_level += 1
            level_nodes = []
            level_paths = []

            # Coleta todos os nós do nível atual
            while queue and len(level_nodes) < num_processes:
                node, path = queue.popleft()
                level_nodes.append(node)
                level_paths.append(path)

            if not level_nodes:
                break

            # Função para processar um nó do nível atual
            def process_node(node_path):
                node, path = node_path
                if node == target_id:
                    return [path]
                neighbors = self.get_neighbors_batch([node]).get(node, [])
                new_paths = []
                for neighbor in neighbors:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        new_paths.append((neighbor, path + [neighbor]))
                return new_paths

            # Processa os nós do nível atual em paralelo (threads)
            with concurrent.futures.ThreadPoolExecutor(max_workers=num_processes) as executor:
                results = list(executor.map(process_node, zip(level_nodes, level_paths)))

            # Atualiza a fila com os novos caminhos
            for new_paths in results:
                for new_path in new_paths:
                    if new_path[-1] == target_id:
                        found_paths.append(new_path)
                    else:
                        queue.append((new_path[-1], new_path))

            print(f"Nível {current_level}: {len(level_nodes)} nós processados, {len(found_paths)} caminhos encontrados")

        end_time = time.time()
        print(f"BFS paralela concluída em {end_time - start_time:.2f} segundos")
        print(f"Total de caminhos encontrados: {len(found_paths)}")
        print(f"Total de requisições ao Supabase: {total_requests}")

        return found_paths

    def find_all_paths_dfs_recursive(self, current_id, target_id, current_path, visited_in_path, all_paths, max_depth):
        if current_id == target_id:
            all_paths.append(list(current_path))
        if len(current_path) >= max_depth:
            return
        visited_in_path.add(current_id)
        neighbors = self.get_neighbors(current_id)
        for neighbor_id in neighbors:
            if neighbor_id not in visited_in_path:
                current_path.append(neighbor_id)
                self.find_all_paths_dfs_recursive(neighbor_id, target_id, current_path, visited_in_path, all_paths, max_depth)
                current_path.pop()
        visited_in_path.remove(current_id)

    def find_all_shortest_paths_bfs(self, start_id, target_id, max_depth=5):
        queue = deque()
        queue.append([start_id])
        found_paths = []
        visited_at_level = {start_id: 0}
        min_length = None

        while queue:
            path = queue.popleft()
            current_id = path[-1]

            # Se já passamos do menor caminho encontrado, pare
            if min_length is not None and len(path) > min_length:
                break

            if current_id == target_id:
                if min_length is None:
                    min_length = len(path)
                found_paths.append(list(path))
                continue

            if len(path) >= max_depth:
                continue

            neighbors = self.get_neighbors(current_id)
            for neighbor in neighbors:
                if neighbor not in path:  # Evita ciclos
                    # Só expande se não visitou esse nó em um caminho mais curto
                    if neighbor not in visited_at_level or visited_at_level[neighbor] >= len(path) + 1:
                        visited_at_level[neighbor] = len(path) + 1
                        queue.append(path + [neighbor])

        return found_paths

class PathSearchWorker:
    def __init__(self, start_username, target_username, config):
        self.start_username = start_username
        self.target_username = target_username
        self.config = config
        self.redis_manager = None
        self.supabase_manager = None

    def _initialize_resources(self):
        """Inicializa conexões e managers para este worker."""
        self.redis_manager = RedisManager(
            host=self.config.redis_host,
            port=self.config.redis_port,
            db=self.config.redis_db,
            connect_timeout=self.config.redis_connect_timeout,
            password=self.config.redis_password
        )
        if self.redis_manager.is_available:
             print(f"[Worker: {self.start_username}] Conexão com Redis estabelecida com sucesso.")
        else:
             print(f"[Worker: {self.start_username}] [AVISO] Não foi possível conectar ao Redis.")

        self.supabase_manager = SupabaseManager(self.redis_manager)

    def _close_resources(self):
        # Não há recursos explícitos para fechar no SupabaseManager
        pass

    def run(self):
        """
        Executa a busca de caminhos para o usuário inicial.
        Retorna (username, lista_de_caminhos, erro)
        """
        start_time = time.time()
        try:
            self._initialize_resources()
            
            if not self.supabase_manager: # Checagem de segurança
                return self.start_username, None, "SupabaseManager não inicializado."

            # Busca IDs
            start_id = self.supabase_manager.get_id_from_username(self.start_username)
            target_id = self.supabase_manager.get_id_from_username(self.target_username)

            if not start_id or not target_id:
                return self.start_username, None, "Usuário(s) não encontrado(s)."

            # Busca caminhos
            paths = self.supabase_manager.level_parallel_bfs(
                start_id, 
                target_id, 
                max_depth=self.config.max_search_depth
            )

            end_time = time.time()
            print(f"Busca concluída em {end_time - start_time:.2f} segundos")
            
            return self.start_username, paths, None

        except Exception as e:
            print(f"Erro ao processar {self.start_username}: {str(e)}")
            return self.start_username, None, str(e)
        finally:
            self._close_resources()

def process_single_user_wrapper(start_username, target_username, config_dict):
    """Wrapper para processar um único usuário em um processo separado."""
    config = PathFinderConfig(**config_dict)
    worker = PathSearchWorker(start_username, target_username, config)
    return worker.run()

def load_profiles_from_csv(csv_path):
    """Carrega perfis do arquivo CSV."""
    import csv
    profiles = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            profiles.append(row)
    return profiles

def format_paths_for_csv(paths):
    """Formata caminhos para o arquivo CSV."""
    return [','.join(map(str, path)) for path in paths]

def main():
    """Função principal para execução do script."""
    config = PathFinderConfig()
    profiles = load_profiles_from_csv(config.csv_path)
    
    results = []
    for profile in profiles:
        username = profile.get('username')
        if username:
            result = process_single_user_wrapper(username, config.target_username, config.__dict__)
            results.append(result)
    
    # Salva resultados
    with open(config.output_csv_path, 'w') as f:
        f.write("username,caminhos,erro\n")
        for username, paths, error in results:
            if paths:
                paths_str = ';'.join(format_paths_for_csv(paths))
            else:
                paths_str = ''
            f.write(f"{username},{paths_str},{error or ''}\n")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()