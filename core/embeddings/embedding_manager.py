import json
import logging
from transformers import AutoTokenizer, AutoModel
import torch

class EmbeddingManager:
    def __init__(self, redis_client):
        self.redis_client = redis_client
        self.tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        self.model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
            
    def create_embedding(self, text, key, context):
        # Gera o embedding do texto e armazena com a chave e contexto no Redis
        embedding = self.generate_embedding(text)
        self.redis.store_embedding(key, embedding, context=context)

    def _generate_embedding(self, text):
        """Gera o embedding para o texto fornecido."""
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():
            embeddings = self.model(**inputs).last_hidden_state.mean(dim=1)
        return embeddings[0].numpy()

    def check_or_insert_embedding(self, key, text):
        """Verifica ou insere um novo embedding no Redis."""
        existing_embedding = self.redis_client.get(key)
        if existing_embedding:
            try:
                # Retorna o embedding existente se já armazenado
                return json.loads(existing_embedding)
            except json.JSONDecodeError as e:
                logging.warning(f"Erro ao carregar o embedding existente para a chave '{key}': {e}")
        
        # Gera e insere um novo embedding, se não existir
        embedding = self._generate_embedding(text)
        self.redis_client.set(key, json.dumps(embedding.tolist()))
        logging.info(f"Novo embedding gerado e armazenado para a chave: {key}")
        return embedding