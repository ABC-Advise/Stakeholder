import asyncio
import os
from hikerapi import AsyncClient
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("HIKER_API_KEY") or "zy45mqr74skx5ylwd9zvg8tzljq4ukod"

async def main():
    client = AsyncClient(token=API_KEY)

    print("\n=== user_by_username_v1 ===")
    resposta_username = await client.user_by_username_v1("victordavi_oc")
    print(resposta_username)

    print("\n=== user_by_id_v1 ===")
    user_id = resposta_username.get("id")
    if user_id:
        resposta_id = await client.user_by_id_v1(user_id)
        print(resposta_id)
    else:
        print("ID não encontrado na resposta de username.")

    print("\n=== user_by_url_v1 ===")
    url = f"https://instagram.com/victordavi_oc"
    resposta_url = await client.user_by_url_v1(url)
    print(resposta_url)

    print("\n=== user_web_profile_info_v1 ===")
    resposta_web = await client.user_web_profile_info_v1("victordavi_oc")
    print(resposta_web)

    print("\n=== search_accounts_v2 (query: 'Victor Davi') ===")
    resposta_query = await client.search_accounts_v2(query="Victor Davi")
    print(resposta_query)

if __name__ == "__main__":
    asyncio.run(main()) 