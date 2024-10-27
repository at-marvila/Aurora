import logging
import importlib

class ActionMapper:
    def __init__(self, context_manager, config_manager):
        self.context_manager = context_manager
        self.config_manager = config_manager
        self.action_paths = {
            "register_employee": "core.actions.register.register_employee.RegisterEmployee",
            "register_client": "core.actions.register.register_client.RegisterClient",
            "register_timekeeping": "core.actions.register.register_timekeeping.RegisterTimekeeping",
            "deal_of_day": "core.actions.promotion.deal_of_day.DealOfDay"
        }

    def execute_action(self, action_name):
        """Executa a ação com base no nome, carregando o módulo apropriado e retornando o resultado."""
        module_path = self.action_paths.get(action_name)
        if not module_path:
            logging.warning(f"Ação '{action_name}' não encontrada.")
            return "Ação desconhecida."

        try:
            # Carrega o módulo dinamicamente
            module_name, class_name = module_path.rsplit('.', 1)
            module = importlib.import_module(module_name)
            action_class = getattr(module, class_name)
            action_instance = action_class()

            # Executa a ação e captura o resultado
            result = action_instance.execute()
            logging.info(f"Ação '{action_name}' executada com sucesso.")
            return result if result else "Ação executada, mas sem resposta definida."

        except (ImportError, AttributeError) as e:
            logging.error(f"Erro ao carregar/instanciar '{action_name}': {e}")
            return f"Erro ao executar a ação '{action_name}'."
        except Exception as e:
            logging.error(f"Erro inesperado ao executar '{action_name}': {e}")
            return f"Erro inesperado ao executar a ação '{action_name}'."