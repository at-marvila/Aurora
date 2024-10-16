import redis

class RedisConnection:
    def __init__(self, url=None, host=None, port=None, password=None):
        if url:
            self.client = redis.StrictRedis.from_url(url, decode_responses=True)
        else:
            self.host = host or "localhost"
            self.port = port or 6379
            self.password = password
            self.client = redis.StrictRedis(host=self.host, port=self.port, password=self.password, decode_responses=True)

    def get_client(self):
        """Retorna o cliente Redis configurado."""
        return self.client
    
    def _check_connection(self):
        try:
            return self.client.ping()
        except redis.ConnectionError:
            return False