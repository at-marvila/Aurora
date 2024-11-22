# core/components/interaction_handler.py

import logging
import speech_recognition as sr
from utils.audio.audio_utils import listen_and_save
import time

class InteractionHandler:
    def __init__(self, config_manager, command_executor):
        self.config = config_manager
        self.command_executor = command_executor
        self.recognizer = sr.Recognizer()
        self.awaiting_interaction = True  # Controla o estado de espera por interação

    def recognize_speech(self):
        """Loop contínuo de reconhecimento de voz para capturar e processar comandos do usuário."""
        logging.info("Aurora está pronta para interações. Aguardando entrada de voz...")

        while True:
            try:
                if self.awaiting_interaction:
                    logging.warning("Aguardando interação do usuário.")
                    time.sleep(3)  # Intervalo antes de verificar novamente

                # Captura áudio do microfone e tenta reconhecer
                recognized_text, audio = listen_and_save(self.recognizer)

                if recognized_text:
                    # Apenas executa o comando sem duplicar o log
                    if "oi aurora" in recognized_text.lower():
                        self.awaiting_interaction = False
                        logging.info("Aurora: Olá! Como posso ajudar?")
                        print("Aurora: Olá! Como posso ajudar?")
                    elif not self.awaiting_interaction:
                        self.command_executor.execute_command(recognized_text)
                    else:
                        logging.warning("Aurora está aguardando 'Oi Aurora' para continuar.")
                else:
                    logging.warning("Aurora: Não consegui entender o que você disse.")

            except sr.WaitTimeoutError:
                logging.info("Aurora continua aguardando entrada de voz...")
                self.awaiting_interaction = True
                continue

            except Exception as e:
                logging.error(f"Erro de reconhecimento de voz: {e}")
                self.awaiting_interaction = True