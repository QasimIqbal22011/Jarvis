from models.ollama_client import OllamaClient
from models.prompts import SYSTEM_PROMPT
import threading
from wake import listen_for_wake_word
from listen_command import record_command, transcribe
from core.assistant import Assistant
from core.state import AssistantState
from core.router import CommandRouter
from speak import speak, reset_delay
from actions import (
    open_app, open_url, close_app, search_files, open_file, open_folder,
    delete_file, copy_file, move_file, find_installed_app, quick_search_files
)
import gui

MAX_STEPS = 7
assistant = Assistant()

AFFIRMATIVE_WORDS = {"yes", "yeah", "yep", "confirm", "correct", "do it", "go ahead", "sure"}

def is_affirmative(text: str) -> bool:
    text = text.lower().strip()
    return any(word in text for word in AFFIRMATIVE_WORDS)

def jarvis_speak(text):
    gui.add_message('jarvis', text)
    gui.set_state('speaking')
    speak(text)
    gui.set_state('listening')

def speak_and_listen(prompt, max_duration=8):
    """Speaks `prompt` while the mic is already warming up in parallel,
    so recording starts capturing before the user even begins talking."""
    result = {}

    def recorder():
        result["audio"] = record_command(max_duration=max_duration, on_level=gui.set_audio_level)

    t = threading.Thread(target=recorder)
    t.start()
    gui.add_message('jarvis', prompt)
    gui.set_state('speaking')
    speak(prompt)
    gui.set_state('listening')
    t.join()
    gui.set_audio_level(0)
    return result.get("audio")

def confirm_delete(path: str) -> str:
    audio = speak_and_listen(f"Are you sure you want to delete {path}? Say yes to confirm.")
    response = transcribe(audio)
    print(f"You said: {response}")
    if response:
        gui.add_message('user', response)
    if response and is_affirmative(response):
        return delete_file(path)
    else:
        return "Okay, cancelled. Nothing was deleted."

def accumulate_stream(messages):
    """
    Accumulate a complete response from the LLM stream.
    Ensures we get the full response before parsing to avoid fragmentation.
    """
    raw = ""
    try:
        for chunk in assistant.stream_messages(messages):
            if "message" not in chunk:
                continue

            content = chunk["message"].get("content", "")
            raw += content

            # Early exit on complete command (optimization)
            if raw.startswith(("ACTION:", "SAY:", "ASK:")) and "\n" in raw:
                break

        return raw.strip()
    except Exception as e:
        print(f"[Jarvis] Stream error: {e}")
        return ""


def parse_response(raw: str):
    """
    Parse LLM response with robust error handling.
    Case-insensitive and handles whitespace variations.
    """
    raw = raw.strip()
    
    # Try ACTION: format
    if raw.upper().startswith("ACTION:"):
        parts = raw.split(":", 2)
        if len(parts) >= 3:
            return "ACTION", parts[1].strip(), parts[2].strip()
        return "SAY", None, "I tried to take an action but couldn't parse the arguments."
    
    # Try ASK: format
    if raw.upper().startswith("ASK:"):
        question = raw[4:].strip()
        return "ASK", None, question
    
    # Try SAY: format
    if raw.upper().startswith("SAY:"):
        response = raw[4:].strip()
        return "SAY", None, response
    
    # Fallback: treat as response
    return "SAY", None, raw


def handle_command(text):
    """
    Handle a command with improved parsing, error recovery, and loop detection.
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": text}
    ]
    last_raw = None
    max_follow_ups = 3  # Limit follow-up turns
    follow_up_count = 0

    for step in range(MAX_STEPS):
        gui.set_state('thinking')
        
        # Accumulate full response before parsing
        raw = accumulate_stream(messages)
        
        if not raw:
            jarvis_speak("I didn't get a response from the language model. Please try again.")
            return

        print(f"[Jarvis reasoning] {raw}")

        # Detect infinite loops
        if raw.strip() == last_raw:
            jarvis_speak("I seem to be stuck repeating myself. Can you rephrase what you'd like?")
            return
        last_raw = raw.strip()

        kind, action_name, payload = parse_response(raw)

        if kind == "SAY":
            jarvis_speak(payload)
            return

        if kind == "ASK":
            # Limit follow-up questions
            if follow_up_count >= max_follow_ups:
                jarvis_speak("I asked too many questions. Let's start over with a clearer request.")
                return
            
            follow_up_count += 1
            audio = speak_and_listen(payload)
            answer = transcribe(audio)
            print(f"You said: {answer}")
            gui.add_message('user', answer if answer else "(no response heard)")
            messages.append({"role": "assistant", "content": raw})
            messages.append({"role": "user", "content": answer if answer else "(no response heard)"})
            continue

        if kind == "ACTION":
            success, result = router.execute(action_name, payload)

            if not success:
                result = f"Error: {result}"

            messages.append({"role": "assistant", "content": raw})
            messages.append({"role": "user", "content": f"Tool result: {result}"})
            continue

    jarvis_speak("I wasn't able to finish that in a reasonable number of steps. Can you clarify what you'd like?")


# Initialize actions dictionary
ACTIONS = {
    "find_installed_app": lambda args: find_installed_app(args[0]) if args else "No app name provided",
    "quick_search_files": lambda args: quick_search_files(args[0]) if args else "No keyword provided",
    "search_files": lambda args: search_files(args[0]) if args else "No keyword provided",
    "open_app": lambda args: open_app(args[0]) if args else "No app name provided",
    "open_url": lambda args: open_url(args[0], args[1] if len(args) > 1 else "chrome") if args else "No URL provided",
    "close_app": lambda args: close_app(args[0]) if args else "No app name provided",
    "open_file": lambda args: open_file(args[0]) if args else "No file path provided",
    "open_folder": lambda args: open_folder(args[0]) if args else "No folder path provided",
    "delete_file": lambda args: confirm_delete(args[0]) if args else "No file path provided",
    "copy_file": lambda args: copy_file(args[0], args[1]) if len(args) >= 2 else "Source and destination paths required",
    "move_file": lambda args: move_file(args[0], args[1]) if len(args) >= 2 else "Source and destination paths required",
}

# Initialize router with actions
router = CommandRouter(ACTIONS)


def main(stop_event=None):
    gui.wait_until_ready()
    jarvis_speak("Jarvis is online.")
    while not (stop_event and stop_event.is_set()):
        listen_for_wake_word()
        reset_delay()
        gui.show_window()
        gui.set_state('listening')

        audio = speak_and_listen("Yes?")
        text = transcribe(audio)
        if not text:
            gui.set_state('idle')
            gui.hide_window()
            continue
        print(f"You said: {text}")
        gui.add_message('user', text)
        handle_command(text)

        # Follow-up window: keep listening without requiring the wake word again
        while True:
            gui.set_state('listening')
            audio = record_command(max_duration=4, on_level=gui.set_audio_level)
            gui.set_audio_level(0)
            text = transcribe(audio)
            if not text:
                break  # silence — go back to waiting for "Hey Jarvis"
            print(f"You said: {text}")
            gui.add_message('user', text)
            handle_command(text)

        gui.set_state('idle')
        gui.hide_window()