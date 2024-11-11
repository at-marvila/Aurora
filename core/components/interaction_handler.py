# core/components/interaction_handler.py

import logging
import speech_recognition as sr
from utils.audio.audio_utils import listen_and_save

class InteractionHandler:
    def __init__(self, config_manager, command_executor):
        self.config = config_manager
        self.command_executor = command_executor
        self.recognizer = sr.Recognizer()

    def recognize_speech(self):
        """Loop de reconhecimento de voz para capturar e processar comandos do usuário."""
        while True:
            try:
                # Chamamos `listen_and_save`, que já faz log de "Você: [texto]"
                recognized_text, audio = listen_and_save(self.recognizer, prompt="Você: ")

                if recognized_text:
                    # Evite log adicional aqui para não duplicar a mensagem "Você: [texto]"
                    self.command_executor.execute_command(recognized_text)
                else:
                    logging.warning("Aurora: Não consegui entender o que você disse.")
                    continue

            except sr.WaitTimeoutError:
                logging.info("Continuo aguardando uma entrada de voz...")
                continue

            except Exception as e:
                logging.error(f"Erro de reconhecimento de voz: {e}")