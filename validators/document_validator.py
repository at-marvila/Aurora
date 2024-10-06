import re
from datetime import datetime

def validate_document(document):
    """
    Remove espaços ou caracteres desnecessários de um número de documento.
    Exemplo: '071 670 419 63' -> '07167041963'
    """
    return re.sub(r'\D', '', document)