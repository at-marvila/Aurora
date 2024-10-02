# integrations/firestore_operations.py

from datetime import datetime
import logging

class FirestoreOperations:
    def __init__(self, firebase_conn):
        self.db = firebase_conn.get_firestore_client()

    def upsert_employee(self, employee_data):
        """Adicionar ou atualizar um colaborador"""
        try:
            doc_ref = self.db.collection('employees').document(employee_data['document'])
            doc_ref.set(employee_data)
            logging.info(f"Documento adicionado/atualizado com sucesso: {employee_data['name']}")
        except Exception as e:
            logging.error(f"Erro ao adicionar/atualizar o colaborador: {e}")

    def get_employee(self, document_id):
        """Obter informações de um colaborador pelo documento"""
        try:
            doc_ref = self.db.collection('employees').document(document_id)
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
            else:
                logging.warning(f"Documento {document_id} não encontrado.")
                return None
        except Exception as e:
            logging.error(f"Erro ao obter colaborador: {e}")
            return None

    def update_employee_field(self, document_id, field, value):
        """Atualizar campos específicos de um colaborador"""
        try:
            doc_ref = self.db.collection('employees').document(document_id)
            doc_ref.update({field: value})
            logging.info(f"Campo {field} atualizado com sucesso para {value}")
        except Exception as e:
            logging.error(f"Erro ao atualizar campo {field} para colaborador {document_id}: {e}")

    def delete_employee(self, document_id):
        """Deletar um colaborador pelo documento"""
        try:
            doc_ref = self.db.collection('employees').document(document_id)
            doc_ref.delete()
            logging.info(f"Documento {document_id} deletado com sucesso.")
        except Exception as e:
            logging.error(f"Erro ao deletar colaborador {document_id}: {e}")
