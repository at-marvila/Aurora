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
        self.intents_config = self.load_intents_config()
        logging.debug("EmbeddingHandler inicializado e modelo carregado.")
        
        # Carregar todos os intents ao inicializar
        self.load_all_embeddings()

    def load_actions_config(self):
        with open("Aurora/data/intentions/actions.yaml", "r") as file:
            actions = yaml.safe_load(file)["actions"]
            actions_config = {}
            for item in actions:
                category = item["category"]
                for context_item in item.get("contexts", []):
                    context = context_item["context"]
                    actions_config[context] = category
            return actions_config

    def load_intents_config(self):
        with open("Aurora/data/intentions/intents.yaml", "r") as file:
            intents = yaml.safe_load(file)["intents"]
            return intents

    def find_function_by_intent_phrase(self, phrase):
        for intent_name, intent_data in self.intents_config.items():
            phrases = intent_data.get("triggers", {}).get("phrases", [])
            if phrase in phrases:
                function = intent_data.get("function")
                if function:
                    logging.debug(f"Intent '{intent_name}' encontrado para a frase '{phrase}' com a função '{function}'")
                    return function, intent_data.get("context")
        logging.warning(f"Frase '{phrase}' não corresponde a nenhum intent em intents.yaml")
        return None, None

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

    def format_embedding(self, embedding, length=5):
        """
        Formata o embedding para exibir apenas uma amostra dos primeiros e últimos valores,
        reduzindo o excesso de informações no log.
        """
        start = embedding[:length]
        end = embedding[-length:] if len(embedding) > length else []
        return f"{start} ... {end}"

    def load_embedding_for_intent(self, intent_name, context):
        supermarket_key = self.config.get_supermarket_key()
        intent_key = f"{supermarket_key}:intent:{context}:{intent_name}"
        
        embedding_data = self.redis_data_retriever.get(intent_key)
        if embedding_data:
            try:
                embedding = json.loads(embedding_data)
                formatted_embedding = self.format_embedding(embedding)  # Exibe uma amostra formatada
                self.action_embeddings[f"{context}:{intent_name}"] = embedding
                logging.debug(f"[load_embedding_for_intent] Embedding para '{intent_name}': {formatted_embedding}")
            except json.JSONDecodeError as e:
                logging.error(f"[load_embedding_for_intent] Erro ao decodificar JSON para '{intent_key}': {e}")
        else:
            logging.warning(f"[load_embedding_for_intent] Embedding para '{context}:{intent_name}' não encontrado no Redis para a chave '{intent_key}'.")

    def get_text_embedding(self, text):
        tokens = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():
            embeddings = self.model(**tokens).last_hidden_state.mean(dim=1)
        embedding_result = embeddings.flatten().numpy()
        formatted_embedding = self.format_embedding(embedding_result)  # Exibe uma amostra formatada
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
            context, intent = best_action_key.split(":")
            function, derived_context = self.find_function_by_intent_phrase(intent)
            if function:
                logging.debug(f"[find_best_action] Melhor ação: {function} (Contexto: {derived_context}, Intent: {intent}) com similaridade: {highest_similarity:.4f}")
                return function, derived_context, intent, highest_similarity
            else:
                logging.warning(f"[find_best_action] Função não encontrada para intent '{intent}'")
                return None, context, intent, highest_similarity
        else:
            logging.warning("[find_best_action] Nenhuma ação encontrada com similaridade suficiente.")
            return None, None, None, highest_similarity

    def execute_best_action(self, input_embedding):
        function, context, intent, similarity = self.find_best_action(input_embedding)
        
        if function:
            result = self.action_mapper.execute_action(function)
            return result
        else:
            logging.warning("Nenhuma função correspondente encontrada.")
            return "Nenhuma ação correspondente encontrada."