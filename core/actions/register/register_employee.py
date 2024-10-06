import logging
from integrations.firebase.firestore_operations import FirestoreOperations
from datetime import datetime
import json
import tempfile
import os
import uuid
from utils.supermarket.generate_supermarket_id import generate_supermarket_id
from validators.date_validator import format_date  # Corrigido para apontar para o local correto do format_date
from validators.data_utils import format_document  # Corrigido para apontar para o local correto do format_document
from utils.audio.audio_utils import save_audio_wav
from utils.firebase.firebase_utils import upload_to_firebase

class RegisterEmployee:
    def __init__(self, aurora_instance, firebase_conn, supermarket_config):
        # Configurando o logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Criar um handler para o console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # Definir aurora e firestore
        self.aurora = aurora_instance
        self.firestore_ops = FirestoreOperations(firebase_conn)

        # Usar a configuração do supermercado do arquivo YAML
        self.supermarket_chain_code = supermarket_config['supermarket_chain_code']
        self.city = supermarket_config['city']
        self.state = supermarket_config['state']
        self.store_number = supermarket_config['store_number']

    def load_employee_template(self):
        self.logger.debug("Carregando template de funcionário.")
        with open('data/employees.json', 'r') as file:
            return json.load(file)

    def register_employee(self):
        folder_path = tempfile.gettempdir()
        employee_template = self.load_employee_template()
        combined_audio_data = []

        # Gerar automaticamente os campos de data, status e ID
        employee_data = {
            "id": str(uuid.uuid4()),                          # ID gerado automaticamente
            "modification_date": datetime.now().isoformat(),  # Data de modificação gerada automaticamente
            "register_date": datetime.now().isoformat(),      # Data de registro gerada automaticamente
            "status": True,                                   # Status gerado automaticamente como ativo (True)
            "notification": True,                             # Notificação padrão como habilitada (True)
            "supermarket_id": generate_supermarket_id(self.supermarket_chain_code, self.city, None, self.store_number)  # Gerando o ID automaticamente
        }

        order_of_questions = employee_template['collaborator_registration']['fields']
        document_number = None

        self.logger.info("Iniciando registro do funcionário.")

        # Remover perguntas desnecessárias
        for field, attributes in order_of_questions.items():
            # Ignorar campos automáticos e os que já estão no arquivo de configuração
            if field in ["id", "register_date", "modification_date", "status", "notification", "supermarket_id", "supermarket_chain_code", "store_number", "city"]:
                continue

            self.logger.info(f"Aurora: Por favor, informe {attributes['label']}.")
            response, audio = self.aurora.listen_and_save()

            if response:
                self.logger.debug(f"Recebido dado para o campo {field}: {response}")
                
                # Tratamento para os campos de data e documento
                if field == "date_of_birth":
                    # Utiliza a função de limpeza de data
                    employee_data[field] = format_date(response)
                elif field == "document":
                    # Utiliza a função de limpeza de número de documento
                    document_number = format_document(response)
                    employee_data[field] = document_number
                elif attributes['type'] == 'timestamp':
                    employee_data[field] = datetime.now().isoformat()
                elif attributes['type'] == 'boolean':
                    employee_data[field] = response.lower() in ['sim', 'yes', 'true']
                else:
                    employee_data[field] = response
                
                combined_audio_data.append(audio.get_wav_data())
            else:
                self.logger.warning(f"Aurora: Campo {attributes['label']} não foi preenchido corretamente.")
                return

        if document_number:
            self.logger.info(f"Salvando o áudio para o documento {document_number}.")
            final_audio_path = os.path.join(folder_path, f"{document_number}.wav")
            save_audio_wav(b''.join(combined_audio_data), final_audio_path)
            upload_to_firebase(final_audio_path, f"Bistek/Employees/{document_number}.wav")

            self.firestore_ops.upsert_employee(employee_data)
            self.logger.info(f"Aurora: Cadastro concluído e enviado ao Firestore. Áudio salvo como {document_number}.wav")
        else:
            self.logger.error("Aurora: Não foi possível registrar o colaborador, número de documento não fornecido.")