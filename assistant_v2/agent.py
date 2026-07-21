from assistant_v2.ollama_client import OllamaClient


class Agent:

    def __init__(self):

        self.client = OllamaClient()

        print("Loading LLM into memory...")

        self.client.chat(
            [
                {
                    "role": "system",
                    "content": "Reply only with SAY, ASK or ACTION."
                },
                {
                    "role": "user",
                    "content": "Hello"
                }
            ]
        )

        print("LLM ready.")

    def think(self, messages):

        response = self.client.chat(messages)

        return response["message"]["content"]