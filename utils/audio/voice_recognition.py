import numpy as np
import torchaudio
import torch
from speechbrain.inference import EncoderClassifier
from pydub import AudioSegment
import noisereduce as nr
import io

class VoiceRecognition:
    def __init__(self, sample_rate=44100):
        self.model = EncoderClassifier.from_hparams(source="speechbrain/spkrec-xvect-voxceleb")
        self.sample_rate = sample_rate

    def preprocess_audio(self, audio_segment):
        """Preprocessa o áudio aplicando normalização e redução de ruído."""
        normalized_audio = audio_segment.apply_gain(-audio_segment.max_dBFS)  # Normalização
        audio_data = np.array(normalized_audio.get_array_of_samples())
        reduced_noise_audio = nr.reduce_noise(y=audio_data, sr=normalized_audio.frame_rate)
        
        processed_audio = AudioSegment(
            reduced_noise_audio.tobytes(),
            frame_rate=normalized_audio.frame_rate,
            sample_width=normalized_audio.sample_width,
            channels=normalized_audio.channels
        )
        return processed_audio

    def generate_embedding(self, audio_data):
        """
        Gera o embedding do áudio fornecido.
        :param audio_data: Bytes do áudio.
        :return: Embedding do áudio.
        """
        try:
            audio_segment = AudioSegment.from_file(io.BytesIO(audio_data), format="wav")
            processed_audio = self.preprocess_audio(audio_segment)
            
            # Converter o áudio para um tensor compatível com torchaudio
            signal = torch.tensor(np.array(processed_audio.get_array_of_samples())).float().unsqueeze(0)
            signal = torchaudio.transforms.Resample(orig_freq=processed_audio.frame_rate, new_freq=self.sample_rate)(signal)
            
            # Gerar o embedding
            embedding = self.model.encode_batch(signal)
            embedding_np = embedding.squeeze().detach().numpy()
            
            return embedding_np
        except Exception as e:
            raise ValueError(f"Erro ao processar o áudio para o embedding: {e}")