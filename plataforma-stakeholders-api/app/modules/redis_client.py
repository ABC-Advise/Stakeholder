import redis

class RedisClient:
    def __init__(self, app=None):
        self.__redis = None
        if app is not None:
            self.__init_app(app)

    def __init_app(self, app):
        redis_url = app.config.get('IPBAN_REDIS_URL')
        self.__redis = redis.Redis.from_url(redis_url)

    def set(self, key, value, ex=None):
        """
        Set a key in Redis with an optional expiration time.

        :param key: The key to set.
        :param value: The value to set for the key.
        :param ex: Expiration time in seconds.
        :return: True if the operation was successful, False otherwise.
        """
        return self.__redis.set(key, value, ex=ex)

    def get(self, key):
        """
        Get the value of a key from Redis.

        :param key: The key to get.
        :return: The value of the key as a decoded string, or None if the key does not exist.
        """
        value = self.__redis.get(key)
        return value.decode('utf-8') if value else None

    def delete(self, key):
        """
        Delete a key from Redis.

        :param key: The key to delete.
        :return: The number of keys that were removed.
        """
        return self.__redis.delete(key)

    def exists(self, key):
        """
        Check if a key exists in Redis.

        :param key: The key to check.
        :return: True if the key exists, False otherwise.
        """
        return self.__redis.exists(key)

    def keys(self, pattern='*'):
        """
        Get all keys matching a pattern from Redis.

        :param pattern: The pattern to match keys.
        :return: A list of keys matching the pattern.
        """
        return self.__redis.keys(pattern)
