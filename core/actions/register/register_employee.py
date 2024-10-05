# core/actions/register/register_employee.py

from integrations.firebase.firestore_operations import FirestoreOperations
from datetime import datetime
import json
import tempfile

class RegisterEmployee:
    def __init__(self, aurora_instance, firebase_conn):
        self.aurora = aurora_instance
        self.firestore_ops = FirestoreOperations(firebase_conn)

    def load_employee_template(self):
        with open('templates/employees.json', 'r') as file:
            return json.load(file)

    def register_employee(self):
        folder_path = tempfile.gettempdir()
        employee_template = self.load_employee_template()
        combined_audio_data = []

        employee_data = {
            "modification_date": datetime.now().isoformat(),
            "register_date": datetime.now().isoformat()
        }

        order_of_questions = employee_template['collaborator_registration']['fields']
        document_number = None

        for field, attributes in order_of_questions.items():
            self.aurora.logger.info(f"Aurora: Por favor, informe {attributes['label']}.")
            response, audio = self.aurora.listen_and_save()

            if response:
                if attributes['type'] == 'timestamp':
                    employee_data[field] = datetime.now().isoformat()
                elif attributes['type'] == 'boolean':
                    employee_data[field] = response.lower() in ['sim', 'yes', 'true']
                else:
                    employee_data[field] = response
                combined_audio_data.append(audio.get_wav_data())

                if field == "document":
                    document_number = response
            else:
                self.aurora.logger.warning(f"Aurora: Campo {attributes['label']} não foi preenchido corretamente.")
                return

        if document_number:
            final_audio_path = os.path.join(folder_path, f"{document_number}.wav")
            self.aurora.save_audio(b''.join(combined_audio_data), final_audio_path)
            self.aurora.upload_audio(final_audio_path, f"Bistek/Employees/{document_number}.wav")

            employee_data['document'] = document_number
            self.firestore_ops.upsert_employee(employee_data)
            self.aurora.logger.info(f"Aurora: Cadastro concluído e enviado ao Firestore. Áudio salvo como {document_number}.wav")
        else:
            self.aurora.logger.error("Aurora: Não foi possível registrar o colaborador, número de documento não fornecido.")