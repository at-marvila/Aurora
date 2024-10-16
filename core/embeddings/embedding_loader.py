import logging
from core.embeddings.embedding_manager import EmbeddingManager
from integrations.redis_modules.redis_connection import RedisConnection

# Configura a conexão com o Redis
redis_conn = RedisConnection(
    host="redis-11850.c279.us-central1-1.gce.redns.redis-cloud.com",
    port=11850,
    password="j6BhSRwBhX8wO0bAIp8t1NmpMd1eW9Kf"
).get_client()
embedding_manager = EmbeddingManager(redis_conn)

def load_intent_embeddings(intents, supermarket_id):
    """Carrega embeddings de intents para cada frase individualmente no Redis."""
    if not embedding_manager.intents_exist_in_redis(supermarket_id):
        logging.warning(f"Embeddings de intents não encontrados para o supermercado {supermarket_id}. Executando o `embedding_processor.py`.")
        embedding_manager.load_intents_embeddings(intents, supermarket_id)

    intent_embeddings = {}
    for intent, data in intents.items():
        intent_embeddings[intent] = {}
        for phrase in data['triggers']['phrases']:
            key = f"{supermarket_id}:intent:{intent}:{phrase}"
            intent_embeddings[intent][phrase] = embedding_manager.check_or_insert_embedding(key, phrase)
    return intent_embeddings

def load_response_embeddings(responses, supermarket_id):
    """Carrega embeddings de responses já existentes no Redis ou cria novos."""
    embeddings = {}
    for category, response_list in responses.items():
        category_embeddings = []
        for response in response_list:
            # Verifica se o formato do response é uma string simples ou um dicionário com chave 'text'
            text = response if isinstance(response, str) else response.get("text", "")
            key = f"{supermarket_id}:response:{category}"
            embedding = embedding_manager.check_or_insert_embedding(key, text)
            category_embeddings.append(embedding)
        embeddings[category] = category_embeddings
    return embeddings