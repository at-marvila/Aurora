import yaml
from core.embeddings.embedding_manager import EmbeddingManager

class EmbeddingLoader:
    def __init__(self, embedding_manager):
        self.embedding_manager = embedding_manager

    def load_intents_embeddings(self, filepath='data/intentions/intents.yaml'):
        with open(filepath, 'r', encoding='utf-8') as file:
            intents_data = yaml.safe_load(file)['intents']
            for intent_name, intent_info in intents_data.items():
                context = intent_info['context']
                phrases = intent_info['triggers']['phrases']
                for phrase in phrases:
                    self.embedding_manager.create_embedding(phrase, intent_name, context)

    def load_actions_embeddings(self, filepath='data/intentions/actions.yaml'):
        with open(filepath, 'r', encoding='utf-8') as file:
            actions_data = yaml.safe_load(file)['actions']
            for action_name, responses in actions_data.items():
                for response in responses:
                    context = response['context']
                    text = response['text']
                    self.embedding_manager.create_embedding(text, action_name, context)

    def load_responses_embeddings(self, filepath='data/intentions/responses.yaml'):
        with open(filepath, 'r', encoding='utf-8') as file:
            responses_data = yaml.safe_load(file)['responses']
            for category, responses in responses_data.items():
                for response in responses:
                    context = response['context']
                    text = response['text']
                    self.embedding_manager.create_embedding(text, category, context)