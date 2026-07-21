from speak import speak


def say(text):

    speak(text)

    # Wait until the speech engine has completely finished
    if hasattr(speak, "wait_until_done"):
        speak.wait_until_done()