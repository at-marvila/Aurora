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

def listen_and_save(recognizer, prompt="Diga algo:", lang="pt-BR", timeout=5):
    """Função que captura e processa o áudio do usuário, retornando o texto reconhecido e o áudio."""
    with srcd.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print(prompt)
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
            recognized_text = recognizer.recognize_google(audio, language=lang).lower()
            logging.info(f"Texto reconhecido: {recognized_text}")
            return recognized_text, audio
        except srcd.UnknownValueError:
            logging.warning("Aurora: Não consegui entender o que você disse.")
            return None, None
        except srcd.RequestError as e:
            logging.error(f"Aurora: Erro no serviço de reconhecimento de voz: {e}")
            return None, None