# core/utils/audio_utils.py

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