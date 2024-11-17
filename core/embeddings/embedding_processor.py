# core/embeddings/embedding_processor.py
import logging
from core.components.config_manager import ConfigManager
from core.embeddings.embedding_manager import EmbeddingManager
from utils.helpers.general_helpers import load_yaml_file

# Instância do ConfigManager e uso da conexão centralizada
config = ConfigManager(firebase_conn=None)  # Firebase pode ser passado se necessário
embedding_manager = EmbeddingManager(config.redis_conn)

def process_and_store_intents(supermarket_key):
    """Processa e armazena embeddings para cada frase das intents no Redis."""
    intents = load_yaml_file('C:/Sevent/Dev/Aurora/data/intentions/intents.yaml')
    for intent_name, intent_data in intents['intents'].items():
        context = intent_data.get('context', 'default')
        for phrase in intent_data['triggers']['phrases']:
            key = f"{supermarket_key}:intent:{context}:{intent_name}:{phrase}"  # Incluindo o intent e a frase na chave
            embedding_manager.check_or_insert_embedding(key, phrase)  # Usando a frase como entrada do embedding

def process_and_store_responses(supermarket_key):
    """Processa e armazena os embeddings das responses no Redis com a chave do supermercado."""
    responses = load_yaml_file('C:/Sevent/Dev/Aurora/data/intentions/responses.yaml')
    for response in responses['responses']:
        category = response['category']
        text = response['text']
        context = response.get('context', 'default')
        key = f"{supermarket_key}:response:{category}:{context}:{text}"  # Incluindo o texto na chave
        embedding_manager.check_or_insert_embedding(key, text)

def process_and_store_actions(supermarket_key):
    """Processa e armazena embeddings para cada ação no Redis."""
    actions = load_yaml_file('C:/Sevent/Dev/Aurora/data/intentions/actions.yaml')
    for action in actions['actions']:  # Iterando sobre a lista de ações
        category = action['category']
        for context_item in action.get('contexts', []):
            context = context_item['context']
            text = context_item['text']
            key = f"{supermarket_key}:action:{category}:{context}:{text}"  # Incluindo o texto na chave
            embedding_manager.check_or_insert_embedding(key, text)

def store_supermarket_metadata(supermarket_key, cost=1.0, priority="normal"):
    """Armazena metadados do supermercado, como custo de processamento e prioridade, no Redis."""
    metadata_key = f"{supermarket_key}:metadata"
    config.redis_conn.hset(metadata_key, mapping={
        "custo_processamento": cost,
        "prioridade": priority
    })
    logging.info(f"Metadados armazenados para {supermarket_key}: custo={cost}, prioridade={priority}")

if __name__ == "__main__":
    supermarket_config = load_yaml_file('C:/Sevent/Dev/Aurora/data/configs/supermarket_config.yaml')
    supermarket_id = supermarket_config['supermarket']['identifier_format'].format(
        name=supermarket_config['supermarket']['name'],
        state=supermarket_config['supermarket']['state'],
        city_acronym=supermarket_config['supermarket']['acronyms']['city'][supermarket_config['supermarket']['city']],
        district_acronym=supermarket_config['supermarket']['acronyms']['district'][supermarket_config['supermarket']['district']],
        store_number=supermarket_config['supermarket']['store_number']
    )
    
    # Cria a chave hierárquica do supermercado no formato regions:states:cities:supermarkets
    region = supermarket_config['supermarket']['region']
    state = supermarket_config['supermarket']['state']
    city = supermarket_config['supermarket']['city']
    supermarket_key = f"regions:{region}:states:{state}:cities:{city}:supermarkets:{supermarket_id}"
    
    # Processa e armazena intents, responses e actions
    process_and_store_intents(supermarket_key)
    process_and_store_responses(supermarket_key)
    process_and_store_actions(supermarket_key)
    
    # Armazena metadados do supermercado (custo de processamento e prioridade)
    store_supermarket_metadata(supermarket_key, cost=1.5, priority="alta")
    
    logging.info("Embeddings de intents, responses e metadados processados e armazenados com sucesso no Redis.")