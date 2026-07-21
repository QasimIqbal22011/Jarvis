from enum import Enum


class AssistantState(Enum):

    IDLE = "idle"

    LISTENING = "listening"

    THINKING = "thinking"

    EXECUTING = "executing"

    SPEAKING = "speaking"