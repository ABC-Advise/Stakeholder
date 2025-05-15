import sqlite3
from collections import deque
import os
import time
import multiprocessing
from multiprocessing import TimeoutError # Import specific exception
import csv # Adicionado para ler o CSV
import redis
from dataclasses import dataclass

# --- Início: Definição das Classes POO ---

@dataclass
class PathFinderConfig:
    db_path: str = '/Users/waltagan/coleta_instagram/instagram_collector.db'
    target_username: str = 'waltaganlopes'
    csv_path: str = 'stakeholders.csv'
    output_csv_path: str = 'perfis_com_caminhos.csv'
    max_search_depth: int = 3
    search_timeout_seconds: int = 2000 # Timeout por perfil (AUMENTADO)
    redis_host: str = 'localhost'
    redis_port: int = 6379
    redis_db: int = 0
    redis_connect_timeout: int = 2 # Segundos


class RedisManager:
    def __init__(self, host, port, db, connect_timeout=2):
        self.host = host
        self.port = port
        self.db = db
        self.connect_timeout = connect_timeout
        self.client = None
        self.is_available = False
        self._connect()

    def _connect(self):
        try:
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                socket_connect_timeout=self.connect_timeout
            )
            self.client.ping()
            self.is_available = True
            # print(f"[RedisManager] Conexão com Redis ({self.host}:{self.port}) estabelecida.")
        except Exception as e:
            self.is_available = False
            print(f"[RedisManager] [AVISO] Não foi possível conectar ao Redis ({self.host}:{self.port}): {e}")

    def get(self, key):
        if not self.is_available or self.client is None:
            return None
        try:
            return self.client.get(key)
        except Exception as e:
            print(f"[RedisManager] Erro ao GET do Redis: {e}")
            # Em caso de erro de comunicação durante a operação, pode-se tentar reconectar ou marcar como indisponível
            # self.is_available = False 
            return None

    def set(self, key, value):
        if not self.is_available or self.client is None:
            return False
        try:
            self.client.set(key, value)
            return True
        except Exception as e:
            print(f"[RedisManager] Erro ao SET no Redis: {e}")
            # self.is_available = False
            return False

class SQLiteManager:
    def __init__(self, db_path, redis_manager):
        self.db_path = db_path
        self.redis_manager = redis_manager
        self.conn = None # Conexão será gerenciada por método ou worker

    def _get_cursor(self):
        # Esta função é um placeholder. A conexão deve ser gerenciada
        # pelo worker que utiliza esta classe para garantir thread-safety
        # ou processo-safety.
        # No contexto atual, process_single_user criará sua própria conexão.
        # Esta classe SQLiteManager será instanciada DENTRO do worker,
        # com uma conexão já estabelecida.
        if self.conn is None:
            # Isso não deveria acontecer se o SQLiteManager for usado como planejado
            # (instanciado com uma conexão ativa pelo worker)
            raise Exception("Conexão SQLite não estabelecida antes de obter o cursor.")
        return self.conn.cursor()
    
    def set_connection(self, connection):
        """Permite que o worker defina a conexão SQLite a ser usada."""
        self.conn = connection

    def get_id_from_username(self, username):
        """Busca o ID de um perfil pelo username, usando cache Redis."""
        cache_key = f"username:{username}"
        if self.redis_manager and self.redis_manager.is_available:
            cached_value = self.redis_manager.get(cache_key)
            if cached_value is not None:
                try:
                    return int(cached_value)
                except ValueError:
                    pass # Ignora cache se não for int

        cursor = self._get_cursor()
        cursor.execute("SELECT id FROM perfis WHERE username = ?", (username,))
        result = cursor.fetchone()
        if result:
            user_id = result[0]
            if self.redis_manager and self.redis_manager.is_available:
                self.redis_manager.set(cache_key, user_id)
            return user_id
        return None

    def get_username_from_id(self, user_id):
        """Busca o username de um perfil pelo ID, usando cache Redis."""
        cache_key = f"id:{user_id}"
        if self.redis_manager and self.redis_manager.is_available:
            cached_value = self.redis_manager.get(cache_key)
            if cached_value is not None:
                return cached_value.decode() if isinstance(cached_value, (bytes, bytearray)) else str(cached_value)

        cursor = self._get_cursor()
        cursor.execute("SELECT username FROM perfis WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        if result:
            username_val = result[0]
            if self.redis_manager and self.redis_manager.is_available:
                self.redis_manager.set(cache_key, username_val)
            return username_val
        return None

    def find_all_paths_dfs_recursive(self, current_id, target_id, current_path, visited_in_path, all_paths, max_depth):
        """Função recursiva interna para DFS."""
        # current_path já inclui current_id devido à chamada inicial e appends.

        # 1. Se o nó atual é o alvo, o caminho até aqui é válido.
        if current_id == target_id:
            all_paths.append(list(current_path))
            # A condição de profundidade abaixo controlará a exploração adicional.
            # Se já estamos no alvo, este caminho está completo para esta profundidade.

        # 2. Se o comprimento do caminho atual (incluindo current_id) atingiu 
        #    ou excedeu a profundidade máxima de NÓS permitida, não explore mais a partir deste nó.
        if len(current_path) >= max_depth: # max_depth é o número máximo de NÓS no caminho
            return

        # Adiciona current_id ao conjunto de nós visitados NESTE RAMO da DFS
        # para evitar ciclos dentro deste caminho de exploração.
        visited_in_path.add(current_id)

        cursor = self._get_cursor()
        # MODIFICADO: Busca apenas quem o current_id SEGUE (Opção B)
        cursor.execute("""
            SELECT perfil_pai_id AS neighbor_id FROM seguidores WHERE perfil_filho_id = :current_id
        """, {"current_id": current_id})
        all_neighbor_tuples = cursor.fetchall()
        # print(f"[DFS {current_path[0]}->{target_id}] Para current_id: {current_id}, consulta SEGUE encontrou {len(all_neighbor_tuples)} vizinhos.")
        
        for neighbor_tuple in all_neighbor_tuples:
            neighbor_id = neighbor_tuple[0]
            # Só prossegue se o vizinho não foi visitado neste ramo da DFS
            if neighbor_id not in visited_in_path:
                current_path.append(neighbor_id)
                self.find_all_paths_dfs_recursive(neighbor_id, target_id, current_path, visited_in_path, all_paths, max_depth)
                current_path.pop() # Backtrack: remove o vizinho do caminho ao retornar da recursão
        
        # Remove o nó atual do conjunto de visitados deste ramo ao retroceder
        visited_in_path.remove(current_id)

# --- Fim: Definição das Classes POO ---

# --- Configuração (será substituída pela classe PathFinderConfig) ---
# DB_PATH = '/Users/waltagan/coleta_instagram/instagram_collector.db'
# TARGET_USERNAME = 'waltaganlopes'
# CSV_PATH = 'stakeholders.csv' 
# OUTPUT_CSV_PATH = 'perfis_com_caminhos.csv' 
# MAX_SEARCH_DEPTH = 4 
# SEARCH_TIMEOUT_SECONDS = 1000 
# REDIS_HOST = 'localhost'
# REDIS_PORT = 6379
# REDIS_DB = 0
# --- Fim da Configuração ---

# --- Conexão Global com Redis (REMOVIDA) ---
# try:
#     redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, socket_connect_timeout=2)
#     redis_client.ping()
#     redis_available = True
#     print("[Main] Conexão com Redis estabelecida com sucesso.")
# except Exception as e:
#     print(f"[Main] [AVISO] Não foi possível conectar ao Redis: {e}")
#     redis_available = False
# --- Fim Conexão Global Redis ---

# def get_id_from_username(cursor, username, redis_client=None): # MOVIDA para SQLiteManager
#     pass 

# def get_username_from_id(cursor, user_id, redis_client=None): # MOVIDA para SQLiteManager
#     pass

# def find_all_paths_dfs_recursive(cursor, current_id, target_id, current_path, visited_in_path, all_paths, max_depth): # MOVIDA para SQLiteManager
#     pass


class PathSearchWorker:
    def __init__(self, start_username, target_username, config):
        self.start_username = start_username
        self.target_username = target_username
        self.config = config
        self.sqlite_conn = None
        self.redis_manager = None
        self.sqlite_manager = None

    def _initialize_resources(self):
        """Inicializa conexões e managers para este worker."""
        self.redis_manager = RedisManager(
            host=self.config.redis_host,
            port=self.config.redis_port,
            db=self.config.redis_db,
            connect_timeout=self.config.redis_connect_timeout
        )
        if self.redis_manager.is_available:
             print(f"[Worker: {self.start_username}] Conexão com Redis estabelecida com sucesso.")
        else:
             print(f"[Worker: {self.start_username}] [AVISO] Não foi possível conectar ao Redis.")

        self.sqlite_conn = sqlite3.connect(self.config.db_path)
        self.sqlite_manager = SQLiteManager(self.config.db_path, self.redis_manager)
        self.sqlite_manager.set_connection(self.sqlite_conn) # Passa a conexão ativa

    def _close_resources(self):
        if self.sqlite_conn:
            self.sqlite_conn.close()
        # O cliente Redis no RedisManager não precisa ser explicitamente fechado aqui,
        # pois as conexões são geralmente gerenciadas pelo pool de conexões do redis-py.

    def run(self):
        """
        Executa a busca de caminhos para o usuário inicial.
        Retorna (username, lista_de_caminhos, erro)
        """
        start_time = time.time()
        try:
            self._initialize_resources()
            
            if not self.sqlite_manager: # Checagem de segurança
                return self.start_username, None, "SQLiteManager não inicializado."

            target_id = self.sqlite_manager.get_id_from_username(self.target_username)
            if not target_id:
                return self.start_username, None, f"Usuário alvo '{self.target_username}' não encontrado no DB."

            start_id = self.sqlite_manager.get_id_from_username(self.start_username)
            if not start_id:
                return self.start_username, None, f"Usuário inicial '{self.start_username}' não encontrado no DB."

            print(f"[Worker: {self.start_username}] Iniciando find_all_paths_dfs_recursive para start_id: {start_id}, target_id: {target_id}, profundidade: {self.config.max_search_depth}") # LOG ADICIONAL
            all_found_paths_ids = []
            initial_visited = set()
            # A função recursiva agora é um método de SQLiteManager
            self.sqlite_manager.find_all_paths_dfs_recursive(
                start_id, target_id, [start_id], initial_visited, all_found_paths_ids, self.config.max_search_depth
            )
            print(f"[Worker: {self.start_username}] Concluído find_all_paths_dfs_recursive. Encontrados {len(all_found_paths_ids)} caminhos ID.") # LOG ADICIONAL

            all_found_paths_usernames = []
            if all_found_paths_ids:
                username_cache = {} # Cache local simples para usernames dentro do processamento deste worker
                for path_ids in all_found_paths_ids:
                    path_usernames = []
                    for user_id in path_ids:
                        if user_id in username_cache:
                            username = username_cache[user_id]
                        else:
                            username = self.sqlite_manager.get_username_from_id(user_id)
                            if username:
                                username_cache[user_id] = username
                        path_usernames.append(username)
                    
                    valid_path = [name for name in path_usernames if name]
                    if len(valid_path) == len(path_ids):
                        all_found_paths_usernames.append(valid_path)
            
            # print(f"[Worker: {self.start_username}] Processamento levou {time.time() - start_time:.2f}s")
            return self.start_username, all_found_paths_usernames, None

        except sqlite3.Error as e:
            return self.start_username, None, f"Erro de banco de dados ao processar '{self.start_username}': {e}"
        except Exception as e:
            # Captura mais ampla para incluir possíveis erros de inicialização de recursos
            import traceback
            tb_str = traceback.format_exc()
            return self.start_username, None, f"Erro inesperado no worker para '{self.start_username}': {e}\n{tb_str}"
        finally:
            self._close_resources()

def process_single_user_wrapper(start_username, target_username, config_dict):
    """
    Wrapper para ser usado com multiprocessing.Pool.
    Cria uma instância de PathFinderConfig a partir do dict e executa o worker.
    """
    # Recria a config no processo filho para evitar problemas de serialização de objetos complexos
    config = PathFinderConfig(**config_dict)
    worker = PathSearchWorker(start_username, target_username, config)
    return worker.run()


# def process_single_user(args): # SUBSTITUÍDA por PathSearchWorker e wrapper
#     pass

def load_profiles_from_csv(csv_path):
    """Carrega perfis do arquivo CSV, retornando cabeçalho e dados completos."""
    all_data = []
    header = []
    if not os.path.exists(csv_path):
        print(f"Erro: Arquivo CSV não encontrado em {csv_path}")
        return None, None

    try:
        with open(csv_path, mode='r', encoding='latin-1') as infile:
            reader = csv.DictReader(infile, delimiter=',')
            header = reader.fieldnames 
            if not header:
                 print(f"Erro: CSV '{csv_path}' está vazio ou não tem cabeçalho.")
                 return None, None
            
            instagram_col_found = any(h.strip().lower() == 'instagram' for h in header)
            if not instagram_col_found:
                print(f"Erro: A coluna 'Instagram' não foi encontrada no cabeçalho do CSV: {header}")
                return None, None

            for row in reader:
                all_data.append(row)

        return header, all_data

    except FileNotFoundError:
        print(f"Erro: Arquivo CSV não encontrado em {csv_path}")
        return None, None
    except UnicodeDecodeError:
        print(f"Erro de Decodificação: Não foi possível ler o arquivo '{csv_path}'. Verifique a codificação do arquivo.")
        return None, None
    except Exception as e:
        print(f"Erro ao ler o arquivo CSV '{csv_path}': {e}")
        return None, None

def format_paths_for_csv(paths):
    """Formata a lista de caminhos para uma string única para o CSV."""
    if not paths:
        return ""
    return '; '.join([' -> '.join(path) for path in paths])

def main():
    config = PathFinderConfig() # Usa valores padrão ou pode ser carregado de arquivo/env vars

    print(f"--- Iniciando Busca de Caminhos e Geração de CSV ---")
    print(f"Banco de Dados: {config.db_path}")
    print(f"Arquivo de Entrada: {config.csv_path}")
    print(f"Arquivo de Saída: {config.output_csv_path}")
    print(f"Usuário Alvo: {config.target_username}")
    print(f"Profundidade Máxima: {config.max_search_depth}")
    print(f"Timeout por Perfil: {config.search_timeout_seconds} segundos")
    print(f"Redis: {config.redis_host}:{config.redis_port}, DB {config.redis_db}")

    if not os.path.exists(config.db_path):
        print(f"Erro Crítico: Banco de dados não encontrado em {config.db_path}. Abortando.")
        return

    # Teste inicial de conexão Redis no processo principal (opcional, mas bom para feedback rápido)
    main_redis_manager = RedisManager(config.redis_host, config.redis_port, config.redis_db, config.redis_connect_timeout)
    if main_redis_manager.is_available:
        print("[Main] Conexão principal com Redis verificada.")
    else:
        print("[Main] [AVISO] Não foi possível conectar ao Redis a partir do processo principal.")


    original_header, all_profile_data = load_profiles_from_csv(config.csv_path)
    if not all_profile_data:
        print("Erro ao carregar perfis ou CSV vazio. Verifique o arquivo e tente novamente.")
        return

    instagram_col_name = next((h for h in original_header if h.strip().lower() == 'instagram'), None)
    if not instagram_col_name:
         print("Erro interno: não foi possível reconfirmar o nome da coluna Instagram.")
         return
    
    profiles_to_process = [profile for profile in all_profile_data if profile.get(instagram_col_name)]

    if not profiles_to_process:
        print("Nenhum perfil com username válido encontrado no CSV para processar.")
        return

    print(f"Encontrados {len(profiles_to_process)} perfis com username no CSV para processar.")
    start_overall_time = time.time()
    results = {} 
    timeout_occurred = False
    
    # Converte config para dict para passar para o wrapper, pois objetos podem ser problemáticos com multiprocessing
    config_dict = config.__dict__
    tasks = [(profile[instagram_col_name], config.target_username, config_dict) for profile in profiles_to_process]

    num_workers = os.cpu_count()
    print(f"Iniciando processamento paralelo com {num_workers} workers...")

    # Usar with para garantir que o pool seja fechado corretamente
    with multiprocessing.Pool(processes=num_workers) as pool:
        async_results = []
        for task_args in tasks:
            # O wrapper agora lida com a instanciação do worker e da config
            async_results.append(pool.apply_async(process_single_user_wrapper, args=task_args))

        print(f"Aguardando resultados para {len(tasks)} perfis (timeout individual: {config.search_timeout_seconds}s)...")
        processed_count = 0
        for i, res in enumerate(async_results):
            current_task_args = tasks[i] # tasks[i] é uma tupla (start_username, target_username, config_dict)
            print(f"\n[Main] Aguardando resultado para: {current_task_args[0]} (índice {i}, {processed_count + 1}/{len(tasks)})...") # LOG ADICIONAL
            try:
                # O timeout é aplicado ao res.get()
                username, paths, error = res.get(timeout=config.search_timeout_seconds)
                results[username] = {'paths': paths, 'error': error}
                if error:
                    print(f"\n[Main] Erro retornado para '{username}': {error}")
                processed_count += 1
                # Atualiza o progresso na mesma linha
                print(f"\rProgresso: {processed_count}/{len(tasks)} perfis processados...", end="")

            except TimeoutError:
                timed_out_username = current_task_args[0] # tasks[i] é uma tupla (start_username, target_username, config_dict)
                print(f"\n!!! ATENÇÃO: Timeout de {config.search_timeout_seconds}s excedido ao processar '{timed_out_username}'. Marcando erro.")
                results[timed_out_username] = {'paths': None, 'error': f'Timeout de {config.search_timeout_seconds}s excedido.'}
                timeout_occurred = True
            except Exception as e:
                failed_username = current_task_args[0]
                print(f"\n!!! Erro inesperado ao obter resultado para '{failed_username}': {e}. Marcando erro.")
                results[failed_username] = {'paths': None, 'error': f'Erro inesperado no worker controller: {e}'}
                timeout_occurred = True
        print() # Nova linha após a barra de progresso

    # Geração do CSV de Saída
    print(f"\nGerando arquivo de saída: {config.output_csv_path}")
    new_column_name = 'Caminhos_Encontrados'
    # Adiciona a nova coluna ao cabeçalho original se ainda não existir (improvável aqui, mas seguro)
    output_header = list(original_header) # Cria cópia
    if new_column_name not in output_header:
        output_header.append(new_column_name)
        
    output_data = []

    for original_row in all_profile_data:
        output_row = original_row.copy()
        username_key = original_row.get(instagram_col_name) # Username do stakeholder processado
        paths_string = ""

        if username_key: # Se o stakeholder tinha um username para processar
            result_data = results.get(username_key) # Busca o resultado pelo username do stakeholder
            if not result_data:
                # Isso pode acontecer se o username do stakeholder não estava em profiles_to_process
                # ou se houve algum problema não capturado que impediu a entrada no dict results.
                paths_string = "Processamento não iniciado ou falhou (resultado não encontrado)"
            elif result_data['error']:
                paths_string = f"Erro: {result_data['error']}"
            elif result_data['paths'] is not None and result_data['paths']: # Caminhos encontrados
                paths_string = format_paths_for_csv(result_data['paths'])
            elif result_data['paths'] is not None: # Lista de caminhos explicitamente vazia, sem erro
                paths_string = f"Nenhum caminho encontrado (profundidade {config.max_search_depth})"
            else: # result_data['paths'] é None, mas não há erro (pode indicar um estado não previsto)
                paths_string = "Status inesperado no resultado (caminhos são None sem erro)"
        else:
            paths_string = "Username não fornecido no CSV"

        output_row[new_column_name] = paths_string
        output_data.append(output_row)

    try:
        with open(config.output_csv_path, mode='w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=output_header, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(output_data)
        print(f"Arquivo '{config.output_csv_path}' gerado com sucesso.")
    except Exception as e:
        print(f"\nErro Crítico: Não foi possível escrever o arquivo de saída '{config.output_csv_path}': {e}")

    if timeout_occurred:
        print("\nAVISO: O processamento foi concluído, mas ocorreram timeouts ou erros para um ou mais perfis. Verifique a coluna 'Caminhos_Encontrados' no CSV.")

    end_overall_time = time.time()
    print(f"\nTempo total de execução: {end_overall_time - start_overall_time:.2f} segundos.")
    print("--- Fim da Execução ---")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()