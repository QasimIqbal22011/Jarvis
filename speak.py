import pyttsx3
import threading
import time


_lock = threading.Lock()


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