import os
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

from datetime import datetime
import logging

class FirestoreOperations:
    def __init__(self, firebase_conn):
        self.db = firebase_conn.get_firestore_client()

    def upsert_employee(self, employee_data, collection_path=None, document_id=None):
        """
        Adicionar ou atualizar um colaborador.
        Se 'document_id' for fornecido, o documento será salvo com esse ID.
        Caso contrário, ele usará o campo 'document' como ID.
        """
        try:
            # Definir o caminho da coleção customizado, se fornecido
            if collection_path:
                collection_ref = self.db.collection(collection_path)
            else:
                collection_ref = self.db.collection('employees')

            # Definir o ID do documento
            doc_id = document_id if document_id else employee_data['document']
            doc_ref = collection_ref.document(doc_id)

            doc_ref.set(employee_data)
            logging.info(f"Documento adicionado/atualizado com sucesso: {employee_data['name']}")
        except Exception as e:
            logging.error(f"Erro ao adicionar/atualizar o colaborador: {e}")