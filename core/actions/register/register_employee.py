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

        for field, attributes in self.parameters['collaborator_registration']['fields'].items():
            if field in ["id", "register_date", "modification_date", "active", "notification", "supermarket_id", "created_by", "updated_by", "voice_vector", "recognition_method", "recognition_score"]:
                continue

            if field == "shift":
                # Coleta os dados do turno de trabalho
                shift_data = self._collect_shift_data(attributes)
                if shift_data:
                    employee_data["shift"] = shift_data
                continue

            self.logger.info(self.responses.get(f"ask_{field}", f"Please provide {attributes['label']}."))
            response, audio = self._ask_and_repeat(field, attributes)

            if response:
                self.logger.info(f"You: {response}")
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
                continue

        employee_data.update(Validator.validate_data(employee_data))
        self._generate_voice_embedding(employee_data, combined_audio_data)

        supermarket_name = self.supermarket_config.get("name", "supermarket").replace(" ", "_").lower()
        service_company = employee_data.get("service_company", "unknown").replace(" ", "_").lower()

        firestore_path = (
            f"regions/{self.supermarket_config['region']}/"
            f"states/{self.supermarket_config['state']}/"
            f"cities/{self.supermarket_config['city'].replace(' ', '_').lower()}/"
            f"supermarkets/{supermarket_name}/{self.supermarket_id}/employees/{service_company}"
        )

        # Definir o document_id como o número do documento
        if document_number:
            document_id = document_number
            full_firestore_path = f"{firestore_path}/{document_id}"
            self.logger.debug(f"Firestore Path (final): {full_firestore_path}")
            self.firestore_ops.upsert_employee(employee_data, document_id=document_id, firestore_path=firestore_path)
        else:
            self.logger.error("Documento não fornecido, não é possível registrar o colaborador.")


    def _collect_shift_data(self, attributes):
        """Coleta e processa os dados de turno (shift) do colaborador."""
        shift_data = {}

        # Pergunta o horário de entrada
        self.logger.info(self.responses.get("ask_shift_start", "Por favor, informe o horário de entrada."))
        start_response, _ = self._ask_and_repeat("shift_start", attributes["fields"]["start"])
        shift_data["start"] = start_response if start_response else attributes["fields"]["start"]["default"]

        # Pergunta o horário de saída
        self.logger.info(self.responses.get("ask_shift_end", "Por favor, informe o horário de saída."))
        end_response, _ = self._ask_and_repeat("shift_end", attributes["fields"]["end"])
        shift_data["end"] = end_response if end_response else attributes["fields"]["end"]["default"]

        # Pergunta sobre finais de semana
        self.logger.info(self.responses.get("ask_weekend", "Você trabalha nos finais de semana? (sim/não)"))
        weekend_response, _ = self._ask_and_repeat("weekend", attributes["fields"]["weekend"])
        shift_data["weekend"] = weekend_response.lower() in ["sim", "yes", "true"] if weekend_response else False

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