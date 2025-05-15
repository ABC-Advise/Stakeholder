import asyncio
from src.config.supabase_config import get_supabase_client, get_supabase_table

async def test_connection():
    """
    Testa a conexão com o Supabase e faz uma consulta básica
    """
    try:
        print("🔄 Testando conexão com Supabase...")
        
        # Testa a conexão básica
        client = get_supabase_client()
        print("✅ Cliente Supabase criado com sucesso!")
        
        # Tenta fazer uma consulta simples em uma tabela específica
        print("\n🔍 Testando consulta na tabela 'test_perfis'...")
        table = get_supabase_table("test_perfis")
        response = await table.select("*").limit(1).execute()
        print(f"Dados encontrados: {response.data}")
        
        print("\n✨ Teste concluído com sucesso!")
        
    except Exception as e:
        print(f"\n❌ Erro ao testar conexão: {str(e)}")
        print("\nDetalhes do erro:")
        print(f"Tipo do erro: {type(e).__name__}")
        print(f"Mensagem: {str(e)}")
        raise e

if __name__ == "__main__":
    # Executa o teste
    asyncio.run(test_connection()) 