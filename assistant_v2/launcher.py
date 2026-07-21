import threading
import gui

from assistant_v2.voice import run
from assistant_v2.tray import JarvisTray


running = True


def start_voice():

    run()


def shutdown():

    global running

    running = False

    gui.destroy_window()


def start_tray():

    tray = JarvisTray(
        shutdown
    )

    tray.start()


def main():

    threading.Thread(
        target=start_voice,
        daemon=True
    ).start()


    threading.Thread(
        target=start_tray,
        daemon=True
    ).start()


    gui.create_gui()


if __name__ == "__main__":
    main()