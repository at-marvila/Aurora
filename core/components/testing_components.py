from unittest.mock import Mock
from core.components.command_executor import CommandExecutor  # Certifique-se de que o caminho está correto

# Mock dos componentes
config_manager = Mock()
embedding_handler = Mock()
context_manager = Mock()
redis_data_retriever = Mock()

# Configuração dos retornos dos mocks
embedding_handler.get_text_embedding.return_value = [0.1, 0.2, 0.3]  # Exemplo de embedding simulado
embedding_handler.find_best_action.return_value = ('register_employee', 0.85)  # Exemplo de ação identificada

# Instancia o CommandExecutor com os mocks
command_executor = CommandExecutor(config_manager, embedding_handler, context_manager, redis_data_retriever)

# Teste de execução com uma frase de exemplo
recognized_text = "registrar colaborador"
command_executor.execute_command(recognized_text)

# Verificação de chamadas aos métodos mockados
embedding_handler.get_text_embedding.assert_called_once_with(recognized_text)
embedding_handler.find_best_action.assert_called_once()
context_manager.reset_context.assert_not_called()  # Deve chamar reset apenas se a similaridade for baixa