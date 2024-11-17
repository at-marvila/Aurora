import os
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

import logging

class FirestoreOperations:
    def __init__(self, firebase_conn):
        self.db = firebase_conn.get_firestore_client()

    def upsert_employee(self, employee_data, document_id=None, firestore_path=None):
        try:
            if not firestore_path or not document_id:
                raise ValueError("Firestore path e document_id devem ser fornecidos.")

            # Remove barras finais, se existirem
            firestore_path = firestore_path.rstrip('/')

            # Cria o caminho final adicionando o document_id
            full_path = f"{firestore_path}/{document_id}"

            # Verifica se o caminho é válido
            if len(full_path.split('/')) % 2 != 0:
                raise ValueError(f"O caminho do Firestore deve conter um número par de elementos: {full_path}")

            # Cria o documento no Firestore
            doc_ref = self.db.document(full_path)
            doc_ref.set(employee_data)

            logging.info(f"Documento salvo com sucesso no caminho: {full_path}")
        except Exception as e:
            logging.error(f"Erro ao adicionar/atualizar o colaborador: {e}")
