import numpy as np
import torchaudio
import torch
from speechbrain.inference import EncoderClassifier
from pydub import AudioSegment
import noisereduce as nr
import io
import logging
import speech_recognition as sr

class VoiceRecognition:
    def __init__(self, sample_rate=44100):
        self.model = EncoderClassifier.from_hparams(source="speechbrain/spkrec-xvect-voxceleb")
        self.sample_rate = sample_rate
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.recognizer = sr.Recognizer()

    def listen(self):
        """Captura áudio em tempo real do microfone e retorna o áudio como bytes."""
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source)  # Ajusta para ruído ambiente
                self.logger.info("Aguardando som...")
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=10)
                audio_data = audio.get_wav_data()
                return audio_data
        except sr.WaitTimeoutError:
            self.logger.error("Tempo esgotado ao aguardar áudio.")
            raise ValueError("Tempo esgotado ao aguardar áudio.")
        except Exception as e:
            self.logger.error(f"Erro ao capturar o áudio: {e}")
            raise ValueError(f"Erro ao capturar o áudio: {e}")

    def preprocess_audio(self, audio_segment):
        """Preprocessa o áudio aplicando normalização e redução de ruído."""
        try:
            # Normaliza o áudio
            normalized_audio = audio_segment.apply_gain(-audio_segment.max_dBFS)
            audio_data = np.array(normalized_audio.get_array_of_samples())
            
            # Reduz o ruído no áudio
            reduced_noise_audio = nr.reduce_noise(y=audio_data, sr=normalized_audio.frame_rate)
            
            # Converte o áudio processado de volta para AudioSegment
            processed_audio = AudioSegment(
                reduced_noise_audio.astype(np.int16).tobytes(),
                frame_rate=normalized_audio.frame_rate,
                sample_width=normalized_audio.sample_width,
                channels=normalized_audio.channels
            )
            return processed_audio
        except Exception as e:
            self.logger.error(f"Erro ao preprocessar o áudio: {e}")
            raise ValueError(f"Erro ao preprocessar o áudio: {e}")

    def generate_embedding(self, audio_data):
        """Gera o embedding do áudio fornecido."""
        try:
            audio_segment = AudioSegment.from_file(io.BytesIO(audio_data), format="wav")
            self.logger.info("Áudio carregado com sucesso para geração de embedding.")
            
            processed_audio = self.preprocess_audio(audio_segment)
            
            signal = torch.tensor(np.array(processed_audio.get_array_of_samples())).float().unsqueeze(0)
            
            signal = torchaudio.transforms.Resample(
                orig_freq=processed_audio.frame_rate, new_freq=self.sample_rate
            )(signal)
            self.logger.info("Áudio reamostrado e preparado para modelo de embeddings.")
            
            embedding = self.model.encode_batch(signal)
            embedding_np = embedding.squeeze().detach().numpy()
            
            self.logger.info("Embedding gerado com sucesso.")
            return embedding_np
        except Exception as e:
            self.logger.error(f"Erro ao processar o áudio para o embedding: {e}")
            raise ValueError(f"Erro ao processar o áudio para o embedding: {e}")