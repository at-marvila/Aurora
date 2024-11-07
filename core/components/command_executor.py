# core/components/command_executor.py

import logging
from core.context.aurora_context import AuroraContext
from core.components.embedding_handler import EmbeddingHandler

class CommandExecutor:
    def __init__(self, aurora_context: AuroraContext, embedding_handler: EmbeddingHandler):
        self.config = aurora_context.config_manager
        self.embedding_handler = embedding_handler
        self.context_manager = aurora_context.context_manager
        self.redis_data_retriever = aurora_context.redis_data_retriever
        self.awaiting_greeting = True

        # Usa o ActionMapper diretamente do aurora_context
        self.action_mapper = aurora_context.action_mapper

    def execute_command(self, recognized_text):
        """Processa o texto reconhecido e executa a ação ou saudação apropriada."""
        if "oi aurora" in recognized_text.lower() and self.awaiting_greeting:
            self.awaiting_greeting = False
            logging.info("Aurora: Olá! Como posso ajudar?")
            print("Aurora: Olá! Como posso ajudar?")
            return

        # Obtenha o embedding do texto e execute a melhor ação diretamente
        input_embedding = self.embedding_handler.get_text_embedding(recognized_text)
        action_name, context, intent, similarity = self.embedding_handler.find_best_action(input_embedding)

        # Executa a ação encontrada e imprime o resultado
        if action_name:
            result = self.action_mapper.execute_action(action_name)
            print(f"Aurora: {result}")
        else:
            logging.warning("Nenhuma ação correspondente foi encontrada.")
            print("Aurora: Não consegui encontrar uma ação correspondente ao que foi dito.")