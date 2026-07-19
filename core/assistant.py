from models.ollama_client import OllamaClient


class Assistant:

    def __init__(self):
        self.llm = OllamaClient()

    def ask_llm(self, messages):
        response = self.llm.chat(messages)
        return response["message"]["content"]