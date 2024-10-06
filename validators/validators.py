# validators/validator.py

# Importando os métodos de validação de outros módulos
from .document_validator import validate_document
from .date_validator import validate_date
from .text_validator import validate_text

class Validator:
    """
    Classe central para validar diferentes tipos de dados.
    Pode ser expandida conforme mais tipos de validação forem necessários.
    """

    @staticmethod
    def validate_document(document):
        """
        Valida e formata o número do documento.
        :param document: Número de documento em formato texto (pode conter espaços ou caracteres extras).
        :return: Documento formatado (somente números).
        """
        return validate_document(document)
    
    @staticmethod
    def validate_date(text_date):
        """
        Valida e formata uma data falada ou escrita.
        :param text_date: Data em formato texto (pode conter o nome do mês ou ser numérico).
        :return: Data no formato numérico 'ddMMyyyy'.
        """
        return validate_date(text_date)

    @staticmethod
    def validate_text(text):
        """
        Limpa o texto, removendo caracteres especiais e aplicando formatação necessária.
        :param text: Texto a ser limpo e validado.
        :return: Texto limpo e validado.
        """
        return validate_text(text)