# core/components/embedding_handler.py

import numpy as np
from scipy.spatial.distance import cosine
from transformers import AutoTokenizer, AutoModel
import torch
import logging
import json
import yaml

class EmbeddingHandler:
    def __init__(self, config_manager, redis_data_retriever, context_manager, action_mapper):
        self.config = config_manager
        self.redis_data_retriever = redis_data_retriever
        self.context_manager = context_manager
        self.action_mapper = action_mapper
        self.tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        self.model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        self.action_embeddings = {}
        self.actions_config = self.load_actions_config()
        logging.debug("EmbeddingHandler inicializado e modelo carregado.")
        
        # Carregar todos os intents ao inicializar
        self.load_all_embeddings()

    def load_actions_config(self):
        """Carrega o arquivo actions.yaml para mapear contextos e textos associados a cada categoria."""
        with open("Aurora/data/intentions/actions.yaml", "r") as file:
            actions = yaml.safe_load(file)["actions"]
            
            actions_config = {}
            for item in actions:
                category = item["category"]
                for context_item in item.get("contexts", []):
                    context = context_item["context"]
                    actions_config[context] = category

            return actions_config

    def retrieve_category_from_context(self, full_context):
        """Recupera a categoria com base apenas no contexto principal (sem incluir intent)."""
        # Extraindo apenas a categoria base
        category_context_key = full_context.split(":")[0]
        category = self.actions_config.get(category_context_key)

        if not category:
            logging.warning(f"Categoria não encontrada para o contexto '{full_context}'")
        return category


    def load_all_embeddings(self):
        supermarket_key = self.config.get_supermarket_key()
        intent_keys = self.redis_data_retriever.keys(f"{supermarket_key}:intent:*")
        
        if intent_keys:
            for intent_key in intent_keys:
                *_, context, intent_name = intent_key.split(":")
                self.load_embedding_for_intent(intent_name, context)
            logging.debug("[load_all_embeddings] Todos os intents foram carregados do Redis para o cache.")
        else:
            logging.warning("[load_all_embeddings] Nenhum intent encontrado no Redis para o supermercado especificado.")

    def load_embedding_for_intent(self, intent_name, context):
        supermarket_key = self.config.get_supermarket_key()
        intent_key = f"{supermarket_key}:intent:{context}:{intent_name}"
        
        logging.debug(f"[load_embedding_for_intent] Intent key gerado: {intent_key}")
        
        embedding_data = self.redis_data_retriever.get(intent_key)
        logging.debug(f"[load_embedding_for_intent] Dados brutos recebidos do Redis para '{intent_key}': {embedding_data}")

        if embedding_data:
            try:
                self.action_embeddings[f"{context}:{intent_name}"] = json.loads(embedding_data)
                logging.debug(f"[load_embedding_for_intent] Embedding carregado para '{context}:{intent_name}': {self.action_embeddings[f'{context}:{intent_name}']}")
            except json.JSONDecodeError as e:
                logging.error(f"[load_embedding_for_intent] Erro ao decodificar JSON para '{intent_key}': {e}")
        else:
            logging.warning(f"[load_embedding_for_intent] Embedding para '{context}:{intent_name}' não encontrado no Redis para a chave '{intent_key}'.")

    def get_text_embedding(self, text):
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
        best_action_key = None

        for action_key, action_embedding in self.action_embeddings.items():
            similarity = 1 - cosine(input_embedding, np.array(action_embedding))
            logging.debug(f"[find_best_action] Similaridade para '{action_key}': {similarity}")
            if similarity > highest_similarity:
                highest_similarity, best_action_key = similarity, action_key

        if best_action_key:
            # Aqui, usamos o intent completo como "context:intent" para extrair categoria e contexto
            context, intent = best_action_key.split(":")
            category = self.retrieve_category_from_context(f"{context}:{intent}")
            logging.debug(f"[find_best_action] Melhor ação: {category} (Contexto: {context}, Intent: {intent}) com similaridade: {highest_similarity}")
            return category, context, intent, highest_similarity
        else:
            logging.warning("[find_best_action] Nenhuma ação encontrada com similaridade suficiente.")
            return None, None, None, highest_similarity


    def execute_best_action(self, input_embedding):
        category, context, intent, similarity = self.find_best_action(input_embedding)
        
        if category:
            result = self.action_mapper.execute_action(category)
            return result
        else:
            logging.warning("Nenhuma categoria correspondente encontrada.")
            return "Nenhuma ação correspondente encontrada."