from models.ollama_client import OllamaClient
from models.prompts import SYSTEM_PROMPT


class Assistant:

    def __init__(self):
        self.llm = OllamaClient()

    def ask(self, user_text):
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text},
        ]

        return self.llm.chat(messages)

    def ask_messages(self, messages):
        return self.llm.chat(messages)

    def stream_messages(self, messages):
        return self.llm.stream(messages)