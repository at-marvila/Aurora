import re

def validate_document(document):
    """Valida um CPF para garantir que tenha exatamente 11 números e seja válido."""
    cleaned_document = re.sub(r"\D", "", document)  # Remove caracteres não numéricos
    if len(cleaned_document) < 11:
        raise ValueError("O CPF tem menos de 11 números.")
    if len(cleaned_document) > 11:
        raise ValueError("O CPF tem mais de 11 números.")
    if not validate_cpf(cleaned_document):
        raise ValueError("O CPF informado é inválido.")
    return cleaned_document

def validate_cpf(cpf):
    """Valida o CPF com base nos dígitos verificadores."""
    if len(cpf) != 11 or cpf in [str(x) * 11 for x in range(10)]:
        return False
    
    def calculate_digit(digits, multiplier_start):
        total = sum(int(d) * multiplier for d, multiplier in zip(digits, range(multiplier_start, 1, -1)))
        remainder = (total * 10) % 11
        return remainder if remainder < 10 else 0

    first_digit = calculate_digit(cpf[:9], 10)
    second_digit = calculate_digit(cpf[:10], 11)

    return cpf[-2:] == f"{first_digit}{second_digit}"
