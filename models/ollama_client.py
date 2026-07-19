import ollama


class OllamaClient:
    def __init__(
        self,
        model="llama3.1:8b",
        keep_alive="10m",
        num_ctx=2048,
        temperature=0.2,
    ):
        self.model = model
        self.keep_alive = keep_alive
        self.options = {
            "num_ctx": num_ctx,
            "temperature": temperature,
        }

    def chat(self, messages, stream=False):
        return ollama.chat(
            model=self.model,
            messages=messages,
            stream=stream,
            keep_alive=self.keep_alive,
            options=self.options,
        )