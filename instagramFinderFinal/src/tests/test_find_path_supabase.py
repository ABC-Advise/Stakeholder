from src.config.supabase_config import get_supabase_table, SUPABASE_SCHEMA, get_supabase_client

def listar_tabelas():
    """
    Lista todas as tabelas disponíveis no Supabase
    """
    print("\n📊 Listando tabelas do Supabase:")
    print(f"Schema atual: {SUPABASE_SCHEMA}")
    
    # Lista de tabelas conhecidas para testar
    tabelas_conhecidas = [
        "perfis",
        "seguidores"
    ]
    
    print("\n📋 Testando tabelas conhecidas:")
    for tabela in tabelas_conhecidas:
        try:
            table = get_supabase_table(tabela)
            # Consulta limitada para evitar timeout
            sample = table.select("*").limit(5).execute()
            if sample.data:
                print(f"✅ Tabela '{tabela}' existe e está acessível. Exemplo de dados: {sample.data}")
            else:
                print(f"✅ Tabela '{tabela}' existe, mas está vazia ou não retornou dados.")
        except Exception as e:
            print(f"❌ Tabela '{tabela}' não existe ou não está acessível: {str(e)}")

def buscar_id_por_username_supabase(username):
    print(f"\n🔍 Buscando username: {username}")
    print(f"📊 Schema: {SUPABASE_SCHEMA}")
    
    # Primeiro, vamos verificar na tabela perfis
    print("\n📋 Verificando tabela perfis:")
    table_perfis = get_supabase_table("perfis")
    
    # Ver alguns exemplos (limitado)
    print("\n📝 Exemplos de usernames na tabela perfis:")
    sample = table_perfis.select("username").limit(5).execute()
    if sample.data:
        print("   Primeiros 5 usernames:")
        for row in sample.data:
            print(f"   - {row['username']}")
    else:
        print("   Nenhum username encontrado ou erro na consulta.")
    
    # Busca exata em perfis
    print(f"\n🔎 Buscando username exato em perfis: {username}")
    response = table_perfis.select("id, username").eq("username", username).limit(5).execute()
    print(f"📥 Resposta completa: {response.data}")
    
    if response.data:
        return response.data[0]["id"]
    
    # Se não encontrou em perfis, vamos verificar em seguidores
    print("\n📋 Verificando tabela seguidores:")
    table_seguidores = get_supabase_table("seguidores")
    
    # Ver alguns exemplos (limitado)
    print("\n📝 Exemplos de usernames na tabela seguidores:")
    sample = table_seguidores.select("username_pai, username_filho").limit(5).execute()
    if sample.data:
        print("   Primeiros 5 registros:")
        for row in sample.data:
            print(f"   - Pai: {row['username_pai']}, Filho: {row['username_filho']}")
    else:
        print("   Nenhum registro encontrado ou erro na consulta.")
    
    # Busca em seguidores
    print(f"\n🔎 Buscando username em seguidores: {username}")
    response = table_seguidores.select("id, username_pai, username_filho").or_(f"username_pai.eq.{username},username_filho.eq.{username}").limit(5).execute()
    print(f"📥 Resposta completa: {response.data}")
    
    if response.data:
        print("\n⚠️ Usuário encontrado na tabela seguidores!")
        return response.data[0]["id"]
    
    return None

if __name__ == "__main__":
    # Primeiro, vamos listar todas as tabelas
    listar_tabelas()
    
    # Depois, tentamos buscar o usuário
    username = "alexandrebononi"
    id_encontrado = buscar_id_por_username_supabase(username)
    print(f"\n✅ ID encontrado: {id_encontrado}")