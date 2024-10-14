import logging
from core.embeddings.embedding_manager import EmbeddingManager
from integrations.redis_modules.redis_connection import RedisConnection

# Configura a conexão com o Redis usando a URL completa com as credenciais
redis_conn = RedisConnection(
    host="redis-11850.c279.us-central1-1.gce.redns.redis-cloud.com",
    port=11850,
    password="j6BhSRwBhX8wO0bAIp8t1NmpMd1eW9Kf"
).get_client()

embedding_manager = EmbeddingManager(redis_conn)

def load_intent_embeddings():
    """Carrega embeddings de intents já existentes no Redis."""
    if not embedding_manager.intents_exist_in_redis():
        logging.warning("Embeddings de intents não encontrados no Redis. Execute o `embedding_processor.py`.")
    return embedding_manager.load_intents_embeddings()

def load_response_embeddings():
    """Carrega embeddings de responses já existentes no Redis."""
    if not embedding_manager.responses_exist_in_redis():
        logging.warning("Embeddings de responses não encontrados no Redis. Execute o `embedding_processor.py`.")
    return embedding_manager.load_responses_embeddings()