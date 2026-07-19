import ctypes
import sys
import os
import threading
import pythoncom
import pystray
from PIL import Image, ImageDraw
import gui
from jarvis import main as jarvis_main

stop_event = threading.Event()

# When packaged as a --noconsole exe there is no visible console for print()
# output, so redirect stdout/stderr to a log file for debugging.
if getattr(sys, 'frozen', False):
    log_path = os.path.join(os.path.expanduser("~"), "jarvis_log.txt")
    log_file = open(log_path, "a", buffering=1)
    sys.stdout = log_file
    sys.stderr = log_file

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def relaunch_as_admin():
    if getattr(sys, 'frozen', False):
        exe = sys.executable
        params = " ".join(sys.argv[1:])
        ctypes.windll.shell32.ShellExecuteW(None, "runas", exe, params, None, 1)
    else:
        script = os.path.abspath(__file__)
        params = " ".join([f'"{script}"'] + sys.argv[1:])
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)

def create_tray_image():
    img = Image.new('RGB', (64, 64), color=(20, 20, 20))
    draw = ImageDraw.Draw(img)
    draw.ellipse((8, 8, 56, 56), fill=(0, 150, 255))
    return img

def on_exit(icon, item):
    stop_event.set()
    icon.stop()
    gui.destroy_window()

def jarvis_worker():
    pythoncom.CoInitialize()
    try:
        jarvis_main(stop_event)
    finally:
        pythoncom.CoUninitialize()

def run_tray():
    icon = pystray.Icon(
        "Jarvis",
        create_tray_image(),
        "Jarvis Assistant",
        menu=pystray.Menu(
            pystray.MenuItem("Jarvis is running (Admin)", None, enabled=False),
            pystray.MenuItem("Exit", on_exit)
        )
    )
    icon.run()

if __name__ == "__main__":
    if not is_admin():
        relaunch_as_admin()
        sys.exit()

    tray_thread = threading.Thread(target=run_tray, daemon=True)
    tray_thread.start()

    worker_thread = threading.Thread(target=jarvis_worker, daemon=True)
    worker_thread.start()

    gui.create_gui()  # blocks on the main thread until the app exits