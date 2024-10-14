# validators/data_cleaner.py

import re
from utils.nlp.text_processing import correct_spelling

def validate_and_correct_email(email):
    """Corrige e valida o formato de e-mail."""
    email = email.replace(" arroba ", "@").replace(" ponto ", ".")
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):  # Verifica formato de e-mail
        email = correct_spelling(email)  # Corrige usando NLP
    return email

def validate_and_correct_phone(phone):
    """Remove espaços e valida se o número é composto apenas de dígitos."""
    phone = phone.replace(" ", "")
    return phone if phone.isdigit() else None

def validate_and_correct_dob(dob):
    """Valida e formata a data de nascimento."""
    dob = re.sub(r"[^0-9]", "", dob)
    return dob if len(dob) == 8 else "Data inválida"  # Exemplo: YYYYMMDD

def validate_and_correct_name(name):
    """Aplica correção ortográfica no nome."""
    return correct_spelling(name)

def validate_data(data):
    """Aplica todas as validações e correções no conjunto de dados."""
    corrected_data = {
        "email": validate_and_correct_email(data.get("email", "")),
        "contact_number": validate_and_correct_phone(data.get("contact_number", "")),
        "dob": validate_and_correct_dob(data.get("dob", "")),
        "name": validate_and_correct_name(data.get("name", "")),
        "last_name": validate_and_correct_name(data.get("last_name", ""))
    }
    return corrected_data