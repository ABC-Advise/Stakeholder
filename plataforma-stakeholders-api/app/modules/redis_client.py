import redis
from urllib.parse import quote_plus

class RedisClient:
    def __init__(self, app=None):
        self.__redis = None
        if app is not None:
            self.__init_app(app)

    def __init_app(self, app):
        try:
            # Construindo a URL do Redis com os parâmetros do config.ini
            redis_host = app.config.get('REDIS_HOST', 'localhost')
            redis_port = app.config.get('REDIS_PORT', 6379)
            redis_db = app.config.get('REDIS_DB', 0)
            redis_user = app.config.get('REDIS_USER', 'default')
            redis_password = app.config.get('REDIS_PASSWORD', 'redis123')
            
            # Montando a URL do Redis
            redis_url = f"redis://{redis_user}:{quote_plus(redis_password)}@{redis_host}:{redis_port}/{redis_db}"
            
            self.__redis = redis.Redis.from_url(redis_url, decode_responses=True)
            # Testa a conexão
            self.__redis.ping()
            print("Redis conectado com sucesso!")
        except redis.ConnectionError as e:
            print(f"Erro ao conectar ao Redis: {e}")
            # Fallback para um cache em memória simples se o Redis não estiver disponível
            self.__redis = {}
        except Exception as e:
            print(f"Erro inesperado ao conectar ao Redis: {e}")
            self.__redis = {}

    def set(self, key, value, ex=None):
        """
        Set a key in Redis with an optional expiration time.

        :param key: The key to set.
        :param value: The value to set for the key.
        :param ex: Expiration time in seconds.
        :return: True if the operation was successful, False otherwise.
        """
        try:
            if isinstance(self.__redis, dict):
                self.__redis[key] = value
                return True
            return self.__redis.set(key, value, ex=ex)
        except Exception as e:
            print(f"Erro ao definir chave no Redis: {e}")
            return False

    def get(self, key):
        """
        Get the value of a key from Redis.

        :param key: The key to get.
        :return: The value of the key as a decoded string, or None if the key does not exist.
        """
        try:
            if isinstance(self.__redis, dict):
                return self.__redis.get(key)
            return self.__redis.get(key)
        except Exception as e:
            print(f"Erro ao obter chave do Redis: {e}")
            return None

    def delete(self, key):
        """
        Delete a key from Redis.

        :param key: The key to delete.
        :return: The number of keys that were removed.
        """
        try:
            if isinstance(self.__redis, dict):
                if key in self.__redis:
                    del self.__redis[key]
                    return 1
                return 0
            return self.__redis.delete(key)
        except Exception as e:
            print(f"Erro ao deletar chave do Redis: {e}")
            return 0

    def exists(self, key):
        """
        Check if a key exists in Redis.

        :param key: The key to check.
        :return: True if the key exists, False otherwise.
        """
        try:
            if isinstance(self.__redis, dict):
                return key in self.__redis
            return self.__redis.exists(key)
        except Exception as e:
            print(f"Erro ao verificar existência da chave no Redis: {e}")
            return False

    def keys(self, pattern='*'):
        """
        Get all keys matching a pattern from Redis.

        :param pattern: The pattern to match keys.
        :return: A list of keys matching the pattern.
        """
        try:
            if isinstance(self.__redis, dict):
                return [k for k in self.__redis.keys() if pattern == '*' or pattern in k]
            return self.__redis.keys(pattern)
        except Exception as e:
            print(f"Erro ao buscar chaves no Redis: {e}")
            return []
