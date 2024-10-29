# core/components/command_executor.py

import logging
from core.components.action_mapper import ActionMapper

class CommandExecutor:
    def __init__(self, config_manager, embedding_handler, context_manager, redis_data_retriever):
        self.config = config_manager
        self.embedding_handler = embedding_handler
        self.context_manager = context_manager
        self.action_mapper = ActionMapper(context_manager, config_manager)
        self.redis_data_retriever = redis_data_retriever
        self.awaiting_greeting = True

    def execute_command(self, recognized_text):
        """Processa o texto reconhecido e executa a ação ou saudação apropriada."""
        if "oi aurora" in recognized_text.lower() and self.awaiting_greeting:
            self.awaiting_greeting = False
            logging.info("Aurora: Olá! Como posso ajudar?")
            print("Aurora: Olá! Como posso ajudar?")
            return

        intent_context, intent_name = self.detect_intent_context(recognized_text)
        if not intent_context:
            logging.warning("Nenhum contexto encontrado para o comando.")
            print("Aurora: Comando não reconhecido.")
            return

        action_category = self.embedding_handler.retrieve_category_from_context(intent_context)
        if action_category:
            response = self.action_mapper.execute_action(action_category)
            print(f"Aurora: {response}")
        else:
            logging.warning("Nenhuma ação correspondente foi encontrada.")
            print("Aurora: Não consegui encontrar uma ação correspondente ao que foi dito.")
    
    def detect_intent_context(self, text):
        """Determina o contexto da intenção com base no texto reconhecido."""
        input_embedding = self.embedding_handler.get_text_embedding(text)
        context, _ = self.embedding_handler.find_best_action(input_embedding)
        return context