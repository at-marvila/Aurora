import logging
import json
from datetime import datetime


class SessionLogger:
    """Classe centralizada para gerenciamento de sessões e logs."""

    def __init__(self, action_name, supermarket_config, user_name=None):
        self.action_name = action_name
        self.supermarket_config = supermarket_config
        self.user_name = user_name
        self.start_time = datetime.now()

        # Informações fixas do local
        self.location = f"{supermarket_config['city']}, {supermarket_config['state']}"
        self.supermarket_name = supermarket_config["name"]

    def log_session_start(self):
        """Loga o início da sessão."""
        start_message = (
            f"\n{'=' * 50}"
            f"\n### Início da Sessão ###"
            f"\nAção: {self.action_name}"
            f"\nData: {self.start_time.strftime('%d/%m/%Y %H:%M:%S')}"
            f"\nLocal: {self.location}"
            f"\nSupermercado: {self.supermarket_name}"
            f"\n{'=' * 50}"
        )
        logging.info(start_message)

    def log_session_end(self, success=True, error_field=None, reason=None):
        """Loga o final da sessão."""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        status = "Sucesso" if success else "Erro"
        reason_message = reason or ("Máximo de tentativas excedido." if not success else "Operação concluída.")

        # Mensagem human-readable
        end_message = (
            f"\n{'=' * 50}"
            f"\n### Fim da Sessão ###"
            f"\nAção: {self.action_name}"
            f"\nUsuário: {self.user_name or 'N/A'}"
            f"\nData: {end_time.strftime('%d/%m/%Y %H:%M:%S')}"
            f"\nLocal: {self.location}"
            f"\nSupermercado: {self.supermarket_name}"
            f"\nDuração: {duration:.2f} segundos"
            f"\nStatus: {status}"
            f"\nMotivo: {reason_message}"
            f"\nCampo com erro: {error_field or 'Nenhum'}"
            f"\n{'=' * 50}"
        )
        logging.info(end_message)

        # Log JSON estruturado (para análise futura ou sistemas de monitoramento)
        log_data = {
            "action": self.action_name,
            "user": self.user_name or "N/A",
            "timestamp": end_time.isoformat(),
            "location": self.location,
            "supermarket": self.supermarket_name,
            "duration_seconds": duration,
            "status": status,
            "error_field": error_field,
            "reason": reason_message,
        }
        logging.info(f"LOG_JSON: {json.dumps(log_data)}")

    def log_event(self, message, level="info"):
        """Loga um evento genérico durante a sessão."""
        log_methods = {
            "info": logging.info,
            "warning": logging.warning,
            "error": logging.error,
        }
        log_methods.get(level, logging.info)(message)