import os
import logging
import yaml
import json
from integrations.firebase.firestore_operations import FirestoreOperations
from utils.helpers.general_helpers import generate_supermarket_id, get_default_employee_data
from utils.audio.voice_recognition import VoiceRecognition
from utils.audio.audio_utils import listen_and_save
from validators.validators import Validator
from typing import Optional
import tempfile

# Define o caminho base da aplicação como o diretório onde o arquivo principal do projeto está
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
RESPONSES_DIR = os.path.join(BASE_DIR, "data", "employees", "responses")
PARAMETERS_DIR = os.path.join(BASE_DIR, "data", "employees", "parameters")

def load_responses(file_name):
    file_path = os.path.join(RESPONSES_DIR, file_name)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"O arquivo de respostas '{file_path}' não foi encontrado.")
    with open(file_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)["responses"]

def load_parameters(file_name):
    file_path = os.path.join(PARAMETERS_DIR, file_name)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"O arquivo de parâmetros '{file_path}' não foi encontrado.")
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

class RegisterEmployee:
    def __init__(self, aurora_instance, firebase_conn, supermarket_config):
        self.logger = logging.getLogger(__name__)
        self.aurora = aurora_instance

        # Instancia VoiceRecognition para capturar e processar áudio
        if not hasattr(self.aurora, 'voice_recognition'):
            self.aurora.voice_recognition = VoiceRecognition()

        # Carrega respostas e parâmetros
        self.responses = load_responses("registration_responses.yaml")
        self.parameters = load_parameters("employees.json")

        self.firestore_ops = FirestoreOperations(firebase_conn)
        self.supermarket_config = supermarket_config['supermarket']
        self.supermarket_id = generate_supermarket_id(self.supermarket_config)

    def register_employee(self) -> None:
        combined_audio_data = []
        employee_data = get_default_employee_data(self.supermarket_id)
        document_number: Optional[str] = None

        # Itera sobre cada campo requerido no cadastro
        for field, attributes in self.parameters['collaborator_registration']['fields'].items():
            # Ignora campos que são preenchidos automaticamente
            if field in ["id", "register_date", "modification_date", "active", "notification", "supermarket_id", "created_by", "updated_by", "voice_vector", "recognition_method", "recognition_score"]:
                continue

            # Tratamento especial para o campo "shift"
            if field == "shift":
                shift_data = self._collect_shift_data(attributes)
                if shift_data:
                    employee_data['shift'] = shift_data
                continue

            # Pergunta e coleta a resposta usando mensagens do YAML
            self.logger.info(self.responses.get(f"ask_{field}", f"Por favor, informe {attributes['label']}."))
            response, audio = self._ask_and_repeat(field, attributes)

            if response:
                self.logger.info(f"Você: {response}")
                
                # Aplica validações específicas para cada campo
                if field == "email":
                    employee_data[field] = Validator.validate_and_correct_email(response)
                elif field == "dob":
                    employee_data[field] = Validator.validate_date(response)
                elif field == "contact_number":
                    employee_data[field] = Validator.validate_and_correct_phone(response)
                else:
                    employee_data[field] = response
                
                if field == "document":
                    document_number = Validator.validate_document(response)

                if audio:
                    combined_audio_data.append(audio.get_wav_data())
            else:
                self.logger.warning(self.responses["field_not_filled"].format(field=attributes['label']))
                continue  # Repassa ao próximo campo caso o campo não seja preenchido

        # Valida e limpa os dados coletados
        employee_data.update(Validator.validate_data(employee_data))

        # Gera o embedding de voz
        self._generate_voice_embedding(employee_data, combined_audio_data)

        # Define o caminho do Firestore e salva os dados do colaborador
        firestore_path = f"regions/{self.supermarket_config['region']}/states/{self.supermarket_config['state']}/cities/{self.supermarket_config['city'].replace(' ', '_').lower()}/supermarkets/{self.supermarket_id}/employees"

        if document_number:
            self.firestore_ops.upsert_employee(employee_data, document_id=document_number, firestore_path=firestore_path)
            self.logger.info(f"Aurora: Cadastro concluído e enviado ao Firestore no caminho {firestore_path}/{document_number}")
        else:
            self.logger.error("Aurora: Não foi possível registrar o colaborador, número de documento não fornecido.")

    def _collect_shift_data(self, attributes):
        """Coleta e processa os dados de turno (shift) do colaborador."""
        shift_data = {"week": "5"}
        self.logger.info(self.responses["ask_shift_start"])
        start_response, _ = self._ask_and_repeat("shift_start", attributes['fields']['start'])

        if start_response and start_response.isdigit():
            shift_data['start'] = start_response
        else:
            shift_data['start'] = attributes['fields']['start']['default']

        self.logger.info(self.responses["ask_shift_end"])
        end_response, _ = self._ask_and_repeat("shift_end", attributes['fields']['end'])

        if end_response and end_response.isdigit():
            shift_data['end'] = end_response
        else:
            shift_data['end'] = attributes['fields']['end']['default']

        self.logger.info(self.responses["ask_weekend"])
        weekend_response, _ = self._ask_and_repeat("weekend", attributes)

        if weekend_response:
            shift_data['weekend'] = weekend_response.lower() in ["sim", "yes", "true"]
        else:
            self.logger.warning("Não foi possível registrar resposta sobre finais de semana.")

        return shift_data

    def _ask_and_repeat(self, field, attributes, max_attempts=3):
        """Pergunta e, em caso de erro, repete a pergunta até `max_attempts` vezes."""
        attempts = 0
        while attempts < max_attempts:
            response, audio = listen_and_save(self.aurora.voice_recognition.recognizer)
            if response:
                return response, audio
            else:
                self.logger.warning(self.responses["not_understood"])
                attempts += 1
        self.logger.warning(self.responses["field_not_filled"].format(field=attributes['label']))
        return None, None

    def _generate_voice_embedding(self, employee_data, combined_audio_data):
        """Gera o vetor de voz a partir dos dados de áudio combinados e os adiciona aos dados do colaborador."""
        try:
            if combined_audio_data:
                audio_data = b''.join(combined_audio_data)
                voice_embedding = self.aurora.voice_recognition.generate_embedding(audio_data)
                employee_data["voice_vector"] = list(map(float, voice_embedding.tolist()))
                employee_data["recognition_method"] = "speechbrain_xvector_voxceleb"
            else:
                self.logger.warning("Nenhum dado de áudio foi capturado para o vetor de voz.")
        except Exception as e:
            self.logger.error(f"Aurora: Erro ao gerar o vetor de voz: {e}")