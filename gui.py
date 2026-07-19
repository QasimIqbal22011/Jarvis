import webview
import threading
import time
import sys
import os
import json

def resource_path(relative_path):
    """Works both running as a normal script and as a frozen PyInstaller exe."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

HTML_PATH = resource_path("jarvis_ui.html")

_window = None
_ready_event = threading.Event()

def _on_loaded():
    _ready_event.set()

def create_gui():
    """Blocks until the app exits. Call this on the MAIN thread only."""
    global _window
    _window = webview.create_window(
        "Jarvis",
        HTML_PATH,
        width=380,
        height=640,
        min_size=(320, 420),
        resizable=True,
        frameless=True,
        easy_drag=True,
        on_top=True,
        transparent=True,
        hidden=True,
        background_color="#000000"
    )
    _window.events.loaded += _on_loaded
    _start_audio_level_thread()
    webview.start()

def wait_until_ready(timeout=20):
    _ready_event.wait(timeout)

def show_window():
    if _window:
        try:
            _window.show()
        except Exception:
            pass

def hide_window():
    if _window:
        try:
            _window.hide()
        except Exception:
            pass

def destroy_window():
    if _window:
        try:
            _window.destroy()
        except Exception:
            pass

def set_state(state: str):
    """state: 'idle', 'listening', 'thinking', or 'speaking'"""
    if _window:
        try:
            _window.evaluate_js(f"setJarvisState('{state}')")
        except Exception:
            pass

def add_message(sender: str, text: str):
    """sender: 'user' or 'jarvis'. Appends a chat bubble to the conversation view."""
    if _window:
        try:
            # json.dumps safely escapes quotes/newlines so text can't break the JS call
            safe_sender = json.dumps(sender)
            safe_text = json.dumps(text)
            _window.evaluate_js(f"addMessage({safe_sender}, {safe_text})")
        except Exception:
            pass

# ---------------------------------------------------------------------------
# Live audio level -> sphere pulse.
#
# Both the mic (listen_command.py, ~33 calls/sec) and TTS word events
# (speak.py, a few calls/sec) call set_audio_level() from different
# background threads. Calling evaluate_js() directly from each of them
# caused two problems: the high-frequency mic calls were losing a race
# against evaluate_js's internal result-passing when TTS called it at the
# same time (so mic updates silently never landed), and single-shot spikes
# decayed within one JS frame, reading as a flicker instead of a pulse.
#
# Instead, producers just cheaply store a target level (a float behind a
# lock — no IPC, can't block). One dedicated thread here owns every
# evaluate_js('setAudioLevel...') call, smooths toward the target at a
# fixed, tunable rate, and pushes it on a steady schedule. Only one thread
# ever touches evaluate_js for this, so there's no contention, and the
# smoothing rate below is what controls how "slow and smooth" it feels.
# ---------------------------------------------------------------------------
_audio_level_target = 0.0
_audio_level_lock = threading.Lock()
_audio_level_thread_started = False

# Lower SMOOTHING = slower/smoother motion, higher = snappier/more twitchy.
# At UPDATE_HZ=20 with SMOOTHING=0.15, the sphere takes ~1/3 second to catch
# up to a big volume change — a visible, breathing pulse rather than an
# instant snap or a sluggish crawl. Tweak these two numbers to taste.
_AUDIO_SMOOTHING = 0.15
_AUDIO_UPDATE_HZ = 20

def _audio_level_loop():
    current = 0.0
    interval = 1.0 / _AUDIO_UPDATE_HZ
    while True:
        with _audio_level_lock:
            target = _audio_level_target
        current += (target - current) * _AUDIO_SMOOTHING
        if _window:
            try:
                _window.evaluate_js(f"setAudioLevel({current:.3f})")
            except Exception:
                pass
        time.sleep(interval)

def _start_audio_level_thread():
    global _audio_level_thread_started
    if not _audio_level_thread_started:
        _audio_level_thread_started = True
        threading.Thread(target=_audio_level_loop, daemon=True).start()

def set_audio_level(level: float):
    """Cheap and safe to call at any frequency from any thread — mic frames,
    TTS word events, whatever. Just records the latest target; the
    background thread above handles all the actual GUI pushing."""
    global _audio_level_target
    with _audio_level_lock:
        _audio_level_target = max(0.0, min(1.0, level))

def clear_chat():
    """Clears the conversation view (e.g. on app restart)."""
    if _window:
        try:
            _window.evaluate_js("clearChat()")
        except Exception:
            pass