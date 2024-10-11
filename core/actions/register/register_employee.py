import logging
from integrations.firebase.firestore_operations import FirestoreOperations
from datetime import datetime
import tempfile
import os
import uuid
from validators.date_validator import validate_date
from validators.document_validator import validate_document
from utils.audio.voice_recognition import VoiceRecognition
import json

class RegisterEmployee:
    def __init__(self, aurora_instance, firebase_conn, supermarket_config):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.aurora = aurora_instance
        self.firestore_ops = FirestoreOperations(firebase_conn)
        self.voice_recognition = VoiceRecognition()

        # Carregar as configurações do supermercado e definir acrônimos
        self.supermarket_config = supermarket_config['supermarket']
        self.supermarket_name = self.supermarket_config['name']
        self.region = self.supermarket_config['region']
        self.state = self.supermarket_config['state']
        self.city = self.supermarket_config['city']
        self.district = self.supermarket_config['district']
        self.store_number = self.supermarket_config['store_number']
        self.city_acronym = self.supermarket_config['acronyms']['city'].get(self.city, self.city)
        self.district_acronym = self.supermarket_config['acronyms']['district'].get(self.district, self.district)
        self.identifier_format = self.supermarket_config['identifier_format']

    def load_employee_template(self):
        """Carrega o template de colaborador a partir do arquivo employees.json"""
        self.logger.debug("Carregando template de funcionário.")
        with open('data/employees.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    
    def generate_supermarket_id(self):
        """Gera o identificador do supermercado usando o formato definido"""
        return self.identifier_format.format(
            name=self.supermarket_name,
            state=self.state,
            city_acronym=self.city_acronym,
            district_acronym=self.district_acronym,
            store_number=self.store_number
        )

    def register_employee(self):
        folder_path = tempfile.gettempdir()
        employee_template = self.load_employee_template()
        combined_audio_data = []

        # Dados automáticos e valores padrão
        employee_data = {
            "id": str(uuid.uuid4()),
            "modification_date": datetime.now().isoformat(),
            "register_date": datetime.now().isoformat(),
            "active": True,
            "notification": True,
            "created_by": "Sistema",
            "updated_by": "Sistema",
            "supermarket_id": self.generate_supermarket_id(),  # Usa o novo método para gerar o ID
            "recognition_score": 98  # Score hard-coded conforme solicitado
        }

        order_of_questions = employee_template['collaborator_registration']['fields']
        document_number = None

        for field, attributes in order_of_questions.items():
            # Ignora campos automáticos
            if field in ["id", "register_date", "modification_date", "active", "notification", "supermarket_id", "created_by", "updated_by", "voice_vector", "recognition_method", "recognition_score"]:
                continue

            if field == "shift":
                # Pergunta apenas horário de entrada, saída e se trabalha no fim de semana
                shift_data = {"week": "5"}

                # Pergunta horário de entrada
                self.logger.info("Aurora: Por favor, informe o Horário de Entrada.")
                start_response, _ = self.aurora.listen_and_save()
                if start_response and start_response.isdigit():
                    shift_data['start'] = int(start_response)
                else:
                    shift_data['start'] = attributes['fields']['start']['default']

                # Pergunta horário de saída
                self.logger.info("Aurora: Por favor, informe o Horário de Saída.")
                end_response, _ = self.aurora.listen_and_save()
                if end_response and end_response.isdigit():
                    shift_data['end'] = int(end_response)
                else:
                    shift_data['end'] = attributes['fields']['end']['default']

                # Pergunta sobre finais de semana
                self.logger.info("Aurora: Trabalha nos finais de semana? (sim/não)")
                weekend_response, _ = self.aurora.listen_and_save()
                shift_data['weekend'] = weekend_response and weekend_response.lower() in ["sim", "yes", "true"]

                employee_data['shift'] = shift_data
                continue  # Pula a pergunta padrão para 'shift'

            self.logger.info(f"Aurora: Por favor, informe {attributes['label']}.")
            response, audio = self.aurora.listen_and_save()

            if response:
                self.logger.debug(f"Recebido dado para o campo {field}: {response}")
                
                # Tratamento específico para campos com tipos e verificações
                if field == "dob":
                    employee_data[field] = validate_date(response)
                elif field == "document":
                    document_number = validate_document(response)
                    employee_data[field] = document_number
                else:
                    employee_data[field] = response

                combined_audio_data.append(audio.get_wav_data() if audio else b'')
            else:
                self.logger.warning(f"Aurora: Campo {attributes['label']} não foi preenchido corretamente.")
                return

        # Configurar o vetor de voz e o método de reconhecimento
        try:
            voice_embedding = self.voice_recognition.generate_embedding(b''.join(combined_audio_data))
            employee_data["voice_vector"] = list(map(float, voice_embedding.tolist()))  # Converte o array numpy para lista
            employee_data["recognition_method"] = "speechbrain_xvector_voxceleb"
        except Exception as e:
            self.logger.error(f"Aurora: Erro ao gerar o vetor de voz: {e}")
            return

        # Define o caminho detalhado para salvar no Firestore
        firestore_path = f"regions/{self.region}/states/{self.state}/cities/{self.city.replace(' ', '_').lower()}/supermarkets/{employee_data['supermarket_id']}/employees/{document_number}"

        # Tenta inserir os dados no Firestore
        if document_number:
            self.firestore_ops.upsert_employee(employee_data, document_id=document_number)
            self.logger.info(f"Aurora: Cadastro concluído e enviado ao Firestore no caminho {firestore_path}")
        else:
            self.logger.error("Aurora: Não foi possível registrar o colaborador, número de documento não fornecido.")