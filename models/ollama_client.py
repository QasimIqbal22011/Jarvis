import ollama
import time
from typing import List, Dict, Optional
import json


class OllamaClient:
    """
    Enhanced Ollama client with connection health checks,
    model warming, and streaming support.
    """

    def __init__(
        self,
        model="llama3.1:8b",
        keep_alive="30m",
        num_ctx=2048,
        temperature=0.2,
        max_retries=3,
    ):
        self.model = model
        self.keep_alive = keep_alive
        self.max_retries = max_retries
        self.options = {
            "num_ctx": num_ctx,
            "temperature": temperature,
        }
        self.is_healthy = False
        self._check_connection()

    def _check_connection(self) -> bool:
        """Check if Ollama is running and accessible."""
        try:
            ollama.list()
            self.is_healthy = True
            return True
        except Exception as e:
            print(f"[OllamaClient] Connection check failed: {e}")
            self.is_healthy = False
            return False

    def ping(self) -> bool:
        """Ping Ollama with exponential backoff retry."""
        for attempt in range(self.max_retries):
            if self._check_connection():
                return True
            if attempt < self.max_retries - 1:
                wait_time = 2 ** attempt
                print(f"[OllamaClient] Retrying in {wait_time}s...")
                time.sleep(wait_time)
        return False

    def warmup_model(self) -> bool:
        """Load model into memory to avoid startup latency."""
        try:
            ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": ""}],
                keep_alive=self.keep_alive,
                options=self.options,
            )
            return True
        except Exception as e:
            print(f"[OllamaClient] Model warmup failed: {e}")
            return False

    def chat(self, messages: List[Dict[str, str]]) -> str:
        """Send a chat request to Ollama."""
        if not self.is_healthy:
            if not self.ping():
                raise ConnectionError("Ollama is not responding")

        try:
            response = ollama.chat(
                model=self.model,
                messages=messages,
                stream=False,
                keep_alive=self.keep_alive,
                options=self.options,
            )
            # Log token usage for debugging context limits
            if "eval_count" in response:
                print(
                    f"[OllamaClient] Tokens - Input: {response.get('prompt_eval_count', 0)}, "
                    f"Output: {response.get('eval_count', 0)}"
                )
            return response["message"]["content"]
        except Exception as e:
            self.is_healthy = False
            raise

    def stream(self, messages: List[Dict[str, str]]):
        """Stream a chat response from Ollama."""
        if not self.is_healthy:
            if not self.ping():
                raise ConnectionError("Ollama is not responding")

        try:
            return ollama.chat(
                model=self.model,
                messages=messages,
                stream=True,
                keep_alive=self.keep_alive,
                options=self.options,
            )
        except Exception as e:
            self.is_healthy = False
            raise

    def chat_structured(self, messages: List[Dict[str, str]], schema: Dict) -> Dict:
        """
        Request JSON structured output from Ollama (requires format support).
        Falls back to regular chat if JSON mode is not supported.
        """
        if not self.is_healthy:
            if not self.ping():
                raise ConnectionError("Ollama is not responding")

        try:
            response = ollama.chat(
                model=self.model,
                messages=messages,
                stream=False,
                keep_alive=self.keep_alive,
                options=self.options,
                format=schema,  # JSON schema
            )
            content = response["message"]["content"]
            return json.loads(content)
        except Exception as e:
            print(f"[OllamaClient] Structured output failed, falling back to regular chat: {e}")
            # Fallback to regular chat
            return {"type": "error", "content": self.chat(messages)}