import logging
import json
from datetime import datetime


class SessionLogger:
    def __init__(self, supermarket_config, action_name):
        self.supermarket_config = supermarket_config
        self.action_name = action_name
        self.start_time = None
        self.end_time = None
        self.status = None
        self.error_details = None

    def start_session(self):
        """Inicia uma nova sessão."""
        self.start_time = datetime.now()
        location = f"{self.supermarket_config['city']}, {self.supermarket_config['state']} - {self.supermarket_config['name']}"
        logging.info(f"[{self.start_time.strftime('%H:%M:%S')}] === Nova Sessão Iniciada ===\n"
                     f"Ação: {self.action_name}\n"
                     f"Local: {location}\n"
                     f"Data: {self.start_time.strftime('%d/%m/%Y %H:%M:%S')}\n"
                     f"{'='*50}")

    def log_event(self, message):
        """Registra um evento no log da sessão."""
        current_time = datetime.now().strftime('%H:%M:%S')
        logging.info(f"[{current_time}] {message}")

    def log_error(self, field, message):
        """Registra um erro específico relacionado a um campo."""
        current_time = datetime.now().strftime('%H:%M:%S')
        logging.info(f"[{current_time}] Erro no campo '{field}': {message}")

    def end_session(self, status, error_details=None):
        """Finaliza a sessão e registra o resumo."""
        self.end_time = datetime.now()
        self.status = status
        self.error_details = error_details
        duration = (self.end_time - self.start_time).total_seconds()

        session_summary = {
            "action": self.action_name,
            "status": self.status,
            "location": f"{self.supermarket_config['city']}, {self.supermarket_config['state']} - {self.supermarket_config['name']}",
            "start_time": self.start_time.strftime('%d/%m/%Y %H:%M:%S'),
            "end_time": self.end_time.strftime('%d/%m/%Y %H:%M:%S'),
            "duration": f"{duration:.2f} segundos",
            "error_details": self.error_details if self.error_details else "Nenhum",
        }

        # Log em formato JSON
        logging.info(f"[{self.end_time.strftime('%H:%M:%S')}] Sessão Concluída: {json.dumps(session_summary, indent=4, ensure_ascii=False)}")
        logging.info(f"[{self.end_time.strftime('%H:%M:%S')}] {'='*50}")