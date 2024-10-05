import os
import yaml
import logging
import speech_recognition as srcd
from fuzzywuzzy import fuzz
from integrations.firebase.connections import FirebaseConnection
from utils.firebase_utils import upload_to_firebase
from utils.audio_utils import save_audio_wav
from utils.logging_config import setup_logging
from actions.register.register_employee import RegisterEmployee
import random
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
        self.supermarket_config = self.load_yaml_file('../data/configs/supermarket_config.yaml')  # Carregando a config do supermercado
        self.register_employee_instance = RegisterEmployee(self, firebase_conn, self.supermarket_config)
        self.inactivity_counter = 0

    def load_yaml_file(self, relative_path):
        """Carrega um arquivo YAML e retorna os dados"""
        yaml_path = os.path.join(os.path.dirname(__file__), relative_path)
        with open(yaml_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)

    def get_response(self, category, action=None):
        """Obtém uma resposta da categoria especificada"""
        if action and action in self.responses['actions']:
            return self.responses['actions'][action]
        if category in self.responses:
            return random.choice(self.responses[category])
        return self.responses['default_response'][0]

    def normalize_text(self, text):
        """Normaliza o texto reconhecido"""
        return text.lower().replace("colaboradores", "colaborador").replace("clientes", "cliente").replace("promoções", "promoção")

    def handle_greeting(self):
        """Trata a saudação inicial"""
        response = self.get_response('greetings')
        logging.info(f"Aurora: {response}")
        print(f"Aurora: {response}")

    def execute_command(self, recognized_text, audio=None):
        """Executa o comando correspondente ao texto reconhecido"""
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
        """Reconhece a fala e inicia a interação"""
        while True:
            print("Aurora: Aguardando saudação 'Oi Aurora' para iniciar...")
            try:
                recognized_text, audio = self.listen_and_save(prompt="Você: ", timeout=10)  # Escuta por 10 segundos para "Oi Aurora"
                if recognized_text:
                    if "oi aurora" in recognized_text:
                        self.handle_greeting()
                        self.interaction_loop()  # Entra no loop de interação
                    elif "aurora, por do sol" in recognized_text:
                        print(self.get_response('farewells'))
                        break  # Sai da aplicação se o comando de encerramento for dado
            except srcd.WaitTimeoutError:
                print("Aurora: Continuo aguardando a saudação 'Oi Aurora'...")
                continue  # Continua aguardando por uma saudação "Oi Aurora"
            except Exception as e:
                print(f"Aurora: Houve um erro inesperado: {e}")
                continue

    def interaction_loop(self):
        """Loop para interação após o 'Oi Aurora' inicial"""
        self.inactivity_counter = 0  # Reseta o contador de inatividade
        while True:
            try:
                recognized_text, audio = self.listen_and_save(prompt="Você: ", timeout=5)  # Continua ouvindo durante a interação
                if recognized_text:
                    self.inactivity_counter = 0

                    if "aurora, por do sol" in recognized_text:
                        print(self.get_response('farewells'))
                        self.handle_session_end()
                        break

                    self.execute_command(recognized_text, audio)
                else:
                    self.inactivity_counter += 1

                    if self.inactivity_counter == 2:
                        prompt = self.get_response('inactive_prompt')
                        print(f"Aurora: {prompt}")

                    elif self.inactivity_counter >= 4:  # Tentativa de interação após 4 ciclos
                        print("Aurora: Sessão encerrada por inatividade.")
                        self.handle_session_end()
                        break

            except srcd.WaitTimeoutError:
                self.inactivity_counter += 1

                if self.inactivity_counter == 2:
                    prompt = self.get_response('inactive_prompt')
                    print(f"Aurora: {prompt}")

                elif self.inactivity_counter >= 4:
                    print("Aurora: Sessão encerrada por inatividade.")
                    self.handle_session_end()
                    break

            except Exception as e:
                logging.error(f"Aurora: Houve um erro inesperado: {e}")
                continue

    def listen_and_save(self, prompt="Diga algo:", lang="pt-BR", timeout=5):
        """Escuta e salva o áudio"""
        with srcd.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            print(prompt)
            try:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
                recognized_text = self.recognizer.recognize_google(audio, language=lang).lower()
                logging.info(f"Texto reconhecido: {recognized_text}")
                return recognized_text, audio
            except srcd.UnknownValueError:
                logging.warning("Aurora: Não consegui entender o que você disse.")
                return None, None
            except srcd.RequestError as e:
                logging.error(f"Aurora: Erro no serviço de reconhecimento de voz: {e}")
                return None, None

    def upload_audio(self, local_file, bucket_path):
        """Faz upload de um arquivo de áudio para o Firebase"""
        upload_to_firebase(local_file, bucket_path)

    def save_audio(self, audio_data, file_path):
        """Salva um arquivo de áudio em formato WAV"""
        save_audio_wav(audio_data, file_path)

    def handle_session_end(self):
        """Método para manipular o encerramento de uma sessão"""
        logging.info("Aurora: Encerrando e salvando a sessão atual...")
        print("Aurora: Encerrando e salvando a sessão atual...")

if __name__ == "__main__":
    aurora = AuroraAI()
    aurora.recognize_speech()