import logging
from utils.helpers.general_helpers import load_yaml_file, generate_supermarket_id
from integrations.redis_modules.redis_connection import RedisConnection
from core.embeddings.embedding_manager import EmbeddingManager

# Configura a conexão com o Redis usando a URL completa
redis_url = "redis://default:j6BhSRwBhX8wO0bAIp8t1NmpMd1eW9Kf@redis-11850.c279.us-central1-1.gce.redns.redis-cloud.com:11850"
redis_conn = RedisConnection(url=redis_url).get_client()
embedding_manager = EmbeddingManager(redis_conn)

def process_and_store_intents(supermarket_key):
    """Processa e armazena embeddings para cada frase das intents no Redis."""
    intents = load_yaml_file(r'C:/Sevent/Dev/Aurora/data/intentions/intent_actions.yaml')
    for intent_name, intent_data in intents['actions'].items():
        for phrase in intent_data['triggers']['phrases']:
            embedding_manager.check_or_insert_embedding(f"{supermarket_key}:intent:{intent_name}:{phrase}", phrase)

def process_and_store_responses(supermarket_key):
    """Processa e armazena os embeddings das responses no Redis com a chave do `supermarket`."""
    responses = load_yaml_file(r'C:/Sevent/Dev/Aurora/data/intentions/responses.yaml')
    for category, response_list in responses.items():
        if category == "actions":
            # Lida com subcategorias dentro de "actions"
            for action, action_responses in response_list.items():
                for response in action_responses:
                    if isinstance(response, dict) and "text" in response:
                        key = f"{supermarket_key}:response:actions:{action}"
                        embedding_manager.check_or_insert_embedding(key, response["text"])
                    else:
                        logging.warning(f"Formato inesperado em response (actions): {response}")
        else:
            # Lida com categorias normais como greetings, farewells, etc.
            for response in response_list:
                if isinstance(response, dict) and "text" in response:
                    key = f"{supermarket_key}:response:{category}"
                    embedding_manager.check_or_insert_embedding(key, response["text"])
                else:
                    logging.warning(f"Formato inesperado em response: {response}")

def store_supermarket_metadata(supermarket_key, cost=1.0, priority="normal"):
    """Armazena metadados do supermercado, como custo de processamento e prioridade, no Redis."""
    metadata_key = f"{supermarket_key}:metadata"
    redis_conn.hset(metadata_key, mapping={
        "custo_processamento": cost,
        "prioridade": priority
    })
    logging.info(f"Metadados armazenados para {supermarket_key}: custo={cost}, prioridade={priority}")

if __name__ == "__main__":
    supermarket_config = load_yaml_file(r'C:/Sevent/Dev/Aurora/data/configs/supermarket_config.yaml')
    supermarket_id = generate_supermarket_id(supermarket_config['supermarket'])
    
    # Cria a chave hierárquica do supermercado no formato regions:states:cities:supermarkets
    region = supermarket_config['supermarket']['region']
    state = supermarket_config['supermarket']['state']
    city = supermarket_config['supermarket']['city']
    supermarket_key = f"regions:{region}:states:{state}:cities:{city}:supermarkets:{supermarket_id}"
    
    # Processa e armazena intents e responses
    process_and_store_intents(supermarket_key)
    process_and_store_responses(supermarket_key)
    
    # Armazena metadados do supermercado (custo de processamento e prioridade)
    store_supermarket_metadata(supermarket_key, cost=1.5, priority="alta")
    
    logging.info("Embeddings de intents, responses e metadados processados e armazenados com sucesso no Redis.")