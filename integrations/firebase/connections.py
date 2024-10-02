import firebase_admin
from firebase_admin import credentials, firestore, storage

# Inicialize o Firebase apenas uma vez
class FirebaseConnection:
    def __init__(self, credentials_path, storage_bucket):
        # Inicialize apenas se ainda não foi inicializado
        if not firebase_admin._apps:
            cred = credentials.Certificate(credentials_path)
            firebase_admin.initialize_app(cred, {
                'storageBucket': storage_bucket
            })

    def get_firestore_client(self):
        return firestore.client()

    def get_storage_bucket(self):
        return storage.bucket()

# Exemplo de inicialização:
# firebase_conn = FirebaseConnection('/path/to/credentials.json', 'sevent-7197f.appspot.com')