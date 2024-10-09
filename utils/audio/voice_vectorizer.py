import os
import torch
import numpy as np
import librosa
from speechbrain.pretrained import SpeakerRecognition

# Desativar o aviso de symlinks
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

def generate_voice_embedding(audio_path, sample_rate=16000):
    """
    Gera um embedding de características de voz a partir de um arquivo de áudio.
    Utiliza um modelo pré-treinado para gerar o embedding.

    :param audio_path: Caminho do arquivo de áudio
    :param sample_rate: A taxa de amostragem do áudio (default: 16000)
    :return: Um embedding da voz como vetor numpy
    """
    try:
        # Carregar o modelo pré-treinado de reconhecimento de voz da SpeechBrain
        model = SpeakerRecognition.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb", savedir="pretrained_models")

        # Carregar o áudio usando librosa
        audio_data, sr = librosa.load(audio_path, sr=sample_rate)

        # Verificar se o áudio está no formato adequado (numpy array)
        if not isinstance(audio_data, np.ndarray):
            raise ValueError(f"Formato de áudio inválido: esperado np.ndarray, mas obteve {type(audio_data)}")

        # Converter o áudio para tensor do PyTorch
        audio_tensor = torch.tensor(audio_data).unsqueeze(0)  # Adicionar dimensão extra para batch

        # Gerar o embedding a partir do tensor de áudio
        embedding = model.encode_batch(audio_tensor).detach().cpu().numpy()

        # Retornar o embedding como um vetor de numpy para armazenamento ou comparação
        return embedding.flatten()

    except Exception as e:
        print(f"Erro ao gerar o embedding de voz: {e}")
        return None