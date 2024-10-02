import firebase_admin
from firebase_admin import credentials, storage

# Caminho para o arquivo JSON da conta de serviço
cred = credentials.Certificate(r"C:\Users\salut\OneDrive\Documentos\Sevent\Connecion firebase\firebase-connection.json")

# Inicialize o Firebase
firebase_admin.initialize_app(cred, {
    'storageBucket': 'sevent-7197f.appspot.com'
})

# Função para fazer o upload de um arquivo de forma dinâmica
def upload_file_to_bucket(local_file_path, bucket_folder, file_name):
    try:
        # Obtenha uma referência ao bucket de armazenamento
        bucket = storage.bucket()

        # Crie o caminho completo no bucket (pasta/bucket + nome do arquivo)
        blob = bucket.blob(f'{bucket_folder}/{file_name}')

        # Faça o upload do arquivo
        blob.upload_from_filename(local_file_path)

        print(f'Upload do arquivo {file_name} concluído com sucesso no bucket {bucket_folder}.')

    except Exception as e:
        print(f'Ocorreu um erro durante o upload: {str(e)}')

# Exemplo de uso
local_file = r'C:\caminho\para\arquivo.txt'  # Caminho para o arquivo local
bucket_folder = 'pasta_no_bucket'            # Pasta no bucket onde o arquivo será enviado
file_name = 'arquivo.txt'                    # Nome do arquivo

# Chamada da função para upload
upload_file_to_bucket(local_file, bucket_folder, file_name)