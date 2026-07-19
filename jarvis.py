import ollama
import threading
from wake import listen_for_wake_word
from listen_command import record_command, transcribe
from speak import speak, reset_delay
from actions import (
    open_app, close_app, search_files, open_file, open_folder,
    delete_file, copy_file, move_file, find_installed_app, quick_search_files
)
import gui

MAX_STEPS = 7

SYSTEM_PROMPT = """You are Jarvis, an intelligent voice assistant with full control over the user's PC.
You are the brain — you decide the fastest, most efficient way to complete each request. Think before acting.

Each turn, respond with EXACTLY ONE of these, and nothing else:

ACTION:find_installed_app:<appname>       (fastest way to locate an installed app — try this FIRST for "find/open/close X app" requests)
ACTION:quick_search_files:<keyword>       (fast, checks common folders only — try this before a deep search)
ACTION:search_files:<keyword>             (SLOW, scans every drive fully — only use if the fast options failed)
ACTION:open_app:<appname or full path>    (use a known app name, OR the exact full path returned by find_installed_app/quick_search_files)
ACTION:close_app:<appname>
ACTION:open_file:<full path>
ACTION:open_folder:<full path>
ACTION:delete_file:<full path>
ACTION:copy_file:<source path>|<destination path>
ACTION:move_file:<source path>|<destination path>
ASK:<question you need to ask the user before continuing>
SAY:<short, natural, spoken-style final answer to the user, 1-2 sentences max>

Rules:
- Always try the fastest method first. Never jump straight to a full drive search.
- After an action result comes back, decide: is this enough to answer, do you need another action, or do you need to ask the user something?
- Never repeat the exact same action twice in a row. If a result already gave you what you need (e.g. a file path), use that result in your next action instead of searching again.
- When giving a final answer with SAY, be brief and conversational — never read out raw lists of file paths. Summarize.
- Only use ASK if you genuinely cannot proceed without more info from the user.
- Do not narrate your reasoning. Output only one line in one of the formats above.
"""

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

def parse_response(raw: str):
    raw = raw.strip()
    if raw.startswith("ACTION:"):
        parts = raw.split(":", 2)
        if len(parts) == 3:
            return "ACTION", parts[1], parts[2]
        return "SAY", None, "I tried to take an action but couldn't parse it."
    elif raw.startswith("ASK:"):
        return "ASK", None, raw[len("ASK:"):].strip()
    elif raw.startswith("SAY:"):
        return "SAY", None, raw[len("SAY:"):].strip()
    else:
        return "SAY", None, raw

ACTIONS = {
    "find_installed_app": lambda args: find_installed_app(args[0]),
    "quick_search_files": lambda args: quick_search_files(args[0]),
    "search_files": lambda args: search_files(args[0]),
    "open_app": lambda args: open_app(args[0]),
    "close_app": lambda args: close_app(args[0]),
    "open_file": lambda args: open_file(args[0]),
    "open_folder": lambda args: open_folder(args[0]),
    "delete_file": lambda args: confirm_delete(args[0]),
    "copy_file": lambda args: copy_file(args[0], args[1]),
    "move_file": lambda args: move_file(args[0], args[1]),
}

def ask_llm(messages):
    response = ollama.chat(model="llama3.1:8b", messages=messages, stream=False)
    return response["message"]["content"]

def handle_command(text):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": text}
    ]
    last_raw = None

    for step in range(MAX_STEPS):
        gui.set_state('thinking')
        raw = ask_llm(messages)
        print(f"[Jarvis reasoning] {raw}")

        if raw.strip() == last_raw:
            jarvis_speak("I seem to be stuck repeating myself. Can you rephrase what you'd like?")
            return
        last_raw = raw.strip()

        kind, action_name, payload = parse_response(raw)

        if kind == "SAY":
            jarvis_speak(payload)
            return

        if kind == "ASK":
            audio = speak_and_listen(payload)
            answer = transcribe(audio)
            print(f"You said: {answer}")
            gui.add_message('user', answer if answer else "(no response heard)")
            messages.append({"role": "assistant", "content": raw})
            messages.append({"role": "user", "content": answer if answer else "(no response heard)"})
            continue

        if kind == "ACTION":
            args = payload.split("|")
            action_fn = ACTIONS.get(action_name)
            if action_fn:
                try:
                    result = action_fn(args)
                except Exception as e:
                    result = f"Error: {e}"
            else:
                result = f"Unknown action: {action_name}"

            messages.append({"role": "assistant", "content": raw})
            messages.append({"role": "user", "content": f"Tool result: {result}"})
            continue

    jarvis_speak("I wasn't able to finish that in a reasonable number of steps. Can you clarify what you'd like?")

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