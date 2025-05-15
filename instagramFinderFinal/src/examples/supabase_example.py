from src.config.supabase_config import get_supabase_table

async def exemplo_busca_dados():
    """
    Exemplo de como usar o cliente Supabase para buscar dados
    """
    # Obtém referência para uma tabela
    table = get_supabase_table("sua_tabela")
    
    # Exemplo de consulta
    response = await table.select("*").execute()
    
    # Exemplo de inserção
    data = {"campo1": "valor1", "campo2": "valor2"}
    response = await table.insert(data).execute()
    
    # Exemplo de atualização
    response = await table.update({"campo1": "novo_valor"}).eq("id", 1).execute()
    
    # Exemplo de deleção
    response = await table.delete().eq("id", 1).execute()

# Para usar em um endpoint FastAPI:
"""
from fastapi import APIRouter
from src.config.supabase_config import get_supabase_table

router = APIRouter()

@router.get("/dados")
async def get_dados():
    table = get_supabase_table("sua_tabela")
    response = await table.select("*").execute()
    return response.data
""" 