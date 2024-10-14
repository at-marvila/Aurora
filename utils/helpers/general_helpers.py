import os
import yaml
import json
import uuid
import tempfile
from datetime import datetime
import logging


def load_yaml_file(relative_path):
    """Carrega um arquivo YAML a partir de um caminho relativo."""
    yaml_path = os.path.join(os.path.dirname(__file__), relative_path)
    with open(yaml_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

def load_employee_template(filepath='C:/Sevent/Dev/Aurora/data/employees/employees.json') -> dict:
    """Carrega o template de colaborador a partir do arquivo employees.json."""
    logger = logging.getLogger(__name__)
    logger.debug("Carregando template de funcionário.")
    with open(filepath, 'r', encoding='utf-8') as file:
        return json.load(file)

def generate_supermarket_id(supermarket_config: dict) -> str:
    """Gera o identificador do supermercado usando o formato definido."""
    return supermarket_config['identifier_format'].format(
        name=supermarket_config['name'],
        state=supermarket_config['state'],
        city_acronym=supermarket_config['acronyms']['city'].get(supermarket_config['city'], supermarket_config['city']),
        district_acronym=supermarket_config['acronyms']['district'].get(supermarket_config['district'], supermarket_config['district']),
        store_number=supermarket_config['store_number']
    )

def get_default_employee_data(supermarket_id: str) -> dict:
    """Retorna os dados padrão do colaborador."""
    return {
        "id": str(uuid.uuid4()),
        "modification_date": datetime.now().isoformat(),
        "register_date": datetime.now().isoformat(),
        "active": True,
        "notification": True,
        "created_by": "Sistema",
        "updated_by": "Sistema",
        "supermarket_id": supermarket_id,
        "recognition_score": 98
    }