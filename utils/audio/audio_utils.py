# core/utils/audio_utils.py
import speech_recognition as srcd
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

import logging
import speech_recognition as sr

def listen_and_save(recognizer, prompt="Você: ", timeout=10):
    with sr.Microphone() as source:
        print(prompt)
        try:
            # Tenta ouvir o áudio com o timeout especificado
            audio = recognizer.listen(source, timeout=timeout)
            if audio is None:
                logging.error("Erro de áudio: Nenhum áudio foi capturado.")
                return None, None
            
            # Reconhece o áudio com o idioma definido como português
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