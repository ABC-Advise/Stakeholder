from src.services.find_path_refatorado import PathFinderConfig, SupabaseManager

if __name__ == "__main__":
    start_username = "alexandrebononi"
    target_username = "waltaganlopes"
    max_depth = 4

    manager = SupabaseManager()
    start_id = manager.get_id_from_username(start_username)
    target_id = manager.get_id_from_username(target_username)

    print(f"Usuário origem: {start_username} (id: {start_id})")
    print(f"Usuário alvo: {target_username} (id: {target_id})")

    if not start_id or not target_id:
        print("Usuário(s) não encontrado(s).")
    else:
        print("\n--- BFS: Todos os menores caminhos ---")
        paths_bfs = manager.find_all_shortest_paths_bfs(start_id, target_id, max_depth=max_depth)
        if paths_bfs:
            for path in paths_bfs:
                usernames = [manager.get_username_from_id(uid) for uid in path]
                print(" -> ".join(usernames))
        else:
            print("Nenhum caminho encontrado com BFS.")

