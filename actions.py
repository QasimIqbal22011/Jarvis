import os
import shutil
import string
import subprocess
import getpass

import psutil
from send2trash import send2trash

USERNAME = getpass.getuser()

# -------------------------------------------------
# Known Windows applications
# -------------------------------------------------

APP_PATHS = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "calc": "calc.exe",

    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "google chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "googlechrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "browser": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "internet": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "explorer": "explorer.exe",
    "file explorer": "explorer.exe",
    "steam": r"C:\Program Files (x86)\Steam\steam.exe",

    # Windows URI apps
    "settings": "ms-settings:",
    "windows settings": "ms-settings:",
    "control panel": "control.exe",
    "task manager": "taskmgr.exe",
    "paint": "mspaint.exe",
    "cmd": "cmd.exe",
    "command prompt": "cmd.exe",
    "powershell": "powershell.exe",
}

APP_PROCESS_NAMES = {
    "notepad": "notepad.exe",
    "calculator": "CalculatorApp.exe",
    "calc": "CalculatorApp.exe",
    "chrome": "chrome.exe",
    "google chrome": "chrome.exe",
    "explorer": "explorer.exe",
    "file explorer": "explorer.exe",
    "steam": "steam.exe",
    "paint": "mspaint.exe",
    "cmd": "cmd.exe",
    "command prompt": "cmd.exe",
    "powershell": "powershell.exe",
    "googlechrome": "chrome.exe",
    "browser": "chrome.exe",
    "internet": "chrome.exe",
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


# -------------------------------------------------
# Helpers
# -------------------------------------------------

def is_running(process_name: str) -> bool:

    for proc in psutil.process_iter(["name"]):
        try:
            if (
                proc.info["name"]
                and proc.info["name"].lower()
                == process_name.lower()
            ):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    return False


def open_app(name_or_path: str) -> str:

    target = name_or_path.strip()

    # absolute path

    if os.path.isabs(target) or ":\\" in target:

        if not os.path.exists(target):
            return f"Path not found: {target}"

        os.startfile(target)

        return f"Opening {os.path.basename(target)}."

    name = target.lower()

    executable = APP_PATHS.get(name)

    process_name = APP_PROCESS_NAMES.get(name)

    if executable is None:
        return (
            f"Unknown application: {name}. "
            f"Use find_installed_app."
        )

    # URI apps

    if executable.startswith("ms-"):
        os.startfile(executable)
        return f"Opening {name}."

    if process_name and is_running(process_name):
        return f"{name.capitalize()} is already running."

    try:
        subprocess.Popen(executable)
        return f"Opening {name}."
    except FileNotFoundError:
        return (
            f"{name} is known but isn't installed "
            f"at the expected location."
        )

def close_app(name: str) -> str:

    name = name.strip().lower()

    process_name = APP_PROCESS_NAMES.get(name)

    if process_name is None:
        return f"Unknown application: {name}"


    closed = False


    for proc in psutil.process_iter(["name"]):

        try:

            if (
                proc.info["name"]
                and proc.info["name"].lower()
                == process_name.lower()
            ):

                proc.terminate()
                closed = True


        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied
        ):

            pass


    if closed:

        return f"Closed {name}."

    else:

        return f"{name} is not running."

def find_installed_app(keyword: str) -> str:

    keyword = keyword.lower().strip()

    matches = []

    for base in START_MENU_DIRS:

        if not os.path.exists(base):
            continue

        for dirpath, _, filenames in os.walk(base):

            for filename in filenames:

                name = filename.lower()

                if (
                    keyword in name
                    and (
                        name.endswith(".lnk")
                        or name.endswith(".exe")
                    )
                ):
                    matches.append(
                        os.path.join(
                            dirpath,
                            filename,
                        )
                    )

    return (
        "\n".join(matches[:10])
        if matches
        else "NOT_FOUND_IN_START_MENU"
    )


def quick_search_files(keyword: str):

    keyword = keyword.lower().strip()

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
                        pass

        except (PermissionError, OSError):
            pass

        if len(matches) >= 20:
            break

    return (
        "\n".join(matches[:20])
        if matches
        else "NOT_FOUND_IN_COMMON_DIRS"
    )


def get_available_drives():

    return [
        f"{d}:\\"
        for d in string.ascii_uppercase
        if os.path.exists(f"{d}:\\")
    ]


def search_files(keyword: str, root=None):

    keyword = keyword.lower().strip()

    roots = [root] if root else get_available_drives()

    matches = []

    for drive in roots:

        for dirpath, _, filenames in os.walk(drive):

            for filename in filenames:

                if keyword in filename.lower():

                    matches.append(
                        os.path.join(
                            dirpath,
                            filename,
                        )
                    )

                    if len(matches) >= 20:
                        return "\n".join(matches)

    return (
        "\n".join(matches)
        if matches
        else "NOT_FOUND"
    )


def open_file(path):

    path = path.strip()

    if not os.path.exists(path):
        return "File not found."

    os.startfile(path)

    return f"Opening {os.path.basename(path)}."


def open_folder(path):

    path = path.strip()

    if not os.path.isdir(path):
        return "Folder not found."

    os.startfile(path)

    return f"Opening folder {path}."


def delete_file(path):

    path = path.strip()

    if not os.path.exists(path):
        return "File not found."

    send2trash(path)

    return f"Moved {path} to the recycle bin."


def copy_file(src, dest):

    src = src.strip()
    dest = dest.strip()

    if not os.path.exists(src):
        return "Source file not found."

    try:

        shutil.copy2(src, dest)

        return f"Copied to {dest}."

    except Exception as e:

        return str(e)


def move_file(src, dest):

    src = src.strip()
    dest = dest.strip()

    if not os.path.exists(src):
        return "Source file not found."

    try:

        shutil.move(src, dest)

        return f"Moved to {dest}."

    except Exception as e:

        return str(e)