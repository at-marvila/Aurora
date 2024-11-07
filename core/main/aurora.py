# c:\Sevent\Dev\Aurora\core\main\aurora.py

from core.components.config_manager import ConfigManager
from core.context.aurora_context import AuroraContext
from core.components.embedding_handler import EmbeddingHandler
from core.components.command_executor import CommandExecutor
from core.components.interaction_handler import InteractionHandler
from core.components.context_manager import ContextManager
from core.components.redis_data_retriever import RedisDataRetriever
from core.components.action_mapper import ActionMapper
from utils.logging.logging_config import setup_logging
from integrations.firebase.connections import FirebaseConnection

# Configuração de logging
setup_logging()

# Inicializa FirebaseConnection, ConfigManager, ContextManager, e RedisDataRetriever
firebase_conn = FirebaseConnection(r"C:\Sevent\Connections\Connecion firebase\firebase-connection.json", 'sevent-7197f.appspot.com')
config = ConfigManager(firebase_conn)
context_manager = ContextManager()
redis_data_retriever = RedisDataRetriever(config.redis_conn)

class AuroraAI:
    def __init__(self):
        # Inicializa o contexto Aurora e passa a própria instância como aurora_instance
        self.aurora_context = AuroraContext(config, context_manager, redis_data_retriever, firebase_conn, self)

        # Inicializa o ActionMapper com `self`
        action_mapper = ActionMapper(
            context_manager,
            config,
            self,  # Passa a própria instância
            firebase_conn,
            self.aurora_context.supermarket_config
        )

        # Passe o action_mapper para o EmbeddingHandler
        self.embedding_handler = EmbeddingHandler(config, redis_data_retriever, context_manager, action_mapper)

        # Passe o aurora_context e o embedding_handler para o CommandExecutor
        self.command_executor = CommandExecutor(self.aurora_context, self.embedding_handler)

        # Inicialize o InteractionHandler
        self.interaction_handler = InteractionHandler(config, self.command_executor)

    def start(self):
        """Inicia o loop de reconhecimento de voz e interação com o usuário."""
        self.interaction_handler.recognize_speech()

if __name__ == "__main__":
    aurora = AuroraAI()
    aurora.start()