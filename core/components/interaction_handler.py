# core/components/interaction_handler.py

import logging
from utils.audio.audio_utils import listen_and_save
import speech_recognition as srcd

class InteractionHandler:
    def __init__(self, config_manager, command_executor):
        self.config = config_manager
        self.command_executor = command_executor
        self.recognizer = srcd.Recognizer()

    def recognize_speech(self):
        """Loop de reconhecimento de voz para capturar e processar comandos do usuário."""
        while True:
            try:
                recognized_text, audio = listen_and_save(self.recognizer, prompt="Você: ", timeout=10)

                if recognized_text:
                    logging.info(f"Texto reconhecido: {recognized_text}")
                    self.command_executor.execute_command(recognized_text)
                else:
                    logging.warning("Aurora: Não consegui entender o que você disse.")
                    continue

            except srcd.WaitTimeoutError:
                logging.info("Continuo aguardando uma entrada de voz...")
                continue

            except Exception as e:
                logging.error(f"Erro de reconhecimento de voz: {e}")