import subprocess
import os
import shutil
import string
import getpass
import psutil
from send2trash import send2trash

USERNAME = getpass.getuser()

APP_PATHS = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "explorer": "explorer.exe",
    "steam": r"C:\Program Files (x86)\Steam\steam.exe",
}

APP_PROCESS_NAMES = {
    "notepad": "notepad.exe",
    "calculator": "CalculatorApp.exe",
    "chrome": "chrome.exe",
    "explorer": "explorer.exe",
    "steam": "steam.exe",
}

COMMON_SEARCH_DIRS = [
    r"C:\Program Files",
    r"C:\Program Files (x86)",
    fr"C:\Users\{USERNAME}\AppData\Local",
    fr"C:\Users\{USERNAME}\AppData\Roaming",
    fr"C:\Users\{USERNAME}\AppData\Local\Programs",
    fr"C:\Users\{USERNAME}\Desktop",
    fr"C:\Users\{USERNAME}\Downloads",
    fr"C:\Users\{USERNAME}\Documents",
]

START_MENU_DIRS = [
    r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
    fr"C:\Users\{USERNAME}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs",
]

def open_app(name_or_path: str) -> str:
    # If it's a full/absolute path, launch it directly
    if os.path.isabs(name_or_path) or ":\\" in name_or_path:
        if os.path.exists(name_or_path):
            os.startfile(name_or_path)
            return f"Opening {name_or_path}."
        return f"Path not found: {name_or_path}"

    name = name_or_path.lower()
    if name in APP_PATHS:
        subprocess.Popen(APP_PATHS[name])
        return f"Opening {name}."
    return f"I don't know where {name} is installed by name. Use find_installed_app first to get its full path, then call open_app again with that exact path."

def close_app(name: str) -> str:
    name = name.lower()
    proc_name = APP_PROCESS_NAMES.get(name, f"{name}.exe")
    closed = False
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and proc.info['name'].lower() == proc_name.lower():
                proc.terminate()
                closed = True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return f"Closed {name}." if closed else f"{name} doesn't seem to be running."

def find_installed_app(keyword: str) -> str:
    """Fast: checks Start Menu shortcuts first. Best way to find installed apps."""
    keyword = keyword.lower()
    matches = []
    for base in START_MENU_DIRS:
        if not os.path.exists(base):
            continue
        for dirpath, _, filenames in os.walk(base):
            for f in filenames:
                if keyword in f.lower() and f.lower().endswith(".lnk"):
                    matches.append(os.path.join(dirpath, f))
    if matches:
        return "\n".join(matches[:5])
    return "NOT_FOUND_IN_START_MENU"

def quick_search_files(keyword: str) -> str:
    """Fast: checks common install/user folders only, 2 levels deep. Try this before deep search."""
    keyword = keyword.lower()
    matches = []
    for base in COMMON_SEARCH_DIRS:
        if not os.path.exists(base):
            continue
        try:
            for entry in os.scandir(base):
                if keyword in entry.name.lower():
                    matches.append(entry.path)
                if entry.is_dir():
                    try:
                        for sub in os.scandir(entry.path):
                            if keyword in sub.name.lower():
                                matches.append(sub.path)
                    except (PermissionError, OSError):
                        continue
        except (PermissionError, OSError):
            continue
        if len(matches) >= 10:
            break
    return "\n".join(matches[:10]) if matches else "NOT_FOUND_IN_COMMON_DIRS"

def get_available_drives():
    return [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]

def search_files(keyword: str, root: str = None) -> str:
    """SLOW: full scan of every drive. Only use as a last resort."""
    roots = [root] if root else get_available_drives()
    matches = []
    for r in roots:
        for dirpath, _, filenames in os.walk(r):
            for f in filenames:
                if keyword.lower() in f.lower():
                    matches.append(os.path.join(dirpath, f))
                    if len(matches) >= 10:
                        return "\n".join(matches)
    return "\n".join(matches) if matches else "No files found."

def open_file(path: str) -> str:
    if os.path.exists(path):
        os.startfile(path)
        return f"Opening {path}."
    return "File not found."

def open_folder(path: str) -> str:
    if os.path.isdir(path):
        os.startfile(path)
        return f"Opening folder {path}."
    return "Folder not found."

def delete_file(path: str) -> str:
    if os.path.exists(path):
        send2trash(path)
        return f"Moved {path} to the recycle bin."
    return "File not found."

def copy_file(src: str, dest: str) -> str:
    if not os.path.exists(src):
        return "Source file not found."
    try:
        shutil.copy2(src, dest)
        return f"Copied to {dest}."
    except Exception as e:
        return f"Couldn't copy file: {e}"

def move_file(src: str, dest: str) -> str:
    if not os.path.exists(src):
        return "Source file not found."
    try:
        shutil.move(src, dest)
        return f"Moved to {dest}."
    except Exception as e:
        return f"Couldn't move file: {e}"