import logging
from integrations.firebase.firestore_operations import FirestoreOperations
from utils.helpers.general_helpers import load_employee_template, generate_supermarket_id, get_default_employee_data
from utils.audio.voice_recognition import VoiceRecognition
from utils.audio.audio_utils import listen_and_save
from validators.document_validator import validate_document
from validators.data_cleaner import validate_data
from typing import Optional
import tempfile

class RegisterEmployee:
    def __init__(self, aurora_instance, firebase_conn, supermarket_config):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.aurora = aurora_instance
        self.firestore_ops = FirestoreOperations(firebase_conn)
        self.voice_recognition = VoiceRecognition()
        self.supermarket_config = supermarket_config['supermarket']
        self.supermarket_id = generate_supermarket_id(self.supermarket_config)

    def register_employee(self) -> None:
        folder_path = tempfile.gettempdir()
        employee_template = load_employee_template()
        combined_audio_data = []
        
        # Dados automáticos e valores padrão
        employee_data = get_default_employee_data(self.supermarket_id)
        order_of_questions = employee_template['collaborator_registration']['fields']
        document_number: Optional[str] = None

        for field, attributes in order_of_questions.items():
            if field in ["id", "register_date", "modification_date", "active", "notification", "supermarket_id", "created_by", "updated_by", "voice_vector", "recognition_method", "recognition_score"]:
                continue

            if field == "shift":
                shift_data = {"week": "5"}
                self.logger.info("Aurora: Por favor, informe o Horário de Entrada.")
                start_response, _ = listen_and_save(self.aurora.recognizer, prompt="Você: ")
                shift_data['start'] = start_response if start_response and start_response.isdigit() else attributes['fields']['start']['default']

                self.logger.info("Aurora: Por favor, informe o Horário de Saída.")
                end_response, _ = listen_and_save(self.aurora.recognizer, prompt="Você: ")
                shift_data['end'] = end_response if end_response and end_response.isdigit() else attributes['fields']['end']['default']

                self.logger.info("Aurora: Trabalha nos finais de semana? (sim/não)")
                weekend_response, _ = listen_and_save(self.aurora.recognizer, prompt="Você: ")
                shift_data['weekend'] = weekend_response.lower() in ["sim", "yes", "true"]

                employee_data['shift'] = shift_data
                continue

            self.logger.info(f"Aurora: Por favor, informe {attributes['label']}.")
            response, audio = listen_and_save(self.aurora.recognizer, prompt="Você: ")

            if response:
                self.logger.debug(f"Recebido dado para o campo {field}: {response}")
                employee_data[field] = response
                if field == "document":
                    document_number = validate_document(response)
                combined_audio_data.append(audio.get_wav_data() if audio else b'')
            else:
                self.logger.warning(f"Aurora: Campo {attributes['label']} não foi preenchido corretamente.")
                return

        employee_data.update(validate_data(employee_data))

        try:
            voice_embedding = self.voice_recognition.generate_embedding(b''.join(combined_audio_data))
            employee_data["voice_vector"] = list(map(float, voice_embedding.tolist()))
            employee_data["recognition_method"] = "speechbrain_xvector_voxceleb"
        except Exception as e:
            self.logger.error(f"Aurora: Erro ao gerar o vetor de voz: {e}")
            return

        firestore_path = f"regions/{self.supermarket_config['region']}/states/{self.supermarket_config['state']}/cities/{self.supermarket_config['city'].replace(' ', '_').lower()}/supermarkets/{self.supermarket_id}/employees"

        if document_number:
            self.firestore_ops.upsert_employee(employee_data, document_id=document_number, firestore_path=firestore_path)
            self.logger.info(f"Aurora: Cadastro concluído e enviado ao Firestore no caminho {firestore_path}/{document_number}")
        else:
            self.logger.error("Aurora: Não foi possível registrar o colaborador, número de documento não fornecido.")