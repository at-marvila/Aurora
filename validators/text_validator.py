# validators/text_validator.py

import re

def validate_text(text):
    """
    Valida e limpa o texto fornecido, removendo caracteres especiais indesejados
    e garantindo que ele esteja em um formato apropriado para uso.
    
    Exemplo:
        Entrada: "Olá, meu nome é João! #123"
        Saída: "Olá meu nome é João 123"
    
    :param text: O texto a ser validado e limpo.
    :return: Texto validado e limpo.
    """
    if not isinstance(text, str):
        raise ValueError("O valor fornecido não é uma string válida")

    # Remove caracteres especiais, mantendo letras, números e espaços
    clean_text = re.sub(r'[^a-zA-Z0-9\s]', '', text)

    # Remove espaços extras
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()

    return clean_text

def validate_alphanumeric(text):
    """
    Valida se o texto contém apenas caracteres alfanuméricos.
    
    Exemplo:
        Entrada: "Joao123"
        Saída: "Joao123"
        
    :param text: O texto a ser validado.
    :return: True se for alfanumérico, False caso contrário.
    """
    return text.isalnum()