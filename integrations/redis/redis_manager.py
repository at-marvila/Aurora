import redis
from datetime import datetime

class RedisManager:
    def __init__(self, host, port, password):
        # Inicializa a conexão com o Redis
        self.client = redis.Redis(host=host, port=port, password=password)

    def insert_user_profile(self, supermarket_chain_code, document, vector):
        """
        Insere um novo hash para o perfil do usuário no Redis usando o `document` como identificador.
        """
        key = f"profile:{supermarket_chain_code}:{document}"
        self.client.hset(key, mapping={
            "vector": vector,
            "last_access": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow().isoformat(),
            "document": document
        })
        return key

    def get_user_profile(self, supermarket_chain_code, document):
        """
        Retorna o perfil do usuário se existir, baseado no `document`.
        """
        key = f"profile:{supermarket_chain_code}:{document}"
        if self.client.exists(key):
            return self.client.hgetall(key)
        return None

    def check_or_insert_user(self, supermarket_chain_code, vector, document):
        """
        Verifica se um perfil com o vetor existe, se não, insere um novo.
        """
        # Primeiro, tente encontrar o vetor no Redis.
        # (Isso pode exigir uma função de similaridade externa para a comparação exata.)
        all_keys = self.client.keys(f"profile:{supermarket_chain_code}:*")
        
        for key in all_keys:
            stored_vector = self.client.hget(key, "vector").decode('utf-8')
            if stored_vector == vector:  # Substitua com comparação de similaridade conforme necessário
                # Atualiza o last_access e retorna o documento associado
                self.client.hset(key, "last_access", datetime.utcnow().isoformat())
                return self.client.hget(key, "document").decode('utf-8')
        
        # Se não encontrou, insere um novo perfil usando `document` como chave única
        return self.insert_user_profile(supermarket_chain_code, document, vector)

# Exemplo de uso
# redis_manager = RedisManager(host="redis-11850.c279.us-central1-1.gce.redns.redis-cloud.com", port=11850, password="j6BhSRwBhX8wO0bAIp8t1NmpMd1eW9Kf")
# redis_manager.insert_user_profile("RS-POA-CTR-001", "987.654.321-00", "0.235,0.543,0.678,0.876")
# document = redis_manager.check_or_insert_user("RS-POA-CTR-001", "0.235,0.543,0.678,0.876", "987.654.321-00")
# print(document)