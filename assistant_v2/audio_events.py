import threading


class AudioEventManager:

    def __init__(self, events):

        self.events = events


    def emit_level(self, level):

        self.events.emit(
            "audio_level",
            level
        )