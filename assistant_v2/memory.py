class Conversation:

    def __init__(self):
        self.messages = []

    def clear(self):
        self.messages.clear()

    def add(self, role, content):

        if isinstance(content, dict):
            self.messages.append(content)
            return

        self.messages.append({
            "role": role,
            "content": str(content),
        })

    def add_system(self, text):
        self.add("system", text)

    def add_user(self, text):
        self.add("user", text)

    def add_assistant(self, text):
        self.add("assistant", text)

    def get(self):
        return list(self.messages)

    def last(self):

        if not self.messages:
            return None

        return self.messages[-1]

    def trim(self, keep_last=20):

        if len(self.messages) <= keep_last:
            return

        system = None

        if self.messages and self.messages[0]["role"] == "system":
            system = self.messages[0]

        recent = self.messages[-(keep_last - 1):]

        if system:
            self.messages = [system] + recent
        else:
            self.messages = recent

    def __len__(self):
        return len(self.messages)