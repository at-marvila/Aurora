# core/components/config_manager.py

import yaml
import logging
from integrations.firebase.connections import FirebaseConnection
from integrations.redis_modules.redis_connection import RedisConnection

class ConfigManager:
    def __init__(self, firebase_conn):
        self.firebase_conn = firebase_conn
        self.supermarket_config = self.load_yaml_file('C:/Sevent/Dev/Aurora/data/configs/supermarket_config.yaml')
        self.intent_actions = self.load_yaml_file('C:/Sevent/Dev/Aurora/data/intentions/intents.yaml')
        self.responses = self.load_yaml_file('C:/Sevent/Dev/Aurora/data/intentions/responses.yaml')
        
        # Verificação dos carregamentos
        if not self.intent_actions:
            logging.error("Erro: 'intent_actions' não foi carregado corretamente.")
        if not self.responses:
            logging.error("Erro: 'responses' não foi carregado corretamente.")
            
        # Inicializa a conexão Redis
        self.redis_url = "redis://default:j6BhSRwBhX8wO0bAIp8t1NmpMd1eW9Kf@redis-11850.c279.us-central1-1.gce.redns.redis-cloud.com:11850"
        self.redis_conn = RedisConnection(url=self.redis_url).get_client()

    def load_yaml_file(self, file_path):
        """Carrega um arquivo YAML e retorna o conteúdo como dicionário."""
        try:
            with open(file_path, 'r') as file:
                return yaml.safe_load(file)
        except Exception as e:
            logging.error(f"Erro ao carregar {file_path}: {e}")
            return {}
        
    def get_supermarket_key(self):
        """Gera a chave identificadora do supermercado a partir das configurações."""
        try:
            supermarket = self.supermarket_config.get('supermarket')
            if not supermarket:
                logging.error("Erro: Configuração 'supermarket' está ausente no arquivo.")
                return None

            name = supermarket.get('name')
            region = supermarket.get('region', 'default_region')
            state = supermarket.get('state', 'default_state')
            city = supermarket.get('city', 'default_city')
            district = supermarket.get('district', 'default_district')
            store_number = supermarket.get('store_number', '000')
            city_acronym = supermarket.get('acronyms', {}).get('city', {}).get(city, city[:3].upper())
            district_acronym = supermarket.get('acronyms', {}).get('district', {}).get(district, district[:3].upper())
            identifier_format = supermarket.get('identifier_format')

            if not identifier_format:
                logging.error("Erro: 'identifier_format' está ausente na configuração do supermercado.")
                return None

            supermarket_id = identifier_format.format(
                name=name,
                state=state,
                city_acronym=city_acronym,
                district_acronym=district_acronym,
                store_number=store_number
            )

            return f"regions:{region}:states:{state}:cities:{city}:supermarkets:{supermarket_id}"

        except KeyError as e:
            logging.error(f"Erro ao gerar a chave do supermercado: chave faltando '{e.args[0]}'")
            return None