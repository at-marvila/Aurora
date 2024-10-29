import redis
import logging
import json

class RedisDataRetriever:
    def __init__(self, redis_client):
        self.redis_client = redis_client

    def get_intent_response(self, supermarket_key, intent_category, intent_phrase):
        intent_key = f"{supermarket_key}:intent:{intent_category}:{intent_phrase}"
        response = self.redis_client.get(intent_key)
        
        # Loga a resposta original sem formatação adicional
        if response:
            logging.debug(f"get_intent_response - Chave: {intent_key}, Resposta: {response}")
                
        return response

    def get_action_response(self, supermarket_key, action_name, context):
        action_key = f"{supermarket_key}:action:{action_name}:{context}"
        response = self.redis_client.get(action_key)
        
        # Loga a resposta original sem formatação adicional
        if response:
            logging.debug(f"get_action_response - Chave: {action_key}, Resposta: {response}")
                
        return response

    def get_response(self, supermarket_key, response_category, response_context):
        response_key = f"{supermarket_key}:response:{response_category}:{response_context}"
        response = self.redis_client.get(response_key)
        
        # Loga a resposta original sem formatação adicional
        if response:
            logging.debug(f"get_response - Chave: {response_key}, Resposta: {response}")
                
        return response

    def get_all_subkeys(self, base_key):
        keys = self.redis_client.keys(f"{base_key}:*")
        subkeys = [key.split(":")[-1] for key in keys]
        logging.debug(f"get_all_subkeys - Base Key: {base_key}, Subkeys: {subkeys}")
        return subkeys

    def get(self, key):
        response = self.redis_client.get(key)
        
        # Loga a resposta original sem formatação adicional
        if response:
            logging.debug(f"get - Chave: {key}, Resposta: {response}")
                
        return response

    def keys(self, pattern):
        """Busca todas as chaves que correspondem ao padrão fornecido."""
        return self.redis_client.keys(pattern)