# validators/text_validator.py

import re

def validate_text(text):
    """Remove caracteres especiais e espaços extras do texto fornecido."""
    if not isinstance(text, str):
        raise ValueError("O valor fornecido não é uma string válida")
    
    # Remove caracteres especiais e mantém letras, números e espaços
    clean_text = re.sub(r"[^\w\s]", "", text).strip()
    return re.sub(r"\s+", " ", clean_text)

def validate_alphanumeric(text):
    """Valida se o texto contém apenas caracteres alfanuméricos."""
    return text.isalnum()