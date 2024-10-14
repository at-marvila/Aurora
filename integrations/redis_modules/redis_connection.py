# integrations/redis/redis_connections.py
import redis
import logging

class RedisConnection:
    def __init__(self, url=None, host=None, port=None, password=None):
        """
        Inicializa a conexão com o Redis, priorizando uma URL se fornecida.
        """
        if url:
            self.client = redis.Redis.from_url(url)
            logging.info("Conectado ao Redis usando URL.")
        else:
            self.client = redis.Redis(host=host, port=port, password=password)
            logging.info("Conectado ao Redis usando host e porta.")

        # Verifica a conexão no início
        if not self._check_connection():
            raise ConnectionError("Falha ao conectar ao Redis. Verifique as configurações.")

    def get_client(self):
        return self.client

    def _check_connection(self):
        try:
            return self.client.ping()
        except redis.ConnectionError:
            return False