from src.config.supabase_config import get_supabase_table, SUPABASE_SCHEMA, get_supabase_client

def listar_tabelas():
    """
    Lista todas as tabelas disponíveis no Supabase
    """
    print("\n📊 Listando tabelas do Supabase:")
    print(f"Schema atual: {SUPABASE_SCHEMA}")
    
    # Lista de tabelas conhecidas para testar
    tabelas_conhecidas = [
        "test_perfis",
        "test_seguidores",
        "metricas_post",
        "vector_news",
        "noticias_coreia",
        "documents"
    ]
    
    print("\n📋 Testando tabelas conhecidas:")
    for tabela in tabelas_conhecidas:
        try:
            table = get_supabase_table(tabela)
            # Tenta fazer uma consulta simples para verificar se a tabela existe
            response = table.select("count").limit(1).execute()
            print(f"✅ Tabela '{tabela}' existe e está acessível")
            
            # Tenta listar as primeiras linhas para ver a estrutura
            sample = table.select("*").limit(1).execute()
            if sample.data:
                print(f"   Colunas disponíveis: {list(sample.data[0].keys())}")
            else:
                print(f"   Tabela vazia")
                
        except Exception as e:
            print(f"❌ Tabela '{tabela}' não existe ou não está acessível: {str(e)}")

def buscar_id_por_username_supabase(username):
    print(f"\n🔍 Buscando username: {username}")
    print(f"📊 Schema: {SUPABASE_SCHEMA}")
    
    # Primeiro, vamos verificar na tabela test_perfis
    print("\n📋 Verificando tabela test_perfis:")
    table_perfis = get_supabase_table("test_perfis")
    
    # Contar total de registros
    count = table_perfis.select("count").execute()
    print(f"   Total de registros: {count.data[0]['count'] if count.data else 0}")
    
    # Ver alguns exemplos
    print("\n📝 Exemplos de usernames na tabela test_perfis:")
    sample = table_perfis.select("username").limit(5).execute()
    if sample.data:
        print("   Primeiros 5 usernames:")
        for row in sample.data:
            print(f"   - {row['username']}")
    
    # Busca exata em test_perfis
    print(f"\n🔎 Buscando username exato em test_perfis: {username}")
    response = table_perfis.select("id, username").eq("username", username).execute()
    print(f"📥 Resposta completa: {response.data}")
    
    if response.data:
        return response.data[0]["id"]
    
    # Se não encontrou em test_perfis, vamos verificar em test_seguidores
    print("\n📋 Verificando tabela test_seguidores:")
    table_seguidores = get_supabase_table("test_seguidores")
    
    # Contar total de registros
    count = table_seguidores.select("count").execute()
    print(f"   Total de registros: {count.data[0]['count'] if count.data else 0}")
    
    # Ver alguns exemplos
    print("\n📝 Exemplos de usernames na tabela test_seguidores:")
    sample = table_seguidores.select("username_pai, username_filho").limit(5).execute()
    if sample.data:
        print("   Primeiros 5 registros:")
        for row in sample.data:
            print(f"   - Pai: {row['username_pai']}, Filho: {row['username_filho']}")
    
    # Busca em test_seguidores
    print(f"\n🔎 Buscando username em test_seguidores: {username}")
    response = table_seguidores.select("id, username_pai, username_filho").or_(f"username_pai.eq.{username},username_filho.eq.{username}").execute()
    print(f"📥 Resposta completa: {response.data}")
    
    if response.data:
        print("\n⚠️ Usuário encontrado na tabela test_seguidores!")
        return response.data[0]["id"]
    
    return None

if __name__ == "__main__":
    # Primeiro, vamos listar todas as tabelas
    listar_tabelas()
    
    # Depois, tentamos buscar o usuário
    username = "alexandrebononi"
    id_encontrado = buscar_id_por_username_supabase(username)
    print(f"\n✅ ID encontrado: {id_encontrado}")