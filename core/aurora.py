import os
import logging
import random
import speech_recognition as srcd
from integrations.firebase.connections import FirebaseConnection
from utils.audio.audio_utils import listen_and_save
from utils.logging.logging_config import setup_logging
from actions.register.register_employee import RegisterEmployee
from utils.helpers.general_helpers import load_yaml_file, generate_supermarket_id
from transformers import AutoModel, AutoTokenizer
from scipy.spatial.distance import cosine
import numpy as np
import torch
from core.embeddings.embedding_loader import load_intent_embeddings, load_response_embeddings
from integrations.redis_modules.redis_connection import RedisConnection

# Configuração de logging e inicialização do Firebase
setup_logging()
firebase_conn = FirebaseConnection(
    "C:\\Sevent\\Connections\\Connecion firebase\\firebase-connection.json",
    'sevent-7197f.appspot.com'
)

class AuroraAI:
    def __init__(self):
        """Inicializa a IA Aurora, carregando configurações e inicializando classes essenciais."""
        self.recognizer = srcd.Recognizer()
        self.intent_actions = load_yaml_file('C:/Sevent/Dev/Aurora/data/intentions/intent_actions.yaml')
        self.responses = load_yaml_file('C:/Sevent/Dev/Aurora/data/intentions/responses.yaml')
        self.supermarket_config = load_yaml_file('C:/Sevent/Dev/Aurora/data/configs/supermarket_config.yaml')
        
        # Configuração de registro de colaboradores
        self.register_employee_instance = RegisterEmployee(self, firebase_conn, self.supermarket_config)

        # Configuração do Redis
        redis_url = "redis://default:j6BhSRwBhX8wO0bAIp8t1NmpMd1eW9Kf@redis-11850.c279.us-central1-1.gce.redns.redis-cloud.com:11850"
        self.redis_conn = RedisConnection(url=redis_url).client
        
        # Configura chave hierárquica de supermercado
        region = self.supermarket_config['supermarket']['region']
        state = self.supermarket_config['supermarket']['state']
        city = self.supermarket_config['supermarket']['city']
        supermarket_id = generate_supermarket_id(self.supermarket_config['supermarket'])
        self.supermarket_key = f"regions:{region}:states:{state}:cities:{city}:supermarkets:{supermarket_id}"

        # Configurações do modelo para embeddings
        self.tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        self.model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

        # Carrega embeddings de intents e responses do Redis
        self.action_embeddings = load_intent_embeddings(self.intent_actions['actions'], self.supermarket_key)
        self.response_embeddings = load_response_embeddings(self.responses, self.supermarket_key)

    def get_text_embedding(self, text):
        """Gera um embedding 1-D para o texto fornecido usando transformers."""
        tokens = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():
            embeddings = self.model(**tokens).last_hidden_state.mean(dim=1)
        return embeddings.flatten().numpy()  # Garante que é 1-D

    def find_best_action(self, input_embedding):
        """Encontra a ação mais similar no Redis comparando embeddings."""
        highest_similarity = 0
        best_action = None
        input_embedding = np.array(input_embedding).flatten()  # Garante que é 1-D

        for action_key, action_embedding in self.action_embeddings.items():
            action_embedding = np.array(action_embedding).flatten()  # Garante que é 1-D

            # Verificação para evitar erros de alinhamento
            if input_embedding.shape == action_embedding.shape:
                similarity = 1 - cosine(input_embedding, action_embedding)
                if similarity > highest_similarity:
                    highest_similarity, best_action = similarity, action_key
            else:
                logging.warning(f"Dimensão incompatível entre input e action embedding para a ação '{action_key}'")
        return best_action, highest_similarity

    def execute_command(self, recognized_text=None):
        """Executa um comando baseado no texto reconhecido usando embeddings."""
        logging.debug(f"Texto reconhecido: {recognized_text}")
        input_embedding = self.get_text_embedding(recognized_text)
        
        # Busca a ação mais similar
        best_action, highest_similarity = self.find_best_action(input_embedding)
        
        if best_action and highest_similarity > 0.8:  # Threshold de similaridade
            # Executa a função correspondente à ação encontrada
            function_name = self.intent_actions['actions'][best_action]['function']
            command_function = getattr(self.register_employee_instance, function_name, None) or getattr(self, function_name, None)
            
            if callable(command_function):
                logging.info(f"Executando função '{function_name}' para ação '{best_action}'")
                command_function(recognized_text=recognized_text)
            else:
                logging.warning(f"Função '{function_name}' não encontrada.")
        else:
            response = self.get_response('default_response')
            logging.warning(f"Aurora: {response}")

    def get_response(self, category, action=None, **kwargs):
        """Obtém uma resposta com base na categoria e ação, substituindo placeholders."""
        response = (
            random.choice(self.responses.get(category, self.responses['default_response']))
            if not action else random.choice(self.responses['actions'].get(action, self.responses['default_response']))
        )
        response_text = response['text'] if isinstance(response, dict) and 'text' in response else response
        if kwargs:
            return response_text.format(**kwargs)  # Permite passar variáveis dinâmicas para a resposta
        return response_text.format(nome="Usuário")  # Placeholder padrão para o nome

    def recognize_speech(self):
        """Reconhece comandos de voz e gerencia a interação de saudação e encerramento."""
        awaiting_greeting = True
        while True:
            logging.info("Aurora: Aguardando saudação 'Oi Aurora' para iniciar..." if awaiting_greeting else "Aurora: Estou ouvindo...")
            try:
                recognized_text, audio = listen_and_save(self.recognizer, prompt="Você: ", timeout=10)
                if recognized_text:
                    if "oi aurora" in recognized_text.lower() and awaiting_greeting:
                        awaiting_greeting = False
                        self.handle_greeting(audio)
                        response = self.get_response('greetings', nome="Usuário")
                        logging.info(f"Aurora: {response}")
                        self.interaction_loop()
                    elif "aurora desligar" in recognized_text.lower():
                        logging.info(self.get_response('farewells'))
                        break
                    elif not awaiting_greeting:
                        self.execute_command(recognized_text=recognized_text)
            except srcd.WaitTimeoutError:
                logging.info("Aurora: Continuo aguardando a saudação 'Oi Aurora'...")
            except Exception as e:
                logging.error(f"Aurora: Houve um erro inesperado: {e}")

    def handle_greeting(self, audio):
        """Processa a saudação e gera o vetor de voz."""
        try:
            self.voice_vector = self.register_employee_instance.voice_recognition.generate_embedding(audio.get_wav_data())
        except ValueError as e:
            logging.error(f"Erro ao gerar o vetor de voz: {e}")

    def interaction_loop(self):
        """Loop de interação até que a inatividade exceda o limite."""
        inactivity_counter = 0
        while True:
            try:
                recognized_text, _ = listen_and_save(self.recognizer, prompt="Você: ", timeout=5)
                if recognized_text:
                    inactivity_counter = 0
                    self.execute_command(recognized_text=recognized_text)
                else:
                    inactivity_counter += 1
                    if inactivity_counter >= 4:
                        logging.info("Aurora: Sessão encerrada por inatividade.")
                        self.handle_session_end()
                        break
            except srcd.WaitTimeoutError:
                inactivity_counter += 1
                if inactivity_counter >= 4:
                    logging.info("Aurora: Sessão encerrada por inatividade.")
                    self.handle_session_end()
                    break
            except Exception as e:
                logging.error(f"Aurora: Houve um erro inesperado: {e}")

    def handle_session_end(self):
        """Encerra a sessão atual de interação."""
        logging.info("Aurora: Encerrando e salvando a sessão atual...")

if __name__ == "__main__":
    aurora = AuroraAI()
    aurora.recognize_speech()