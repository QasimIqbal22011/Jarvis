from models.ollama_client import OllamaClient
from models.prompts import SYSTEM_PROMPT, build_system_prompt
import json
import os
from pathlib import Path
from datetime import datetime


class Assistant:
    """
    Enhanced assistant with conversation memory persistence.
    Stores conversation history across sessions for better context awareness.
    """

    MEMORY_FILE = os.path.expanduser("~/.jarvis/conversation_memory.json")

    def __init__(self, enable_memory=True):
        self.llm = OllamaClient()
        self.enable_memory = enable_memory
        self.conversation_history = []
        
        # Create memory directory if needed
        if self.enable_memory:
            os.makedirs(os.path.dirname(self.MEMORY_FILE), exist_ok=True)
            self.load_conversation_history()

    def load_conversation_history(self, max_turns=10):
        """Load recent conversation history from persistent storage."""
        if not os.path.exists(self.MEMORY_FILE):
            self.conversation_history = []
            return

        try:
            with open(self.MEMORY_FILE, 'r') as f:
                all_turns = json.load(f)
            # Keep only the most recent turns for context
            self.conversation_history = all_turns[-max_turns:] if all_turns else []
        except Exception as e:
            print(f"[Assistant] Error loading memory: {e}")
            self.conversation_history = []

    def save_conversation_turn(self, user_message: str, assistant_response: str):
        """Save a conversation turn to persistent memory."""
        if not self.enable_memory:
            return

        try:
            turn = {
                "timestamp": datetime.now().isoformat(),
                "user": user_message,
                "assistant": assistant_response,
            }

            # Load existing history
            all_turns = []
            if os.path.exists(self.MEMORY_FILE):
                with open(self.MEMORY_FILE, 'r') as f:
                    all_turns = json.load(f)

            # Append new turn and keep only recent ones
            all_turns.append(turn)
            all_turns = all_turns[-50:]  # Keep last 50 turns

            # Save back to file
            with open(self.MEMORY_FILE, 'w') as f:
                json.dump(all_turns, f, indent=2)

        except Exception as e:
            print(f"[Assistant] Error saving memory: {e}")

    def get_memory_context(self) -> str:
        """Generate a context string from recent conversation memory."""
        if not self.conversation_history:
            return "No recent conversation history."

        context_lines = ["Recent conversation:"]
        for turn in self.conversation_history[-3:]:  # Show last 3 turns
            context_lines.append(f"  User: {turn.get('user', '')[:100]}")
            context_lines.append(f"  Jarvis: {turn.get('assistant', '')[:100]}")

        return "\n".join(context_lines)

    def ask(self, user_text: str):
        """Ask a question with optional memory context."""
        memory_context = self.get_memory_context() if self.enable_memory else ""
        system_prompt = build_system_prompt(recent_context=memory_context)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text},
        ]

        response = self.llm.chat(messages)
        
        if self.enable_memory:
            self.save_conversation_turn(user_text, response)

        return response

    def ask_messages(self, messages):
        """Ask with a pre-built message list (for multi-turn conversations)."""
        return self.llm.chat(messages)

    def stream_messages(self, messages):
        """Stream a response for real-time output."""
        return self.llm.stream(messages)