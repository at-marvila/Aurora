import json
import logging
from transformers import AutoTokenizer, AutoModel
import torch

class EmbeddingManager:
    def __init__(self, redis_client):
        self.redis_client = redis_client
        self.tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        self.model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

    def _generate_embedding(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():
            embeddings = self.model(**inputs).last_hidden_state.mean(dim=1)
        return embeddings[0].numpy()

    def check_or_insert_embedding(self, key_prefix, text):
        key = f"{key_prefix}"

        if self.redis_client.exists(key):
            logging.info(f"Embedding já existe para a chave: {key}")
            return json.loads(self.redis_client.get(key))

        embedding = self._generate_embedding(text)
        self.redis_client.set(key, json.dumps(embedding.tolist()))
        logging.info(f"Novo embedding gerado e armazenado para a chave: {key}")
        return embedding

    def intents_exist_in_redis(self, supermarket_id):
        intent_keys = self.redis_client.keys(f"{supermarket_id}:intent:*")
        return len(intent_keys) > 0

    def responses_exist_in_redis(self, supermarket_id):
        response_keys = self.redis_client.keys(f"{supermarket_id}:response:*")
        return len(response_keys) > 0