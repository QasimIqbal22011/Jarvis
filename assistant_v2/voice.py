from assistant_v2.assistant import Assistant

from assistant_v2.speech.microphone import listen
from assistant_v2.speech.transcriber import speech_to_text
from assistant_v2.speech.tts import say

from assistant_v2.state import AssistantState
from assistant_v2.gui_bridge import GUIBridge
from assistant_v2.profiler import Profiler

import time


WAKE_PHRASES = [
    "hey jarvis",
    "hey jarvis,",
    "ok jarvis",
    "okay jarvis",
]


assistant = Assistant()


profiler = Profiler()


gui_bridge = GUIBridge(
    assistant.events
)



assistant.events.subscribe(
    lambda event, data:
        print(
            f"[EVENT] {event}: {data}"
        )
)



def extract_command(text):

    if not text:
        return None


    cleaned = text.lower().strip()


    for phrase in WAKE_PHRASES:

        if cleaned.startswith(phrase):

            command = cleaned[
                len(phrase):
            ].strip()


            return command



    return None



def run():

    print(
        "Jarvis active listening mode started."
    )

    print(
        "Say 'Hey Jarvis' followed by a command."
    )


    while True:


        assistant.state.set(
            AssistantState.LISTENING
        )


        profiler.start(
            "Listening"
        )


        audio = listen(
            on_level=None
        )


        profiler.stop(
            "Listening"
        )



        profiler.start(
            "Transcription"
        )


        text = speech_to_text(
            audio
        )


        profiler.stop(
            "Transcription"
        )



        if not text:
            continue



        print(
            "Heard:",
            text
        )



        command = extract_command(
            text
        )


        # no wake phrase
        # ignore completely

        if command is None:

            continue



        print(
            "Command:",
            command
        )



        assistant.events.emit(
            "message",
            ("user", command)
        )



        profiler.start(
            "Assistant"
        )


        reply = assistant.think(
            command
        )


        profiler.stop(
            "Assistant"
        )



        assistant.state.set(
            AssistantState.SPEAKING
        )



        assistant.events.emit(
            "message",
            ("jarvis", reply)
        )



        say(
            reply
        )



        assistant.state.set(
            AssistantState.LISTENING
        )