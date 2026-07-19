import ollama


class OllamaClient:

    def __init__(
        self,
        model="llama3.1:8b",
        keep_alive="30m",
        num_ctx=2048,
        temperature=0.2,
    ):
        self.model = model
        self.keep_alive = keep_alive
        self.options = {
            "num_ctx": num_ctx,
            "temperature": temperature,
        }

    def chat(self, messages):
        response = ollama.chat(
            model=self.model,
            messages=messages,
            stream=False,
            keep_alive=self.keep_alive,
            options=self.options,
        )
        return response["message"]["content"]

    def stream(self, messages):
        return ollama.chat(
            model=self.model,
            messages=messages,
            stream=True,
            keep_alive=self.keep_alive,
            options=self.options,
        )