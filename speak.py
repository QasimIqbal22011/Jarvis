import pyttsx3
import threading
import time
import gui

_lock = threading.Lock()
_needs_delay = True

def _on_word(name, location, length):
    # pyttsx3/SAPI doesn't expose raw waveform amplitude, so we approximate
    # a "volume" per word from its length. Fed through gui.set_audio_level,
    # the GUI's own smoothing turns this into a natural rise/decay pulse
    # roughly in sync with speech cadence.
    level = min(1.0, 0.45 + length * 0.06)
    gui.set_audio_level(level)

def speak(text, apply_delay=None):
    global _needs_delay
    print(f"Jarvis: {text}")
    with _lock:
        engine = pyttsx3.init()
        engine.setProperty('rate', 175)

        should_delay = _needs_delay if apply_delay is None else apply_delay
        if should_delay:
            time.sleep(0.10)  # let SAPI engine settle before speaking
            _needs_delay = False

        engine.connect('started-word', _on_word)
        engine.say(text)
        engine.runAndWait()
        gui.set_audio_level(0)
        engine.stop()
        del engine

def reset_delay():
    global _needs_delay
    _needs_delay = True