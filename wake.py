import openwakeword
from openwakeword.model import Model
import sounddevice as sd
import numpy as np

openwakeword.utils.download_models()

model = Model(wakeword_models=["hey_jarvis"])

WAKE_THRESHOLD = 0.6
CONSECUTIVE_FRAMES_REQUIRED = 2

def listen_for_wake_word():
    samplerate = 16000
    blocksize = 1280
    consecutive_hits = 0

    with sd.InputStream(samplerate=samplerate, channels=1, dtype='int16', blocksize=blocksize) as stream:
        print("Listening for 'Hey Jarvis'...")
        while True:
            audio_chunk, _ = stream.read(blocksize)
            audio_chunk = audio_chunk.flatten()
            prediction = model.predict(audio_chunk)
            score = prediction["hey_jarvis"]

            if score > WAKE_THRESHOLD:
                consecutive_hits += 1
            else:
                consecutive_hits = 0

            if consecutive_hits >= CONSECUTIVE_FRAMES_REQUIRED:
                print("Wake word detected!")
                model.reset()
                return