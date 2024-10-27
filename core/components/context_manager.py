# core/components/context_manager.py

class ContextManager:
    def __init__(self):
        self.current_context = "saudacao"
    
    def get_current_context(self):
        return self.current_context
    
    def update_context(self, new_context):
        self.current_context = new_context
    
    def reset_context(self):
        """Redefine o contexto para o valor inicial."""
        self.current_context = "saudacao"
    
    def is_action_allowed(self, action_context):
        # Retorna True se a ação estiver permitida no contexto atual
        return action_context == self.current_context