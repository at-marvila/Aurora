import os
import yaml
import logging
import random
import speech_recognition as srcd
from fuzzywuzzy import fuzz
from integrations.firebase.connections import FirebaseConnection
from utils.firebase.firebase_utils import upload_to_firebase
from utils.audio.audio_utils import save_audio_wav, listen_and_save
from utils.logging.logging_config import setup_logging
from actions.register.register_employee import RegisterEmployee
from integrations.firebase.firestore_operations import FirestoreOperations

# Configura o logging
setup_logging()

# Configurar a conexão com o Firebase
firebase_conn = FirebaseConnection("C:\\Sevent\\Connections\\Connecion firebase\\firebase-connection.json", 'sevent-7197f.appspot.com')

class AuroraAI:
    def __init__(self):
        self.recognizer = srcd.Recognizer()
        self.intent_actions = self.load_yaml_file('../data/intent_actions.yaml')
        self.responses = self.load_yaml_file('../data/responses.yaml')
        self.supermarket_config = self.load_yaml_file('../data/configs/supermarket_config.yaml')
        self.register_employee_instance = RegisterEmployee(self, firebase_conn, self.supermarket_config)
        self.inactivity_counter = 0
        self.voice_vector = None  # Armazena o vetor de voz após "Oi Aurora"

    def load_yaml_file(self, relative_path):
        yaml_path = os.path.join(os.path.dirname(__file__), relative_path)
        with open(yaml_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)

    def get_response(self, category, action=None):
        if action and action in self.responses['actions']:
            return self.responses['actions'][action]
        if category in self.responses:
            return random.choice(self.responses[category])
        return self.responses['default_response'][0]

    def normalize_text(self, text):
        return text.lower().replace("colaboradores", "colaborador").replace("clientes", "cliente").replace("promoções", "promoção")

    def handle_greeting(self, audio):
        try:
            self.voice_vector = self.register_employee_instance.voice_recognition.generate_embedding(audio.get_wav_data())
            response = self.get_response('greetings')
            logging.info(f"Aurora: {response}")
        except ValueError as e:
            logging.error(f"Erro ao gerar o vetor de voz: {e}")
            logging.error("Aurora: Houve um erro ao processar o vetor de voz.")

    def execute_command(self, recognized_text, audio=None):
        normalized_text = self.normalize_text(recognized_text)
        logging.debug(f"Texto reconhecido e normalizado: {normalized_text}")

        for action, details in self.intent_actions['actions'].items():
            phrases = details['triggers']['phrases']
            logging.debug(f"Verificando ação: {action} com frases {phrases}")
            
            for phrase in phrases:
                similarity = fuzz.ratio(normalized_text, self.normalize_text(phrase))
                if similarity > 80:
                    function_name = details['function']
                    command_function = getattr(self.register_employee_instance, function_name, None) or getattr(self, function_name, None)
                    
                    if callable(command_function):
                        logging.info(f"Executando a função '{function_name}' para a ação '{action}'")
                        command_function()
                        return
                    else:
                        logging.warning(f"Função '{function_name}' não encontrada ou não é executável.")
        
        logging.warning(f"Aurora: {self.get_response('default_response')}")

    def recognize_speech(self):
        while True:
            logging.info("Aurora: Aguardando saudação 'Oi Aurora' para iniciar...")
            try:
                recognized_text, audio = listen_and_save(self.recognizer, prompt="Você: ", timeout=10)
                if recognized_text:
                    if "oi aurora" in recognized_text:
                        self.handle_greeting(audio)  # Salva o vetor de voz
                        self.interaction_loop()
                    elif "aurora desligar" in recognized_text:
                        logging.info(self.get_response('farewells'))
                        break
            except srcd.WaitTimeoutError:
                logging.info("Aurora: Continuo aguardando a saudação 'Oi Aurora'...")
            except Exception as e:
                logging.error(f"Aurora: Houve um erro inesperado: {e}")

    def interaction_loop(self):
        self.inactivity_counter = 0
        while True:
            try:
                recognized_text, audio = listen_and_save(self.recognizer, prompt="Você: ", timeout=5)
                if recognized_text:
                    self.inactivity_counter = 0

                    if "aurora, por do sol" in recognized_text:
                        logging.info(self.get_response('farewells'))
                        self.handle_session_end()
                        break

                    self.execute_command(recognized_text, audio)
                else:
                    self.inactivity_counter += 1

                    if self.inactivity_counter == 2:
                        prompt = self.get_response('inactive_prompt')
                        logging.info(f"Aurora: {prompt}")

                    elif self.inactivity_counter >= 4:
                        logging.info("Aurora: Sessão encerrada por inatividade.")
                        self.handle_session_end()
                        break

            except srcd.WaitTimeoutError:
                self.inactivity_counter += 1
                if self.inactivity_counter == 2:
                    prompt = self.get_response('inactive_prompt')
                    logging.info(f"Aurora: {prompt}")
                elif self.inactivity_counter >= 4:
                    logging.info("Aurora: Sessão encerrada por inatividade.")
                    self.handle_session_end()
                    break
            except Exception as e:
                logging.error(f"Aurora: Houve um erro inesperado: {e}")

    def handle_session_end(self):
        logging.info("Aurora: Encerrando e salvando a sessão atual...")

if __name__ == "__main__":
    aurora = AuroraAI()
    aurora.recognize_speech()