# Documentação da Hiker API

## Instalação

Para usar a Hiker API, primeiro instale-a usando pip:

```bash
pip install hikerapi
```

## Uso

Você precisa passar a chave para o Client e chamar a função desejada para obter o resultado.

Por exemplo:

```python
from hikerapi import Client

# Cliente síncrono
cl = Client(api_key="sua_chave_aqui")
cl.user_by_username_v1("usuario")

# Ou usando cliente assíncrono
from hikerapi import AsyncClient
cl = AsyncClient(api_key="sua_chave_aqui")
await cl.user_by_username_v1("usuario")
```

## Classes Principais

### Client (Síncrono)
```python
class hikerapi.Client(token: str | None = None, timeout: float | None = 10)
```

### AsyncClient (Assíncrono)
```python
class hikerapi.AsyncClient(token: str | None = None, timeout: float | None = 10)
```

## Autenticação

A Hiker API utiliza autenticação via Bearer Token. O token deve ser incluído no header de todas as requisições:

```python
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
```

## Endpoints

### 1. Buscar Perfil do Instagram
```http
GET /v1/instagram/profile/{username}
```

Busca informações básicas de um perfil do Instagram.

#### Parâmetros
- `username` (path): Nome de usuário do Instagram

#### Resposta
```json
{
    "username": "exemplo",
    "full_name": "Nome Completo",
    "followers_count": 1000,
    "following_count": 500,
    "bio": "Descrição do perfil",
    "profile_picture_url": "https://instagram.com/...",
    "is_private": false,
    "is_verified": false,
    "external_url": "https://...",
    "media_count": 150
}
```

### 2. Obter Detalhes do Perfil
```http
GET /v1/instagram/profile/{profile_id}/details
```

Obtém métricas e detalhes adicionais de um perfil.

#### Parâmetros
- `profile_id` (path): ID do perfil

#### Resposta
```json
{
    "engagement_rate": 3.5,
    "average_likes": 500,
    "average_comments": 50,
    "post_frequency": 2.5,
    "audience_demographics": {
        "age_groups": {
            "13-17": 5,
            "18-24": 45,
            "25-34": 35,
            "35-44": 10,
            "45+": 5
        },
        "gender": {
            "male": 40,
            "female": 60
        },
        "locations": {
            "BR": 60,
            "US": 20,
            "PT": 10,
            "other": 10
        }
    },
    "best_posting_times": [
        {
            "day": "monday",
            "hour": 18,
            "engagement": 4.2
        }
    ],
    "hashtag_analysis": [
        {
            "hashtag": "#exemplo",
            "usage_count": 50,
            "engagement_rate": 3.8
        }
    ]
}
```

### 3. Buscar Posts Recentes
```http
GET /v1/instagram/profile/{username}/posts
```

Busca os posts mais recentes de um perfil.

#### Parâmetros
- `username` (path): Nome de usuário do Instagram
- `limit` (query): Número máximo de posts (padrão: 10)
- `offset` (query): Número de posts para pular (padrão: 0)

#### Resposta
```json
{
    "posts": [
        {
            "id": "123456789",
            "caption": "Legenda do post",
            "media_type": "IMAGE",
            "media_url": "https://instagram.com/...",
            "likes_count": 1000,
            "comments_count": 50,
            "posted_at": "2023-11-01T12:00:00Z",
            "hashtags": ["#exemplo", "#teste"],
            "mentions": ["@usuario1", "@usuario2"]
        }
    ],
    "total_count": 150,
    "has_more": true
}
```

## Códigos de Erro

- `400 Bad Request`: Parâmetros inválidos
- `401 Unauthorized`: Token inválido ou expirado
- `404 Not Found`: Perfil não encontrado
- `429 Too Many Requests`: Limite de requisições excedido
- `500 Internal Server Error`: Erro interno do servidor

## Exemplos de Uso

### Python
```python
import requests

class HikerClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.hiker.com/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def get_profile(self, username: str):
        response = requests.get(
            f"{self.base_url}/instagram/profile/{username}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def get_profile_details(self, profile_id: str):
        response = requests.get(
            f"{self.base_url}/instagram/profile/{profile_id}/details",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def get_recent_posts(self, username: str, limit: int = 10, offset: int = 0):
        response = requests.get(
            f"{self.base_url}/instagram/profile/{username}/posts",
            headers=self.headers,
            params={"limit": limit, "offset": offset}
        )
        response.raise_for_status()
        return response.json()

# Exemplo de uso
client = HikerClient(api_key="seu_token_aqui")

# Buscar perfil
profile = client.get_profile("exemplo")
print(profile)

# Obter detalhes
details = client.get_profile_details(profile["id"])
print(details)

# Buscar posts recentes
posts = client.get_recent_posts("exemplo", limit=5)
print(posts)
```

### cURL
```bash
# Buscar perfil
curl -H "Authorization: Bearer seu_token_aqui" \
     https://api.hiker.com/v1/instagram/profile/exemplo

# Obter detalhes
curl -H "Authorization: Bearer seu_token_aqui" \
     https://api.hiker.com/v1/instagram/profile/123/details

# Buscar posts recentes
curl -H "Authorization: Bearer seu_token_aqui" \
     "https://api.hiker.com/v1/instagram/profile/exemplo/posts?limit=5&offset=0"
```

## Limites e Quotas

- Rate Limit: 100 requisições por minuto
- Quota diária: 10.000 requisições
- Tamanho máximo de resposta: 10MB
- Timeout: 30 segundos

## Boas Práticas

1. Sempre trate os erros adequadamente
2. Implemente retry com backoff exponencial
3. Cache as respostas quando possível
4. Monitore o uso da API
5. Implemente rate limiting no seu lado 

## Métodos Principais

### Busca de Usuários
```python
# Buscar usuário por username
user_by_username_v1(username: str) -> Dict
user_by_username_v2(username: str) -> Dict

# Buscar usuário por ID
user_by_id_v1(id: str) -> Dict
user_by_id_v2(id: str) -> Dict

# Buscar usuário por URL
user_by_url_v1(url: str) -> Dict

# Buscar informações do perfil web
user_web_profile_info_v1(username: str) -> Dict
```

### Mídia e Posts
```python
# Buscar mídia por código
media_by_code_v1(code: str) -> Dict
media_info_by_code_v2(code: str) -> Dict

# Buscar mídia por ID
media_by_id_v1(id: str) -> Dict
media_info_by_id_v2(id: str) -> Dict

# Buscar mídia por URL
media_by_url_v1(url: str) -> Dict
media_info_by_url_v2(url: str) -> Dict

# Buscar mídias do usuário
user_medias(user_id: str, page_id: str | None = None) -> List[Dict]
user_medias_v2(user_id: str | None = None, page_id: str | None = None) -> Dict
```

### Stories e Highlights
```python
# Buscar stories
user_stories_v1(user_id: str, amount: int | None = None) -> Dict
user_stories_v2(user_id: str) -> Dict
user_stories_by_username_v1(username: str, amount: int | None = None) -> Dict
user_stories_by_username_v2(username: str) -> Dict

# Buscar highlights
user_highlights_v1(user_id: str, amount: int | None = None) -> Dict
user_highlights_v2(user_id: str, amount: int | None = None) -> Dict
user_highlights_by_username(username: str, amount: int | None = None) -> List[Dict]
```

### Seguidores e Seguindo
```python
# Buscar seguidores
user_followers_chunk_v1(user_id: str, max_id: str | None = None) -> Dict
user_followers_v2(user_id: str | None = None, page_id: str | None = None) -> Dict

# Buscar seguindo
user_following_chunk_v1(user_id: str, max_id: str | None = None) -> Dict
user_following_v2(user_id: str | None = None, page_id: str | None = None) -> Dict
```

### Comentários e Curtidas
```python
# Buscar comentários
media_comments_v2(id: str, can_support_threading: Any | None = None, page_id: Any | None = None) -> Dict
comments_chunk_gql(media_id: str, sort_order: Any | None = None, end_cursor: Any | None = None) -> Dict

# Buscar curtidas
media_likers_v2(id: str) -> Dict
media_likers_gql(media_id: str) -> Dict
```

### Busca
```python
# Buscar contas
search_accounts_v2(query: str, page_token: str | None = None) -> Dict

# Buscar hashtags
search_hashtags_v1(query: str) -> Dict
search_hashtags_v2(query: str, page_token: str | None = None) -> Dict

# Buscar lugares
search_places_v2(query: str) -> Dict

# Buscar reels
search_reels_v2(query: str, reels_max_id: str | None = None) -> Dict
```

## Exemplos de Uso Detalhados

### Busca de Perfil Completo
```python
from hikerapi import Client

client = Client(api_key="sua_chave_aqui")

# Buscar perfil básico
profile = client.user_by_username_v1("exemplo")
print(f"Nome: {profile['full_name']}")
print(f"Seguidores: {profile['followers_count']}")
print(f"Seguindo: {profile['following_count']}")

# Buscar mídias recentes
medias = client.user_medias_v2(profile['id'])
for media in medias['items']:
    print(f"Post: {media['caption']}")
    print(f"Curtidas: {media['like_count']}")

# Buscar stories
stories = client.user_stories_v1(profile['id'])
for story in stories['items']:
    print(f"Story: {story['taken_at']}")

# Buscar seguidores
followers = client.user_followers_v2(profile['id'])
for follower in followers['users']:
    print(f"Seguidor: {follower['username']}")
```

### Busca de Hashtags e Posts
```python
from hikerapi import Client

client = Client(api_key="sua_chave_aqui")

# Buscar hashtags
hashtags = client.search_hashtags_v2("python")
for hashtag in hashtags['results']:
    print(f"Hashtag: #{hashtag['name']}")
    print(f"Posts: {hashtag['media_count']}")

# Buscar posts por hashtag
posts = client.hashtag_medias_recent_v2("python")
for post in posts['items']:
    print(f"Post: {post['caption']}")
    print(f"Autor: {post['user']['username']}")
```

### Análise de Engajamento
```python
from hikerapi import Client
from datetime import datetime, timedelta

client = Client(api_key="sua_chave_aqui")

def analyze_engagement(username: str):
    # Buscar perfil
    profile = client.user_by_username_v1(username)
    
    # Buscar posts recentes
    medias = client.user_medias_v2(profile['id'])
    
    total_likes = 0
    total_comments = 0
    post_count = len(medias['items'])
    
    for media in medias['items']:
        total_likes += media['like_count']
        total_comments += media['comment_count']
    
    if post_count > 0:
        avg_likes = total_likes / post_count
        avg_comments = total_comments / post_count
        engagement_rate = ((avg_likes + avg_comments) / profile['followers_count']) * 100
        
        print(f"Taxa de engajamento: {engagement_rate:.2f}%")
        print(f"Média de curtidas: {avg_likes:.0f}")
        print(f"Média de comentários: {avg_comments:.0f}")

# Exemplo de uso
analyze_engagement("exemplo")
```

### Monitoramento de Stories
```python
from hikerapi import Client
import time

client = Client(api_key="sua_chave_aqui")

def monitor_stories(username: str, interval: int = 300):
    """
    Monitora stories de um usuário a cada intervalo de tempo
    :param username: Nome de usuário
    :param interval: Intervalo em segundos (padrão: 5 minutos)
    """
    while True:
        try:
            stories = client.user_stories_by_username_v1(username)
            
            if stories['items']:
                print(f"\nNovos stories de {username} em {time.strftime('%H:%M:%S')}")
                for story in stories['items']:
                    print(f"- Story postado em: {datetime.fromtimestamp(story['taken_at'])}")
            else:
                print(f"Nenhum story encontrado para {username}")
                
            time.sleep(interval)
            
        except Exception as e:
            print(f"Erro ao buscar stories: {e}")
            time.sleep(60)  # Espera 1 minuto em caso de erro

# Exemplo de uso
monitor_stories("exemplo", interval=600)  # Monitora a cada 10 minutos 
```

## Tratamento de Erros e Boas Práticas

### Tratamento de Erros
```python
from hikerapi import Client
from requests.exceptions import RequestException
import time

client = Client(api_key="sua_chave_aqui")

def buscar_perfil_com_retry(username: str, max_retries: int = 3):
    """
    Busca perfil com retry em caso de erro
    :param username: Nome de usuário
    :param max_retries: Número máximo de tentativas
    :return: Dados do perfil ou None em caso de erro
    """
    for attempt in range(max_retries):
        try:
            return client.user_by_username_v1(username)
        except RequestException as e:
            if attempt == max_retries - 1:
                print(f"Erro ao buscar perfil após {max_retries} tentativas: {e}")
                return None
            print(f"Tentativa {attempt + 1} falhou, tentando novamente...")
            time.sleep(2 ** attempt)  # Backoff exponencial
```

### Cache de Respostas
```python
from hikerapi import Client
from functools import lru_cache
from datetime import datetime, timedelta

client = Client(api_key="sua_chave_aqui")

class CachedHikerClient:
    def __init__(self, api_key: str, cache_timeout: int = 300):
        self.client = Client(api_key=api_key)
        self.cache_timeout = cache_timeout
        self._cache = {}
        self._cache_times = {}
    
    def _is_cache_valid(self, key: str) -> bool:
        if key not in self._cache_times:
            return False
        return (datetime.now() - self._cache_times[key]).seconds < self.cache_timeout
    
    def get_profile(self, username: str):
        cache_key = f"profile_{username}"
        
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
        
        result = self.client.user_by_username_v1(username)
        self._cache[cache_key] = result
        self._cache_times[cache_key] = datetime.now()
        
        return result

# Exemplo de uso
cached_client = CachedHikerClient(api_key="sua_chave_aqui", cache_timeout=600)  # Cache por 10 minutos
```

### Rate Limiting
```python
from hikerapi import Client
import time
from collections import deque
from datetime import datetime, timedelta

class RateLimitedHikerClient:
    def __init__(self, api_key: str, requests_per_minute: int = 100):
        self.client = Client(api_key=api_key)
        self.requests_per_minute = requests_per_minute
        self.request_times = deque()
    
    def _wait_if_needed(self):
        now = datetime.now()
        
        # Remove timestamps antigos
        while self.request_times and (now - self.request_times[0]) > timedelta(minutes=1):
            self.request_times.popleft()
        
        # Se atingiu o limite, espera
        if len(self.request_times) >= self.requests_per_minute:
            sleep_time = 60 - (now - self.request_times[0]).seconds
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        self.request_times.append(now)
    
    def get_profile(self, username: str):
        self._wait_if_needed()
        return self.client.user_by_username_v1(username)

# Exemplo de uso
rate_limited_client = RateLimitedHikerClient(api_key="sua_chave_aqui", requests_per_minute=100)
```

### Monitoramento de Uso
```python
from hikerapi import Client
import time
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MonitoredHikerClient:
    def __init__(self, api_key: str):
        self.client = Client(api_key=api_key)
        self.request_count = 0
        self.start_time = datetime.now()
    
    def _log_request(self, method: str, params: dict):
        self.request_count += 1
        elapsed = (datetime.now() - self.start_time).seconds
        
        logger.info(f"Request #{self.request_count}")
        logger.info(f"Método: {method}")
        logger.info(f"Parâmetros: {params}")
        logger.info(f"Tempo desde início: {elapsed}s")
        logger.info(f"Taxa de requisições: {self.request_count/elapsed:.2f} req/s")
    
    def get_profile(self, username: str):
        self._log_request("get_profile", {"username": username})
        return self.client.user_by_username_v1(username)

# Exemplo de uso
monitored_client = MonitoredHikerClient(api_key="sua_chave_aqui") 
```

## Limites de Requisições e Timeout

### Limites Globais
- Limite diário: 1 milhão de requisições
- Limite por segundo: 11 requisições
- Timeout padrão: 20 segundos

### Informações de Requisições
Cada requisição à API pode incluir várias chamadas internas. O número total de unidades de requisição gastas é retornado no header da resposta:

```
x-hiker-info: reqs=<número>
```

### Contagem de Requisições por Endpoint

| Endpoint | Reqs | Descrição |
|----------|------|-----------|
| `/v1/user/highlights` | 2 | Obtém highlights por ID + verifica privacidade |
| `/v2/user/highlights` | 2 | Obtém highlights por ID + verifica privacidade |
| `/v1/user/highlights/by/username` | 3 | Busca ID por username + obtém highlights + verifica privacidade |
| `/v2/user/highlights/by/username` | 3 | Busca ID por username + obtém highlights + verifica privacidade |
| `/v1/user/stories` | 2 | Obtém stories por ID + verifica privacidade |
| `/v2/user/stories` | 2 | Obtém stories por ID + verifica privacidade |
| `/v1/user/stories/by/username` | 3 | Busca ID por username + obtém stories + verifica privacidade |
| `/v2/user/stories/by/username` | 3 | Busca ID por username + obtém stories + verifica privacidade |
| `/v1/user/search/followers` | 2 | Obtém seguidores por ID + verifica privacidade |
| `/v1/user/search/following` | 2 | Obtém seguindo por ID + verifica privacidade |
| `/a2/user` | 2 | Obtém dados do perfil + mídia |
| `/v2/user/explore/businesses/by/id` | 2 | Obtém recomendações de negócios por ID + detalhes da conta |
| `/gql/user/followers/chunk` | 2 | Obtém seguidores por ID + verifica privacidade |
| `/gql/user/following/chunk` | 2 | Obtém seguindo por ID + verifica privacidade |

### Modo Force
Adicionando o parâmetro `"force": "on"` em endpoints que verificam privacidade, você pode:
- Pular verificações de privacidade
- Reduzir o número de requisições
- Exemplo: `/v1/user/highlights` com force reduz de 2 para 1 req

### Exemplo de Implementação com Rate Limiting
```python
import httpx
import asyncio
from typing import List

class HikerAPIClient:
    def __init__(self, api_key: str, rate_limit: int = 11):
        self.api_key = api_key
        self.rate_limit = rate_limit
        self.semaphore = asyncio.Semaphore(rate_limit)
        self.headers = {
            "x-access-key": api_key,
            "accept": "application/json"
        }
    
    async def _make_request(self, url: str, params: dict = None) -> dict:
        async with self.semaphore:
            async with httpx.AsyncClient(timeout=20) as client:
                while True:
                    try:
                        response = await client.get(url, params=params, headers=self.headers)
                        
                        if response.status_code == 429:
                            print("Limite de requisições excedido, aguardando...")
                            await asyncio.sleep(2)
                            continue
                        elif response.status_code == 402:
                            raise Exception("Saldo insuficiente")
                        
                        return response.json()
                        
                    except Exception as e:
                        print(f"Erro na requisição: {e}")
                        await asyncio.sleep(1)
    
    async def get_followers(self, user_id: str) -> List[dict]:
        params = {"user_id": user_id, "page_id": "", "force": "on"}
        followers = []
        
        while True:
            response = await self._make_request(
                "https://api.hikerapi.com/v2/user/followers",
                params=params
            )
            
            users = response["response"]["users"]
            page_id = response["next_page_id"]
            
            followers.extend(users)
            
            if not page_id:
                break
                
            params["page_id"] = page_id
            
        return followers

# Exemplo de uso
async def main():
    client = HikerAPIClient(api_key="sua_chave_aqui")
    
    # Lista de IDs de usuários para buscar seguidores
    user_ids = [
        "1553030189",
        "12345",
        "4238157586",
        # ... mais IDs ...
    ]
    
    # Criar tasks para buscar seguidores de cada usuário
    tasks = [client.get_followers(user_id) for user_id in user_ids]
    
    # Executar todas as tasks em paralelo
    results = await asyncio.gather(*tasks)
    
    # Processar resultados
    for user_id, followers in zip(user_ids, results):
        print(f"Usuário {user_id}: {len(followers)} seguidores")

# Executar
asyncio.run(main())
```

### Dicas para Otimização
1. Use o modo `force: "on"` quando possível para reduzir o número de requisições
2. Implemente cache para dados que não mudam frequentemente
3. Use semáforos para limitar requisições simultâneas
4. Implemente backoff exponencial em caso de erros
5. Monitore o header `x-hiker-info` para acompanhar o uso de requisições

## Boas Práticas

1. Sempre trate os erros adequadamente
2. Implemente retry com backoff exponencial
3. Cache as respostas quando possível
4. Monitore o uso da API
5. Implemente rate limiting no seu lado 

## Métodos Principais

### Busca de Usuários
```python
# Buscar usuário por username
user_by_username_v1(username: str) -> Dict
user_by_username_v2(username: str) -> Dict

# Buscar usuário por ID
user_by_id_v1(id: str) -> Dict
user_by_id_v2(id: str) -> Dict

# Buscar usuário por URL
user_by_url_v1(url: str) -> Dict

# Buscar informações do perfil web
user_web_profile_info_v1(username: str) -> Dict
```

### Mídia e Posts
```python
# Buscar mídia por código
media_by_code_v1(code: str) -> Dict
media_info_by_code_v2(code: str) -> Dict

# Buscar mídia por ID
media_by_id_v1(id: str) -> Dict
media_info_by_id_v2(id: str) -> Dict

# Buscar mídia por URL
media_by_url_v1(url: str) -> Dict
media_info_by_url_v2(url: str) -> Dict

# Buscar mídias do usuário
user_medias(user_id: str, page_id: str | None = None) -> List[Dict]
user_medias_v2(user_id: str | None = None, page_id: str | None = None) -> Dict
```

### Stories e Highlights
```python
# Buscar stories
user_stories_v1(user_id: str, amount: int | None = None) -> Dict
user_stories_v2(user_id: str) -> Dict
user_stories_by_username_v1(username: str, amount: int | None = None) -> Dict
user_stories_by_username_v2(username: str) -> Dict

# Buscar highlights
user_highlights_v1(user_id: str, amount: int | None = None) -> Dict
user_highlights_v2(user_id: str, amount: int | None = None) -> Dict
user_highlights_by_username(username: str, amount: int | None = None) -> List[Dict]
```

### Seguidores e Seguindo
```python
# Buscar seguidores
user_followers_chunk_v1(user_id: str, max_id: str | None = None) -> Dict
user_followers_v2(user_id: str | None = None, page_id: str | None = None) -> Dict

# Buscar seguindo
user_following_chunk_v1(user_id: str, max_id: str | None = None) -> Dict
user_following_v2(user_id: str | None = None, page_id: str | None = None) -> Dict
```

### Comentários e Curtidas
```python
# Buscar comentários
media_comments_v2(id: str, can_support_threading: Any | None = None, page_id: Any | None = None) -> Dict
comments_chunk_gql(media_id: str, sort_order: Any | None = None, end_cursor: Any | None = None) -> Dict

# Buscar curtidas
media_likers_v2(id: str) -> Dict
media_likers_gql(media_id: str) -> Dict
```

### Busca
```python
# Buscar contas
search_accounts_v2(query: str, page_token: str | None = None) -> Dict

# Buscar hashtags
search_hashtags_v1(query: str) -> Dict
search_hashtags_v2(query: str, page_token: str | None = None) -> Dict

# Buscar lugares
search_places_v2(query: str) -> Dict

# Buscar reels
search_reels_v2(query: str, reels_max_id: str | None = None) -> Dict
```

## Exemplos de Uso Detalhados

### Busca de Perfil Completo
```python
from hikerapi import Client

client = Client(api_key="sua_chave_aqui")

# Buscar perfil básico
profile = client.user_by_username_v1("exemplo")
print(f"Nome: {profile['full_name']}")
print(f"Seguidores: {profile['followers_count']}")
print(f"Seguindo: {profile['following_count']}")

# Buscar mídias recentes
medias = client.user_medias_v2(profile['id'])
for media in medias['items']:
    print(f"Post: {media['caption']}")
    print(f"Curtidas: {media['like_count']}")

# Buscar stories
stories = client.user_stories_v1(profile['id'])
for story in stories['items']:
    print(f"Story: {story['taken_at']}")

# Buscar seguidores
followers = client.user_followers_v2(profile['id'])
for follower in followers['users']:
    print(f"Seguidor: {follower['username']}")
```

### Busca de Hashtags e Posts
```python
from hikerapi import Client

client = Client(api_key="sua_chave_aqui")

# Buscar hashtags
hashtags = client.search_hashtags_v2("python")
for hashtag in hashtags['results']:
    print(f"Hashtag: #{hashtag['name']}")
    print(f"Posts: {hashtag['media_count']}")

# Buscar posts por hashtag
posts = client.hashtag_medias_recent_v2("python")
for post in posts['items']:
    print(f"Post: {post['caption']}")
    print(f"Autor: {post['user']['username']}")
```

### Análise de Engajamento
```python
from hikerapi import Client
from datetime import datetime, timedelta

client = Client(api_key="sua_chave_aqui")

def analyze_engagement(username: str):
    # Buscar perfil
    profile = client.user_by_username_v1(username)
    
    # Buscar posts recentes
    medias = client.user_medias_v2(profile['id'])
    
    total_likes = 0
    total_comments = 0
    post_count = len(medias['items'])
    
    for media in medias['items']:
        total_likes += media['like_count']
        total_comments += media['comment_count']
    
    if post_count > 0:
        avg_likes = total_likes / post_count
        avg_comments = total_comments / post_count
        engagement_rate = ((avg_likes + avg_comments) / profile['followers_count']) * 100
        
        print(f"Taxa de engajamento: {engagement_rate:.2f}%")
        print(f"Média de curtidas: {avg_likes:.0f}")
        print(f"Média de comentários: {avg_comments:.0f}")

# Exemplo de uso
analyze_engagement("exemplo")
```

### Monitoramento de Stories
```python
from hikerapi import Client
import time

client = Client(api_key="sua_chave_aqui")

def monitor_stories(username: str, interval: int = 300):
    """
    Monitora stories de um usuário a cada intervalo de tempo
    :param username: Nome de usuário
    :param interval: Intervalo em segundos (padrão: 5 minutos)
    """
    while True:
        try:
            stories = client.user_stories_by_username_v1(username)
            
            if stories['items']:
                print(f"\nNovos stories de {username} em {time.strftime('%H:%M:%S')}")
                for story in stories['items']:
                    print(f"- Story postado em: {datetime.fromtimestamp(story['taken_at'])}")
            else:
                print(f"Nenhum story encontrado para {username}")
                
            time.sleep(interval)
            
        except Exception as e:
            print(f"Erro ao buscar stories: {e}")
            time.sleep(60)  # Espera 1 minuto em caso de erro

# Exemplo de uso
monitor_stories("exemplo", interval=600)  # Monitora a cada 10 minutos 