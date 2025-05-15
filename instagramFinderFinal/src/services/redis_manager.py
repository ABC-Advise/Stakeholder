import redis
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RedisManager:
    def __init__(self, host, port, db, connect_timeout=2, password=None):
        self.host = host
        self.port = port
        self.db = db
        self.connect_timeout = connect_timeout
        self.password = password
        self.client = None
        self.is_available = False
        self._connect()

    def _connect(self):
        try:
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                socket_connect_timeout=self.connect_timeout
            )
            self.client.ping()
            self.is_available = True
            logger.info(f"[RedisManager] Conexão com Redis ({self.host}:{self.port}) estabelecida.")
        except Exception as e:
            self.is_available = False
            logger.warning(f"[RedisManager] [AVISO] Não foi possível conectar ao Redis ({self.host}:{self.port}): {e}")

    def get(self, key):
        if not self.is_available or self.client is None:
            return None
        try:
            return self.client.get(key)
        except Exception as e:
            logger.error(f"[RedisManager] Erro ao GET do Redis: {e}")
            return None

    def set(self, key, value):
        if not self.is_available or self.client is None:
            return False
        try:
            self.client.set(key, value)
            return True
        except Exception as e:
            logger.error(f"[RedisManager] Erro ao SET no Redis: {e}")
            return False 