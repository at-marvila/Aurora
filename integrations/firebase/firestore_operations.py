import os
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

from datetime import datetime
import logging

class FirestoreOperations:
    def __init__(self, firebase_conn):
        self.db = firebase_conn.get_firestore_client()

    def upsert_employee(self, employee_data, document_id=None, firestore_path=None):
        """
        Adicionar ou atualizar um colaborador.
        Se 'document_id' for fornecido e 'firestore_path', o documento será salvo com esse ID e caminho completo.
        """
        try:
            # Verifica se o firestore_path foi fornecido para construir o caminho completo
            if firestore_path and document_id:
                # Cria referência ao documento no caminho completo especificado
                doc_ref = self.db.document(f"{firestore_path}/{document_id}")
            else:
                # Fallback para o caminho padrão (não recomendado neste caso)
                doc_ref = self.db.collection('employees').document(document_id or employee_data['document'])

            doc_ref.set(employee_data)
            logging.info(f"Documento adicionado/atualizado com sucesso: {employee_data['name']}")
        except Exception as e:
            logging.error(f"Erro ao adicionar/atualizar o colaborador: {e}")