import winreg as reg
import sys
import os

APP_NAME = "Jarvis Assistant"
PYTHONW = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
SCRIPT = os.path.abspath("tray_app.py")

def add_to_startup():
    key = reg.OpenKey(reg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, reg.KEY_SET_VALUE)
    reg.SetValueEx(key, APP_NAME, 0, reg.REG_SZ, f'"{PYTHONW}" "{SCRIPT}"')
    reg.CloseKey(key)
    print("Added to startup. Check Task Manager > Startup Apps to confirm.")

def remove_from_startup():
    try:
        key = reg.OpenKey(reg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, reg.KEY_SET_VALUE)
        reg.DeleteValue(key, APP_NAME)
        reg.CloseKey(key)
        print("Removed from startup.")
    except FileNotFoundError:
        print("Not currently registered for startup.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "remove":
        remove_from_startup()
    else:
        add_to_startup()