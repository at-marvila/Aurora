# core/context/aurora_context.py

import logging
from core.components.config_manager import ConfigManager
from core.components.context_manager import ContextManager
from core.components.redis_data_retriever import RedisDataRetriever
from core.components.action_mapper import ActionMapper
from integrations.firebase.connections import FirebaseConnection

class AuroraContext:
    def __init__(self, config_manager: ConfigManager, context_manager: ContextManager, redis_data_retriever: RedisDataRetriever, firebase_conn: FirebaseConnection, aurora_instance):
        self.config_manager = config_manager
        self.context_manager = context_manager
        self.redis_data_retriever = redis_data_retriever
        self.firebase_conn = firebase_conn
        self.supermarket_key = self.config_manager.get_supermarket_key()

        # Dados adicionais
        self.supermarket_config = self.config_manager.supermarket_config
        self.intent_actions = self.config_manager.intent_actions
        self.responses = self.config_manager.responses

        # Inicialize o ActionMapper com a instância real de aurora_instance
        self.action_mapper = ActionMapper(
            context_manager,
            config_manager,
            aurora_instance,  # Corrigido para passar a instância correta
            firebase_conn,
            self.supermarket_config
        )

    def get_supermarket_key(self):
        """Retorna a chave do supermercado do contexto."""
        return self.supermarket_key

    # Método adicional para obter configurações de intents ou respostas
    def get_intent_response(self, intent):
        return self.responses.get(intent, "Resposta padrão não encontrada.")