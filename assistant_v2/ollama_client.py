import ollama

from assistant_v2.config import (
    MODEL,
    KEEP_ALIVE,
    TEMPERATURE,
    NUM_CTX,
)


class OllamaClient:

    def __init__(self):
        self.model = MODEL

    def chat(self, messages, stream=False):

        return ollama.chat(
            model=self.model,
            messages=messages,
            stream=stream,
            keep_alive=KEEP_ALIVE,
            options={
                "temperature": TEMPERATURE,
                "num_ctx": NUM_CTX,
            },
        )