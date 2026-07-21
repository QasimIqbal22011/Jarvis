import sounddevice as sd
import numpy as np
import queue
import time


SAMPLE_RATE = 16000
CHANNELS = 1

SILENCE_THRESHOLD = 500
SILENCE_DURATION = 1.0

MAX_RECORD_SECONDS = 10


_audio_queue = queue.Queue()



def _callback(indata, frames, time_info, status):

    if status:
        print(status)

    _audio_queue.put(
        indata.copy()
    )



def listen(on_level=None):

    frames = []

    silence_start = None


    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="int16",
        callback=_callback,
    ):

        start = time.time()


        while True:

            if time.time() - start > MAX_RECORD_SECONDS:
                break


            try:

                chunk = _audio_queue.get(
                    timeout=0.5
                )


            except queue.Empty:

                continue



            frames.append(
                chunk
            )



            volume = np.linalg.norm(
                chunk
            )



            if on_level:

                level = min(
                    1.0,
                    volume / 10000
                )

                on_level(
                    level
                )



            if volume < SILENCE_THRESHOLD:

                if silence_start is None:

                    silence_start = time.time()


                elif (
                    time.time()
                    -
                    silence_start
                    >
                    SILENCE_DURATION
                ):

                    break


            else:

                silence_start = None



    audio = np.concatenate(
        frames,
        axis=0
    )


    if on_level:

        on_level(0)



    return audio.flatten()