# Documentação da API do Instagram Finder

## Endpoints

### 1. Buscar Perfil
```http
GET /profiles/{username}
```

Busca um perfil do Instagram pelo username.

#### Parâmetros
- `username` (path): Nome de usuário do Instagram

#### Resposta
```json
{
  "pk": 3688474053,
  "username": "victordavi_oc",
  "full_name": "Victor Davi",
  "is_private": false,
  "profile_pic_url": "https://...",
  "profile_pic_url_hd": null,
  "is_verified": false,
  "media_count": 10,
  "follower_count": 502,
  "following_count": 595,
  "biography": "24 anos 😁\n🖥🖱⌨+🎼🎶🎙\nEngenheiro de Software",
  "external_url": "",
  "account_type": 3,
  "is_business": false,
  "public_email": "",
  "contact_phone_number": "",
  "public_phone_country_code": "",
  "public_phone_number": "",
  "business_contact_method": "UNKNOWN",
  "business_category_name": null,
  "category_name": null,
  "category": "Just for fun",
  "address_street": "",
  "city_id": 0,
  "city_name": "",
  "latitude": 0.0,
  "longitude": 0.0,
  "zip": "",
  "instagram_location_id": "",
  "interop_messaging_user_fbid": 118330336218247
}
```

### 2. Obter Detalhes do Perfil
```http
GET /profiles/{username}/details
```

Obtém detalhes completos de um perfil, incluindo informações adicionais da Hiker API.

#### Parâmetros
- `username` (path): Nome de usuário do Instagram

#### Resposta
```json
{
  "user": {
    "id": "3688474053",
    "username": "victordavi_oc",
    "full_name": "Victor Davi",
    "biography": "24 anos 😁\n🖥🖱⌨+🎼🎶🎙\nEngenheiro de Software",
    "profile_pic_url": "https://...",
    "profile_pic_url_hd": "https://...",
    "is_private": false,
    "is_verified": false,
    "category_name": "Just for fun",
    "edge_followed_by": {"count": 502},
    "edge_follow": {"count": 595},
    "highlight_reel_count": 3,
    "media_count": 10
    // ... outros campos omitidos para brevidade
  }
}
```

### 3. Listar Perfis (Exemplo de busca por nome)
```http
GET /profiles?query=Victor%20Davi
```

Lista perfis encontrados pela busca de nome (query), retornando múltiplos perfis.

#### Parâmetros de Query
- `query` (opcional): Nome ou parte do nome a ser buscado
- `limit` (opcional): Número máximo de resultados (padrão: 10)
- `offset` (opcional): Número de resultados para pular (padrão: 0)

#### Resposta
```json
{
  "num_results": 20,
  "users": [
    {
      "pk": 51659898470,
      "username": "victor.d.hanson",
      "full_name": "Victor Davis Hanson",
      "is_private": false,
      "profile_pic_url": "https://...",
      "is_verified": false
      // ... outros campos
    },
    {
      "pk": 48243289922,
      "username": "victor_.davi",
      "full_name": "Victor Davi",
      "is_private": true,
      "profile_pic_url": "https://...",
      "is_verified": false
      // ... outros campos
    }
    // ... outros perfis
  ],
  "has_more": true,
  "rank_token": "...",
  "status": "ok"
}
```

## Códigos de Erro

- `404 Not Found`: Perfil não encontrado
- `500 Internal Server Error`: Erro interno do servidor

## Exemplos de Uso

### Python
```python
import requests

# Buscar perfil
response = requests.get("http://localhost:8000/profiles/exemplo")
profile = response.json()

# Obter detalhes
response = requests.get("http://localhost:8000/profiles/exemplo/details")
details = response.json()

# Listar perfis
response = requests.get("http://localhost:8000/profiles?limit=10&offset=0")
profiles = response.json()
```

### cURL
```bash
# Buscar perfil
curl http://localhost:8000/profiles/exemplo

# Obter detalhes
curl http://localhost:8000/profiles/exemplo/details

# Listar perfis
curl http://localhost:8000/profiles?limit=10&offset=0
```

# Documentação da Integração com HikerAPI

## Instalação

```bash
pip install hikerapi
```

## Uso Básico

```python
from hikerapi import AsyncClient
client = AsyncClient(api_key="<sua_chave>")
perfil = await client.user_by_username_v1("usuario")
```

## Exemplo de Busca de Perfil

```python
from hikerapi import AsyncClient

async def buscar_perfil(username):
    client = AsyncClient(api_key="<sua_chave>")
    return await client.user_by_username_v1(username)
```

## Principais Métodos Utilizados
- `user_by_username_v1(username: str)`
- `user_about_v1(id: str)`

## Observações
- Sempre utilize o client Python para integração.
- Consulte o arquivo `hiker_api_python_client.md` para métodos avançados. 