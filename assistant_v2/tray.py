import pystray
from PIL import Image


class JarvisTray:

    def __init__(self, on_exit):

        self.on_exit = on_exit
        self.icon = None


    def start(self):

        image = Image.new(
            "RGB",
            (64, 64),
            (0, 0, 0)
        )

        menu = pystray.Menu(
            pystray.MenuItem(
                "Exit Jarvis",
                self.exit
            )
        )

        self.icon = pystray.Icon(
            "Jarvis",
            image,
            "Jarvis AI",
            menu
        )

        self.icon.run()


    def exit(self):

        if self.icon:
            self.icon.stop()

        self.on_exit()