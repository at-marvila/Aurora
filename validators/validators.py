# validators/validators.py

from .document_validator import validate_document
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
        return validate_document(document)
    
    @staticmethod
    def validate_date(text_date):
        return validate_date(text_date)

    @staticmethod
    def validate_text(text):
        return validate_text(text)
    
    @staticmethod
    def validate_alphanumeric(text):
        return validate_alphanumeric(text)

    @staticmethod
    def validate_and_correct_email(email):
        return validate_and_correct_email(email)
    
    @staticmethod
    def validate_and_correct_phone(phone):
        return validate_and_correct_phone(phone)

    @staticmethod
    def validate_data(data):
        return clean_data(data)