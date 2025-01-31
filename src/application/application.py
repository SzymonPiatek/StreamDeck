import platform
import sys

from PyQt6.QtWidgets import QApplication

from src.system.macOS.macOS import MacOS
from src.system.windows.windows import Windows
from src.ui.main_window import Window


class Application:
    def __init__(self, settings):
        self.settings = settings
        self.system = self.recognize_system()

    def run(self):
        if self.system:
            app = QApplication(sys.argv)
            window = Window(system=self.system, settings=self.settings)
            window.show()
            sys.exit(app.exec())
        else:
            print("Brak obsługi dla tego systemu")
            exit()

    def recognize_system(self):
        system_name = platform.system()

        if system_name == "Windows":
            return Windows()
        elif system_name == "Darwin":
            return MacOS()
        else:
            return None
