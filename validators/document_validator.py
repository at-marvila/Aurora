# validators/document_validator.py

import re

def validate_document(document):
    """Remove caracteres não numéricos de um número de documento."""
    return re.sub(r"\D", "", document)