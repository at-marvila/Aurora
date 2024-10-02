# core/utils/firebase_utils.py

from firebase_admin import storage
import logging

def upload_to_firebase(local_file, bucket_path):
    """Faz upload de um arquivo local para o Firebase Storage"""
    bucket = storage.bucket()
    blob = bucket.blob(bucket_path)
    try:
        blob.upload_from_filename(local_file)
        logging.info(f"Upload do arquivo {local_file} para {bucket_path} concluído com sucesso.")
    except Exception as e:
        logging.error(f"Erro ao fazer upload para o Firebase: {e}")