from .document_validator import validate_document, validate_cpf
from .date_validator import validate_date
from .text_validator import validate_text, validate_alphanumeric
from .data_cleaner import (
    validate_and_correct_email, 
    validate_and_correct_phone, 
    validate_data as clean_data
)

class Validator:
    """Classe centralizada para validar e corrigir diferentes tipos de dados."""

    @staticmethod
    def validate_document(document):
        """Valida e retorna um documento, incluindo CPF."""
        return validate_document(document)
    
    @staticmethod
    def validate_cpf(cpf):
        """Valida exclusivamente um CPF."""
        return validate_cpf(cpf)

    @staticmethod
    def validate_date(text_date):
        """Valida uma data fornecida no formato DD/MM/AAAA."""
        return validate_date(text_date)

    @staticmethod
    def validate_text(text):
        """Valida se o texto é apenas alfabético."""
        return validate_text(text)
    
    @staticmethod
    def validate_alphanumeric(text):
        """Valida se o texto contém apenas caracteres alfanuméricos."""
        return validate_alphanumeric(text)

    @staticmethod
    def validate_and_correct_email(email):
        """Valida e corrige um email, se necessário."""
        return validate_and_correct_email(email)
    
    @staticmethod
    def validate_and_correct_phone(phone):
        """Valida e corrige um número de telefone, se necessário."""
        return validate_and_correct_phone(phone)

    @staticmethod
    def validate_data(data):
        """Realiza limpeza geral e validação nos dados fornecidos."""
        return clean_data(data)