# validators/data_cleaner.py

import re
from utils.nlp.text_processing import correct_spelling

def validate_and_correct_email(email):
    """Corrige e valida o formato de e-mail."""
    # Substitui as palavras "arroba" por "@" e "ponto" por "."
    email = email.replace(" arroba ", "@").replace(" ponto ", ".")
    
    # Aplica uma expressão regular robusta para verificar o formato do e-mail
    if re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
        return email
    else:
        # Se não for um formato válido, podemos corrigir o erro com uma função NLP ou deixar para o usuário revisar
        return correct_spelling(email)

def validate_and_correct_phone(phone):
    """Remove espaços e valida se o número é válido (apenas dígitos)."""
    phone = re.sub(r"\s+", "", phone)
    return phone if phone.isdigit() else None

def validate_and_correct_dob(dob):
    """Valida e formata a data de nascimento."""
    # Remover caracteres não numéricos e tentar formatar a data
    dob = re.sub(r"\D", "", dob)  # Remove tudo que não for número
    if len(dob) == 8:
        return dob  # Formato correto: YYYYMMDD
    else:
        # Caso não tenha 8 caracteres numéricos, retorna "Data inválida"
        return "Data inválida"

def validate_and_correct_name(name):
    """Aplica correção ortográfica ao nome."""
    return correct_spelling(name)

def validate_data(data):
    """Aplica todas as validações e correções em um dicionário de dados."""
    return {
        "email": validate_and_correct_email(data.get("email", "")),
        "contact_number": validate_and_correct_phone(data.get("contact_number", "")),
        "dob": validate_and_correct_dob(data.get("dob", "")),
        "name": validate_and_correct_name(data.get("name", "")),
        "last_name": validate_and_correct_name(data.get("last_name", ""))
    }