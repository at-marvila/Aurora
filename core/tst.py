# test_listen_and_save.py

import logging
from utils.audio.audio_utils import listen_and_save  # Certifique-se de que o caminho está correto
import speech_recognition as sr

# Configuração de logging
logging.basicConfig(level=logging.DEBUG)

def test_listen_and_save():
    recognizer = sr.Recognizer()
    print("Iniciando o teste do listen_and_save. Tente falar algo...")

    try:
        recognized_text, audio_data = listen_and_save(recognizer, prompt="Teste de captura: ", timeout=10)
        if recognized_text:
            print(f"Texto reconhecido: {recognized_text}")
            logging.info("Áudio capturado e reconhecido com sucesso.")
        else:
            print("Nenhum áudio foi reconhecido.")
            logging.warning("O áudio não foi reconhecido.")
    except Exception as e:
        logging.error(f"Erro no teste listen_and_save: {e}")

if __name__ == "__main__":
    test_listen_and_save()