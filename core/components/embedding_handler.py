import numpy as np
from scipy.spatial.distance import cosine
from transformers import AutoTokenizer, AutoModel
import torch
import logging
import json
import yaml
from utils.helpers.general_helpers import format_embedding
from core.embeddings.embedding_processor import (
    process_and_store_intents,
    process_and_store_responses,
    process_and_store_actions
)

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
        self.intents_config = self.load_intents_config()
        logging.debug("EmbeddingHandler inicializado e modelo carregado.")

        # Verifica e cria embeddings ausentes
        self.ensure_embeddings_exist()
        # Carrega todos os embeddings
        self.load_all_embeddings()

    def load_actions_config(self):
        """Carrega as configurações de ações a partir do arquivo actions.yaml."""
        with open("C:\\Sevent\\Dev\\Aurora\\data\\intentions\\actions.yaml", "r") as file:
            actions = yaml.safe_load(file)["actions"]
            actions_config = {}
            for item in actions:
                category = item["category"]
                for context_item in item.get("contexts", []):
                    context = context_item["context"]
                    actions_config[context] = category
            return actions_config

    def load_intents_config(self):
        """Carrega as configurações de intents a partir do arquivo intents.yaml."""
        with open("C:\\Sevent\\Dev\\Aurora\\data\\intentions\\intents.yaml", "r") as file:
            intents = yaml.safe_load(file)["intents"]
            return intents

    def ensure_embeddings_exist(self):
        """Verifica se embeddings estão presentes e os cria, caso não existam."""
        supermarket_key = self.config.get_supermarket_key()
        if not supermarket_key:
            logging.error("Erro: Chave do supermercado não foi gerada.")
            return

        intent_keys = self.redis_data_retriever.keys(f"{supermarket_key}:intent:*")
        if not intent_keys:
            logging.warning("Nenhum embedding encontrado no Redis. Processando novos embeddings.")
            self._process_and_store_embeddings(supermarket_key)
        else:
            logging.info(f"Embeddings existentes encontrados para o supermercado '{supermarket_key}'.")

    def _process_and_store_embeddings(self, supermarket_key):
        """Processa e armazena todos os embeddings para intents, responses e actions."""
        process_and_store_intents(supermarket_key)
        process_and_store_responses(supermarket_key)
        process_and_store_actions(supermarket_key)
        logging.info(f"Embeddings processados e armazenados para o supermercado: {supermarket_key}")

    def load_all_embeddings(self):
        """Carrega embeddings de intents do Redis no cache."""
        supermarket_key = self.config.get_supermarket_key()
        intent_keys = self.redis_data_retriever.keys(f"{supermarket_key}:intent:*")
        for intent_key in intent_keys:
            key_parts = intent_key.split(":")
            if len(key_parts) >= 6:
                # Ignoramos as partes iniciais da chave e pegamos os segmentos relevantes.
                _, _, _, context, intent_name, *phrase_parts = key_parts[4:]
                phrase = ":".join(phrase_parts)
                self.load_embedding_for_intent(intent_name, context, phrase, intent_key)
            else:
                logging.warning(f"Chave de intent inválida encontrada: {intent_key}")
        logging.debug("[load_all_embeddings] Todos os intents foram carregados do Redis.")

    def load_embedding_for_intent(self, intent_name, context, phrase, intent_key):
        """Carrega embeddings específicos para intents."""
        embedding_data = self.redis_data_retriever.get(intent_key)
        if embedding_data:
            try:
                embedding = json.loads(embedding_data)
                self.action_embeddings[f"{context}:{intent_name}:{phrase}"] = embedding
                logging.debug(f"[load_embedding_for_intent] Embedding para frase '{phrase}' carregado.")
            except json.JSONDecodeError as e:
                logging.error(f"[load_embedding_for_intent] Erro ao decodificar JSON para '{intent_key}': {e}")
        else:
            logging.warning(f"[load_embedding_for_intent] Embedding para '{intent_key}' não encontrado no Redis.")

    def get_text_embedding(self, text):
        tokens = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():
            embeddings = self.model(**tokens).last_hidden_state.mean(dim=1)
        embedding_result = embeddings.flatten().numpy()
        formatted_embedding = format_embedding(embedding_result)
        logging.debug(f"[get_text_embedding] Embedding gerado para '{text}': {formatted_embedding}")
        return embedding_result

    def find_best_action(self, input_embedding):
        highest_similarity = 0
        best_action_key = None

        logging.debug("Iniciando análise de similaridade dos intents:")
        for action_key, action_embedding in self.action_embeddings.items():
            similarity = 1 - cosine(input_embedding, np.array(action_embedding))
            logging.debug(f"Similaridade para '{action_key}': {similarity:.4f}")
            if similarity > highest_similarity:
                highest_similarity, best_action_key = similarity, action_key

        if best_action_key:
            parts = best_action_key.split(":")
            if len(parts) >= 3:
                context, intent_name, phrase = parts[-3], parts[-2], parts[-1]

                function, derived_context = self.find_function_by_intent_name(intent_name)
                if function:
                    logging.debug(f"[find_best_action] Melhor ação: {function} (Contexto: {derived_context}, Intent: {intent_name}) com similaridade: {highest_similarity:.4f}")
                    return function, derived_context, intent_name, highest_similarity
                else:
                    logging.warning(f"[find_best_action] Função não encontrada para intent '{intent_name}'")
                    return None, context, intent_name, highest_similarity
            else:
                logging.warning("[find_best_action] Estrutura da chave inválida.")
                return None, None, None, highest_similarity
        else:
            logging.warning("[find_best_action] Nenhuma ação encontrada com similaridade suficiente.")
            return None, None, None, highest_similarity

    def find_function_by_intent_name(self, intent_name):
        intent_data = self.intents_config.get(intent_name)
        if intent_data:
            function = intent_data.get("function")
            context = intent_data.get("context")
            logging.debug(f"Intent '{intent_name}' encontrado com a função '{function}'")
            return function, context
        else:
            logging.warning(f"Intent '{intent_name}' não encontrado em intents.yaml")
            return None, None

    def execute_best_action(self, input_embedding):
        function, context, intent, similarity = self.find_best_action(input_embedding)
        if function:
            result = self.action_mapper.execute_action(function)
            return result
        else:
            logging.warning("Nenhuma função correspondente encontrada.")
            return "Nenhuma ação correspondente encontrada."