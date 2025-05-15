from supabase import create_client, Client, ClientOptions
from typing import Optional
from httpx import Timeout
import logging
import time
from functools import wraps

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Reduzir logs do httpx
logging.getLogger("httpx").setLevel(logging.WARNING)

# Configurações do Supabase
SUPABASE_URL = "https://hccolkrnyrxcbxuuajwq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhjY29sa3JueXJ4Y2J4dXVhandxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NjM4NzY5NSwiZXhwIjoyMDYxOTYzNjk1fQ.xroXGjcmzb6VqiGQJP68uxk_MMTAhdr8P1oi8HNXNRw"
SUPABASE_SCHEMA = "instagram_data"

# Cliente Supabase singleton
_supabase_client: Optional[Client] = None
_max_retries = 3
_retry_delay = 1  # segundos

def retry_on_error(max_retries=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        wait_time = delay * (2 ** attempt)  # Exponential backoff
                        logger.warning(f"Tentativa {attempt + 1} falhou: {str(e)}. Tentando novamente em {wait_time}s...")
                        time.sleep(wait_time)
            logger.error(f"Todas as tentativas falharam. Último erro: {str(last_error)}")
            raise last_error
        return wrapper
    return decorator

@retry_on_error(max_retries=_max_retries, delay=_retry_delay)
def get_supabase_client() -> Client:
    """
    Retorna uma instância do cliente Supabase.
    Usa o padrão singleton para reutilizar a conexão.
    Sempre utiliza o schema 'instagram_data'.
    
    Returns:
        Client: Cliente Supabase configurado
    """
    global _supabase_client
    
    if _supabase_client is None:
        logger.info("Inicializando cliente Supabase...")
        try:
            # Configuração de timeout mais longa (5 minutos)
            timeout = Timeout(300.0)
            
            # Opções do cliente com timeout e reconexão
            options = ClientOptions(
                schema=SUPABASE_SCHEMA,
                postgrest_client_timeout=timeout,
                auto_refresh_token=True,
                persist_session=True,
                headers={
                    "User-Agent": "InstagramFinder/1.0",
                    "X-Client-Info": "supabase-py/1.0"
                }
            )
            
            _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY, options=options)
            logger.info("Cliente Supabase inicializado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar cliente Supabase: {str(e)}")
            raise
    
    return _supabase_client

@retry_on_error(max_retries=_max_retries, delay=_retry_delay)
def get_supabase_table(table_name: str):
    """
    Retorna uma referência para uma tabela específica do Supabase.
    Sempre utiliza o schema 'instagram_data'.
    
    Args:
        table_name (str): Nome da tabela
        
    Returns:
        Table: Referência para a tabela no Supabase
    """
    try:
        client = get_supabase_client()
        return client.table(table_name)
    except Exception as e:
        logger.error(f"Erro ao obter tabela {table_name}: {str(e)}")
        raise 