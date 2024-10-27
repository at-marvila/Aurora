# core/components/embedding_handler.py

import numpy as np
from scipy.spatial.distance import cosine
from transformers import AutoTokenizer, AutoModel
import torch
import logging
import json

class EmbeddingHandler:
    def __init__(self, config_manager, redis_data_retriever, context_manager):
        self.config = config_manager
        self.redis_data_retriever = redis_data_retriever
        self.context_manager = context_manager
        self.tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        self.model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        self.action_embeddings = {}  # Inicialmente vazio
        logging.debug("EmbeddingHandler inicializado e modelo carregado.")
        
        # Carregar todos os intents ao inicializar
        self.load_all_embeddings()

    def load_all_embeddings(self):
        """Carrega todos os embeddings de intents do Redis."""
        supermarket_key = self.config.get_supermarket_key()
        intent_keys = self.redis_data_retriever.keys(f"{supermarket_key}:intent:*")
        
        if intent_keys:
            for intent_key in intent_keys:
                # Separação de contexto e nome do intent a partir da chave
                *_, context, intent_name = intent_key.split(":")
                self.load_embedding_for_intent(intent_name, context)
            logging.debug("[load_all_embeddings] Todos os intents foram carregados do Redis para o cache.")
        else:
            logging.warning("[load_all_embeddings] Nenhum intent encontrado no Redis para o supermercado especificado.")

    def load_embedding_for_intent(self, intent_name, context):
        """Carrega o embedding de uma intenção específica com base no contexto."""
        supermarket_key = self.config.get_supermarket_key()
        # Construção correta da chave do intent
        intent_key = f"{supermarket_key}:intent:{context}:{intent_name}"
        
        logging.debug(f"[load_embedding_for_intent] Intent key gerado: {intent_key}")
        
        embedding_data = self.redis_data_retriever.get(intent_key)
        logging.debug(f"[load_embedding_for_intent] Dados brutos recebidos do Redis para '{intent_key}': {embedding_data}")

        if embedding_data:
            try:
                # Armazenando o embedding no cache com chave única para intent e contexto
                self.action_embeddings[f"{context}:{intent_name}"] = json.loads(embedding_data)
                logging.debug(f"[load_embedding_for_intent] Embedding carregado para '{context}:{intent_name}': {self.action_embeddings[f'{context}:{intent_name}']}")
            except json.JSONDecodeError as e:
                logging.error(f"[load_embedding_for_intent] Erro ao decodificar JSON para '{intent_key}': {e}")
        else:
            logging.warning(f"[load_embedding_for_intent] Embedding para '{context}:{intent_name}' não encontrado no Redis para a chave '{intent_key}'.")

    def get_text_embedding(self, text):
        """Gera o embedding de um texto usando o modelo pré-treinado."""
        tokens = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():
            embeddings = self.model(**tokens).last_hidden_state.mean(dim=1)
        embedding_result = embeddings.flatten().numpy()
        
        logging.debug(f"[get_text_embedding] Embedding gerado para o texto '{text}': {embedding_result}")
        return embedding_result

    def find_best_action(self, input_embedding):
        """Encontra a ação com maior similaridade ao embedding de entrada."""
        
        logging.debug(f"[find_best_action] Intents carregados para comparação: {list(self.action_embeddings.keys())}")
        
        highest_similarity = 0
        best_action = None

        for action_key, action_embedding in self.action_embeddings.items():
            similarity = 1 - cosine(input_embedding, np.array(action_embedding))
            logging.debug(f"[find_best_action] Similaridade para '{action_key}': {similarity}")
            if similarity > highest_similarity:
                highest_similarity, best_action = similarity, action_key
        
        logging.debug(f"[find_best_action] Melhor ação: {best_action} com similaridade: {highest_similarity}")
        return best_action, highest_similarity