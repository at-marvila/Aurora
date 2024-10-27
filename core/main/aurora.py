from core.components.config_manager import ConfigManager
from core.components.embedding_handler import EmbeddingHandler
from core.components.command_executor import CommandExecutor
from core.components.interaction_handler import InteractionHandler
from core.components.context_manager import ContextManager
from core.components.redis_data_retriever import RedisDataRetriever
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
        self.supermarket_key = config.get_supermarket_key()  # Chave única para o supermercado
        self.embedding_handler = EmbeddingHandler(config, redis_data_retriever, context_manager)
        self.command_executor = CommandExecutor(config, self.embedding_handler, context_manager, redis_data_retriever)
        self.interaction_handler = InteractionHandler(config, self.command_executor)

    def start(self):
        """Inicia o loop de reconhecimento de voz e interação com o usuário."""
        self.interaction_handler.recognize_speech()

if __name__ == "__main__":
    aurora = AuroraAI()
    aurora.start()