# validators/date_validator.py

import re
from datetime import datetime

MONTHS = {
    "janeiro": "01", "fevereiro": "02", "março": "03", "abril": "04", "maio": "05", "junho": "06",
    "julho": "07", "agosto": "08", "setembro": "09", "outubro": "10", "novembro": "11", "dezembro": "12"
}

def validate_date(text_date):
    """Converte uma data falada (texto) para o formato numérico 'ddMMyyyy'."""
    try:
        for month, month_num in MONTHS.items():
            if month in text_date.lower():
                day, year = re.findall(r'\d+', text_date)
                return f"{day.zfill(2)}{month_num}{year}"
        # Se a data já estiver em um formato numérico, remove caracteres não numéricos
        return re.sub(r"\D", "", text_date)
    except Exception as e:
        print(f"Erro ao formatar data: {e}")
        return "Data inválida"  # Retorna "Data inválida" caso falhe