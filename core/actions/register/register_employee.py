import os
import logging
import yaml
import json
from integrations.firebase.firestore_operations import FirestoreOperations
from utils.helpers.general_helpers import generate_supermarket_id, get_default_employee_data
from utils.audio.voice_recognition import VoiceRecognition
from utils.audio.audio_utils import listen_and_save
from validators.validators import Validator
from utils.session.session_logger import SessionLogger
from typing import Optional
import time
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
RESPONSES_DIR = os.path.join(BASE_DIR, "data", "employees", "responses")
PARAMETERS_DIR = os.path.join(BASE_DIR, "data", "employees", "parameters")


def load_yaml(file_path):
    """Carrega um arquivo YAML."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Arquivo '{file_path}' não encontrado.")
    with open(file_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def load_json(file_path):
    """Carrega um arquivo JSON."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Arquivo '{file_path}' não encontrado.")
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


class RegisterEmployee:
    def __init__(self, aurora_instance, firebase_conn, supermarket_config):
        self.logger = logging.getLogger(__name__)
        self.aurora = aurora_instance
        self.firestore_ops = FirestoreOperations(firebase_conn)
        self.supermarket_config = supermarket_config["supermarket"]
        self.supermarket_id = generate_supermarket_id(self.supermarket_config)

        # Carrega respostas e parâmetros
        self.responses = load_yaml(os.path.join(RESPONSES_DIR, "registration_responses.yaml"))["responses"]
        self.parameters = load_json(os.path.join(PARAMETERS_DIR, "employees.json"))

        # Inicializa o reconhecimento de voz
        if not hasattr(self.aurora, "voice_recognition"):
            self.aurora.voice_recognition = VoiceRecognition()

        self.user_name = None  # Para armazenar o nome do usuário ao longo da interação
        self.session_logger = SessionLogger(
            supermarket_config=self.supermarket_config,
            action_name="register_employee",
        )

    def register_employee(self) -> None:
        """Inicia o processo de registro de colaborador."""
        self.session_logger.start_session()
        self.session_logger.log_event("=== Iniciando Registro de Colaborador ===")
        employee_data = get_default_employee_data(self.supermarket_id)
        combined_audio_data = []

        document_number = None

        for field, attributes in self.parameters["collaborator_registration"]["fields"].items():
            if field in [
                "id", "register_date", "modification_date", "active", "notification",
                "supermarket_id", "created_by", "updated_by", "voice_vector",
                "recognition_method", "recognition_score",
            ]:
                continue

            value, audio = self._process_field(field, attributes)
            if value:
                employee_data[field] = value
                if field == "name":
                    self.user_name = value.split()[0]  # Usa apenas o primeiro nome
                if field == "document":
                    try:
                        document_number = self._validate_field(field, value)
                    except ValueError:
                        self.session_logger.log_error(field, self.responses["fields"]["invalid_cpf"].format(input=value))
                        continue
                if audio:
                    combined_audio_data.append(audio.get_wav_data())
            else:
                self.session_logger.log_event(self.responses["general"]["field_not_filled"].format(field=attributes["label"]))

        self._finalize_interaction(employee_data)

    def _process_field(self, field, attributes):
        """Captura e valida um campo específico."""
        max_attempts = 3
        attempt = 0

        while attempt < max_attempts:
            attempt += 1
            prompt = self.responses["fields"].get(f"ask_{field}", f"Por favor, forneça {attributes['label']}.")
            if self.user_name:
                prompt = f"{self.user_name}, {prompt}"
            self.session_logger.log_event(prompt)

            response, audio = listen_and_save(self.aurora.voice_recognition.recognizer)

            if response:  # Validação
                try:
                    validated_value = self._validate_field(field, response)
                    self.session_logger.log_event(
                        self.responses["success"]["field_captured"].format(field=attributes["label"])
                    )
                    return validated_value, audio
                except ValueError as e:
                    self.logger.error(f"Erro ao validar o campo {field}: {e}")
                    self.session_logger.log_error(field, f"A informação fornecida ({response}) está incorreta.")
            else:  # Falha na interpretação
                self.session_logger.log_event(self.responses["general"]["not_understood"])

            time.sleep(3)
            self.session_logger.log_event(
                self.responses["general"]["retry_in_progress"].format(attempt=attempt, max_attempts=max_attempts)
            )

        # Exibe mensagem final após falha
        self._finalize_with_error(field)

    def _validate_field(self, field, response):
        """Valida campos com validadores específicos."""
        validators = {
            "email": Validator.validate_and_correct_email,
            "dob": Validator.validate_date,
            "contact_number": Validator.validate_and_correct_phone,
            "document": Validator.validate_document,
        }
        if field in validators:
            return validators[field](response)
        return response

    def _finalize_with_error(self, field):
        """Finaliza a interação após falhas."""
        final_message = self.responses["general"]["final_message"].format(name=self.user_name or "usuário")
        self.session_logger.end_session(
            status="Erro",
            error_details=f"Erro no campo: {field}. Máximo de tentativas excedido.",
        )
        raise ValueError(f"Máximo de tentativas para o campo {field} excedido.")

    def _finalize_interaction(self, employee_data):
        """Finaliza a interação."""
        self.session_logger.end_session(status="Sucesso")
        self.session_logger.log_event(self.responses["success"]["registration_complete"])
