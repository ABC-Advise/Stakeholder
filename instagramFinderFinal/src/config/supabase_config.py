from supabase import create_client, Client
from typing import Optional

# Configurações do Supabase
SUPABASE_URL = "https://hccolkrnyrxcbxuuajwq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhjY29sa3JueXJ4Y2J4dXVhandxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NjM4NzY5NSwiZXhwIjoyMDYxOTYzNjk1fQ.xroXGjcmzb6VqiGQJP68uxk_MMTAhdr8P1oi8HNXNRw"
SUPABASE_SCHEMA = "instagram_data"

# Cliente Supabase singleton
_supabase_client: Optional[Client] = None

def get_supabase_client() -> Client:
    """
    Retorna uma instância do cliente Supabase.
    Usa o padrão singleton para reutilizar a conexão.
    
    Returns:
        Client: Cliente Supabase configurado
    """
    global _supabase_client
    
    if _supabase_client is None:
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        # Configurar o schema padrão
        # _supabase_client.table("").select("*").execute()  # Força a conexão inicial
        
    return _supabase_client

def get_supabase_table(table_name: str):
    """
    Retorna uma referência para uma tabela específica do Supabase.
    
    Args:
        table_name (str): Nome da tabela
        
    Returns:
        Table: Referência para a tabela no Supabase
    """
    client = get_supabase_client()
    return client.table(table_name) 