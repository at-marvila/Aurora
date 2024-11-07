import speech_recognition as sr
import wave
import logging

def save_audio_wav(audio_data, file_path):
    """Salva o áudio combinado em formato WAV"""
    try:
        with wave.open(file_path, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(16000)
            wav_file.writeframes(audio_data)
        logging.info(f"Áudio salvo com sucesso em {file_path}")
    except Exception as e:
        logging.error(f"Erro ao salvar o áudio: {e}")

def listen_and_save(recognizer, prompt="Você: "):
    """Captura áudio e o reconhece usando o Google Speech Recognition sem argumentos adicionais."""
    with sr.Microphone() as source:
        print(prompt)
        try:
            recognizer.adjust_for_ambient_noise(source)  # Ajusta para ruído ambiente
            audio = recognizer.listen(source)
            if audio is None:
                logging.error("Erro de áudio: Nenhum áudio foi capturado.")
                return None, None
            
            recognized_text = recognizer.recognize_google(audio, language="pt-BR")
            return recognized_text, audio
        except sr.WaitTimeoutError:
            logging.error("Erro de timeout: Nenhum som detectado.")
            return None, None
        except sr.UnknownValueError:
            logging.error("Erro de reconhecimento: O áudio não pôde ser interpretado.")
            return None, None
        except Exception as e:
            logging.error(f"Erro inesperado de áudio: {e}")
            return None, None