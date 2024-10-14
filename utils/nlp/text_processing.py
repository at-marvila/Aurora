# utils/nlp/text_processing.py

import spacy
from fuzzywuzzy import process, fuzz
from spellchecker import SpellChecker

# Carregar o modelo de linguagem para o português
nlp = spacy.load("pt_core_news_sm")
spell = SpellChecker(language="pt")

def correct_spelling(text):
    """Corrige a ortografia das palavras no texto."""
    corrected_words = [spell.correction(word) if word in spell else word for word in text.split()]
    return " ".join(corrected_words)

def clean_text(text):
    """Remove stop words e lematiza as palavras para melhorar a normalização."""
    doc = nlp(text)
    tokens = [token.lemma_ for token in doc if not token.is_stop]
    return " ".join(tokens)

def normalize_text(text):
    """Aplica correções ortográficas e normaliza o texto para melhorar o processamento."""
    corrected_text = correct_spelling(text.lower().strip())  # Corrige a ortografia e padroniza
    normalized_text = clean_text(corrected_text)  # Remove stop words e lematiza
    return normalized_text

def nlp_processor(recognized_text, command_map):
    """Processa o texto reconhecido, aplicando correções ortográficas e faz o matching com os comandos."""
    normalized_text = normalize_text(recognized_text)
    
    # Tokenize e reconhece entidades no texto normalizado
    doc = nlp(normalized_text)
    tokens = [token.text for token in doc]
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    print(f"Tokens: {tokens}")
    print(f"Entidades reconhecidas: {entities}")

    # Faz o matching do texto normalizado com o mapa de comandos
    matched_command = process.extractOne(normalized_text, command_map.keys(), scorer=fuzz.partial_ratio)
    
    if matched_command and matched_command[1] > 70:
        return command_map[matched_command[0]]
    else:
        return None