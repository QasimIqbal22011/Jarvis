import pyttsx3
import threading
import time


_lock = threading.Lock()
_engine = None


def reset_delay():
    """Reset TTS engine state and clear any pending delays."""
    global _engine
    try:
        if _engine:
            _engine.stop()
    except Exception:
        pass
    # Small delay to ensure clean state
    time.sleep(0.05)


def speak(text):

    print(
        f"Jarvis: {text}"
    )


    with _lock:

        engine = pyttsx3.init()

        engine.setProperty(
            "rate",
            175
        )


        time.sleep(
            0.1
        )


        engine.say(
            text
        )


        engine.runAndWait()


        engine.stop()

        del engine