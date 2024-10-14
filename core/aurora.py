import os
import logging
import random
import asyncio
import speech_recognition as srcd
from integrations.firebase.connections import FirebaseConnection
from utils.audio.audio_utils import listen_and_save_async
from utils.logging.logging_config import setup_logging
from actions.register.register_employee import RegisterEmployee
from utils.helpers.general_helpers import load_yaml_file
from transformers import AutoModel, AutoTokenizer
from scipy.spatial.distance import cosine
import torch

# Configuração do logging e conexão com o Firebase
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
        self.register_employee_instance = RegisterEmployee(self, firebase_conn, self.supermarket_config)
        self.inactivity_counter = 0
        self.voice_vector = None  # Armazena o vetor de voz após "Oi Aurora"
        
        # Configura modelo e tokenizer para embeddings
        self.model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        self.tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        
        # Pré-carrega embeddings de actions e responses
        from core.embeddings.embedding_loader import load_intent_embeddings, load_response_embeddings
        self.action_embeddings = load_intent_embeddings(self.intent_actions['actions'])
        self.response_embeddings = load_response_embeddings(self.responses)

    async def get_text_embedding(self, text):
        """Gera um embedding para o texto fornecido usando transformers."""
        tokens = self.tokenizer(text, return_tensors="pt")
        with torch.no_grad():
            embeddings = self.model(**tokens).last_hidden_state.mean(dim=1).detach().numpy()
        return embeddings[0]

    def get_response(self, category, action=None, **kwargs):
        """Obtém uma resposta com base na categoria e ação, permitindo argumentos adicionais."""
        response = self.responses.get('actions', {}).get(action) or random.choice(self.responses.get(category, self.responses['default_response']))
        if kwargs:
            return response.format(**kwargs)  # Permite passar variáveis dinâmicas para a resposta
        return response

    async def handle_greeting(self, audio):
        """Processa a saudação e gera o vetor de voz."""
        try:
            self.voice_vector = await self.register_employee_instance.voice_recognition.generate_embedding(audio.get_wav_data())
            response = self.get_response('greetings')
            logging.info(f"Aurora: {response}")
        except ValueError as e:
            logging.error(f"Erro ao gerar o vetor de voz: {e}")

    async def execute_command(self, recognized_text=None, audio=None):
        """Executa um comando baseado no texto reconhecido usando embeddings para identificar a ação."""
        logging.debug(f"Texto reconhecido: {recognized_text}")
        input_embedding = await self.get_text_embedding(recognized_text)
        
        # Encontra a ação com maior similaridade ao texto reconhecido
        best_action, highest_similarity = None, float('-inf')
        for action, action_embedding in self.action_embeddings.items():
            similarity = 1 - cosine(input_embedding, action_embedding)
            if similarity > highest_similarity:
                best_action, highest_similarity = action, similarity
        
        if best_action and highest_similarity > 0.7:  # Threshold de similaridade
            function_name = self.intent_actions['actions'][best_action]['function']
            command_function = getattr(self.register_employee_instance, function_name, None) or getattr(self, function_name, None)
            
            if callable(command_function):
                logging.info(f"Executando função '{function_name}' para ação '{best_action}'")
                await command_function(recognized_text=recognized_text, audio=audio)
            else:
                logging.warning(f"Função '{function_name}' não encontrada.")
        else:
            logging.warning(f"Aurora: {self.get_response('default_response')}")

    async def recognize_speech(self):
        """Reconhece comandos de voz e gerencia a interação de saudação e encerramento."""
        while True:
            logging.info("Aurora: Aguardando saudação 'Oi Aurora' para iniciar...")
            try:
                recognized_text, audio = await listen_and_save_async(self.recognizer, prompt="Você: ", timeout=10)
                if recognized_text:
                    if "oi aurora" in recognized_text:
                        await self.handle_greeting(audio)
                        await self.interaction_loop()
                    elif "aurora desligar" in recognized_text:
                        logging.info(self.get_response('farewells'))
                        break
            except srcd.WaitTimeoutError:
                logging.info("Aurora: Continuo aguardando a saudação 'Oi Aurora'...")
            except Exception as e:
                logging.error(f"Aurora: Houve um erro inesperado: {e}")

    async def interaction_loop(self):
        """Loop de interação até que a inatividade exceda o limite."""
        self.inactivity_counter = 0
        while True:
            try:
                recognized_text, audio = await listen_and_save_async(self.recognizer, prompt="Você: ", timeout=5)
                if recognized_text:
                    self.inactivity_counter = 0

                    if "aurora, por do sol" in recognized_text:
                        logging.info(self.get_response('farewells'))
                        await self.handle_session_end()
                        break

                    await self.execute_command(recognized_text=recognized_text, audio=audio)
                else:
                    self.inactivity_counter += 1

                    if self.inactivity_counter == 2:
                        prompt = self.get_response('inactive_prompt')
                        logging.info(f"Aurora: {prompt}")

                    elif self.inactivity_counter >= 4:
                        logging.info("Aurora: Sessão encerrada por inatividade.")
                        await self.handle_session_end()
                        break

            except srcd.WaitTimeoutError:
                self.inactivity_counter += 1
                if self.inactivity_counter == 2:
                    prompt = self.get_response('inactive_prompt')
                    logging.info(f"Aurora: {prompt}")
                elif self.inactivity_counter >= 4:
                    logging.info("Aurora: Sessão encerrada por inatividade.")
                    await self.handle_session_end()
                    break
            except Exception as e:
                logging.error(f"Aurora: Houve um erro inesperado: {e}")

    async def handle_session_end(self):
        """Encerra a sessão atual de interação."""
        logging.info("Aurora: Encerrando e salvando a sessão atual...")

if __name__ == "__main__":
    aurora = AuroraAI()
    asyncio.run(aurora.recognize_speech())