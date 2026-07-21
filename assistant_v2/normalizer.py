import re


class TextNormalizer:

    PHRASES = {
        "note pad": "notepad",
        "node pad": "notepad",
        "notepadd": "notepad",
        "notepat": "notepad",
        "notepads": "notepad",

        "note book": "notebook",

        "file explorer": "explorer",
        "windows explorer": "explorer",

        "command prompt": "cmd",

        "control panel": "control panel",

        "windows setting": "settings",
        "window setting": "settings",
        "windows settings": "settings",

        "task manager": "task manager",

        "google chrome": "chrome",

        "power shell": "powershell",
    }

    FIRST_WORDS = {

        "launch": "open",
        "run": "open",
        "start": "open",

        "quit": "close",
        "exit": "close",
        "end": "close",
        "stop": "close",
        "kill": "close",
        "terminate": "close",

        "closed": "close",
        "closing": "close",
        "opened": "open",
        "opening": "open",
        "started": "open",
        "running": "open",
    }

    COMMON_ERRORS = {

        "oppen": "open",
        "opne": "open",
        "openn": "open",

        "stard": "start",
        "strat": "start",
        "stat": "start",

        "launchh": "launch",

        "clsoe": "close",
        "cls": "close",

        "settngs": "settings",
        "setings": "settings",
        "settingss": "settings",

        "explore": "explorer",
    }

    @classmethod
    def normalize(cls, text: str):

        text = text.lower()

        text = re.sub(r"[^\w\s:\\./-]", " ", text)

        text = re.sub(r"\s+", " ", text).strip()

        for wrong, correct in cls.COMMON_ERRORS.items():
            text = text.replace(wrong, correct)

        for phrase, replacement in cls.PHRASES.items():
            text = text.replace(phrase, replacement)

        words = text.split()

        if words:

            words[0] = cls.FIRST_WORDS.get(
                words[0],
                words[0]
            )

        return " ".join(words)