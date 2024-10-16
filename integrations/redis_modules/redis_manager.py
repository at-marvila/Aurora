import redis
import json
from datetime import datetime
import logging

class RedisManager:
    def __init__(self, host, port, password):
        # Inicializa a conexão com o Redis
        self.client = redis.Redis(host=host, port=port, password=password)

    def insert_action_embedding(self, function_name, vector):
        """
        Insere ou recupera um embedding para uma ação específica no Redis.
        Evita reprocessamento verificando se o embedding já existe.
        """
        key = f"action_embedding:{function_name}"
        
        if not self.client.exists(key):
            self.client.hset(key, mapping={
                "vector": json.dumps(vector),
                "created_at": datetime.utcnow().isoformat()
            })
            logging.info(f"Embedding inserido para a função '{function_name}'")
        return key

    def get_action_embedding(self, function_name):
        """
        Recupera o vetor de embedding para uma ação especificada, se existir.
        """
        key = f"action_embedding:{function_name}"
        
        if self.client.exists(key):
            try:
                return json.loads(self.client.hget(key, "vector"))
            except json.JSONDecodeError as e:
                logging.warning(f"Erro ao carregar o embedding para a função '{function_name}': {e}")
        else:
            logging.warning(f"Nenhum embedding encontrado para a função '{function_name}'")
        return None

    def insert_user_profile(self, supermarket_chain_code, document, vector):
        """
        Insere um novo hash para o perfil do usuário no Redis usando `document` como identificador.
        """
        key = f"profile:{supermarket_chain_code}:{document}"
        self.client.hset(key, mapping={
            "vector": json.dumps(vector),
            "last_access": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow().isoformat(),
            "document": document
        })
        return key

    def get_user_profile(self, supermarket_chain_code, document):
        """
        Recupera o perfil do usuário baseado no `document`, se existir.
        """
        key = f"profile:{supermarket_chain_code}:{document}"
        
        if self.client.exists(key):
            profile = self.client.hgetall(key)
            profile['vector'] = json.loads(profile['vector'])
            return profile
        logging.warning(f"Nenhum perfil encontrado para o documento '{document}'")
        return None

    def update_last_access(self, supermarket_chain_code, document):
        """
        Atualiza o timestamp de `last_access` para um perfil de usuário específico.
        """
        key = f"profile:{supermarket_chain_code}:{document}"
        
        if self.client.exists(key):
            self.client.hset(key, "last_access", datetime.utcnow().isoformat())
            logging.info(f"Último acesso atualizado para o perfil '{document}'")
        else:
            logging.warning(f"O perfil '{document}' não existe para atualização.")

# Exemplo de uso
# redis_manager = RedisManager(host="redis-11850.c279.us-central1-1.gce.redns.redis-cloud.com", port=11850, password="sua_senha")
# redis_manager.insert_action_embedding("register_timekeeping", [0.12, 0.34, 0.56, 0.78])
# embedding = redis_manager.get_action_embedding("register_timekeeping")
# redis_manager.insert_user_profile("SUPERMAGO-RS-POA-CTR-001", "98765432100", [0.235, 0.543, 0.678, 0.876])
# profile = redis_manager.get_user_profile("SUPERMAGO-RS-POA-CTR-001", "98765432100")