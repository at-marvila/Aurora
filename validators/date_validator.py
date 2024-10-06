import re
from datetime import datetime

def validate_date(text_date):
    """
    Converte uma data falada (texto) para o formato numérico 'ddMMyyyy'.
    Exemplo: '29 de setembro de 1994' -> '29091994'
    """
    try:
        # Tenta converter para um formato numérico
        months = {
            "janeiro": "01", "fevereiro": "02", "março": "03", "abril": "04", "maio": "05", "junho": "06",
            "julho": "07", "agosto": "08", "setembro": "09", "outubro": "10", "novembro": "11", "dezembro": "12"
        }

        # Separar os componentes da data
        for month in months:
            if month in text_date.lower():
                day, year = re.findall(r'\d+', text_date)
                return f'{day.zfill(2)}{months[month]}{year}'
        
        # Se for um formato simples, como "29/09/1994"
        return re.sub(r'\D', '', text_date)

    except Exception as e:
        print(f"Erro ao formatar data: {e}")
        return text_date  # Retorna a data original se falhar