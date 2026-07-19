import sounddevice as sd
import numpy as np
import collections
import webrtcvad
from faster_whisper import WhisperModel

whisper_model = WhisperModel("small.en", device="cpu", compute_type="int8")
vad = webrtcvad.Vad(2)

def record_command(samplerate=16000, max_duration=8, silence_duration=0.8, on_level=None):
    """on_level: optional callback(level: float 0.0-1.0) fired once per frame
    with the frame's normalized RMS volume, used to drive live GUI feedback."""
    frame_ms = 30
    frame_size = int(samplerate * frame_ms / 1000)
    padding_frames = int(silence_duration * 1000 / frame_ms)
    ring_buffer = collections.deque(maxlen=padding_frames)
    triggered = False
    voiced_frames = []
    max_frames = int(max_duration * 1000 / frame_ms)

    with sd.InputStream(samplerate=samplerate, channels=1, dtype='int16', blocksize=frame_size) as stream:
        print("Listening for your command...")
        for _ in range(max_frames):
            frame, _ = stream.read(frame_size)
            is_speech = vad.is_speech(frame.tobytes(), samplerate)

            if on_level is not None:
                # Normalized RMS volume of this frame. The gain below is a
                # starting point for typical mic input levels — raise it
                # if the sphere barely pulses on your voice, lower it if it
                # maxes out on quiet speech.
                samples = frame.astype(np.float32) / 32768.0
                rms = float(np.sqrt(np.mean(samples ** 2)))
                on_level(min(1.0, rms * 9.0))

            if not triggered:
                ring_buffer.append((frame, is_speech))
                voiced = len([f for f, s in ring_buffer if s])
                if voiced > 0.6 * ring_buffer.maxlen:
                    triggered = True
                    voiced_frames.extend(f for f, s in ring_buffer)
                    ring_buffer.clear()
            else:
                voiced_frames.append(frame)
                ring_buffer.append((frame, is_speech))
                unvoiced = len([f for f, s in ring_buffer if not s])
                if unvoiced > 0.9 * ring_buffer.maxlen:
                    break

    if not voiced_frames:
        return np.array([], dtype=np.float32)

    audio = np.concatenate(voiced_frames).flatten().astype(np.float32) / 32768.0
    return audio

def transcribe(audio, samplerate=16000):
    if audio.size == 0:
        return ""
    segments, _ = whisper_model.transcribe(audio, language="en", vad_filter=True)
    text = " ".join(segment.text for segment in segments)
    return text.strip()