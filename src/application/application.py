import platform
import sys

from PyQt6.QtWidgets import QApplication

from src.system.macOS.macOS import MacOS
from src.system.windows.windows import Windows
from src.ui.main_window import MainWindow


class Application:
    def __init__(self, name):
        self.name = name
        self.system = self.recognize_system()

    def run(self):
        app = QApplication(sys.argv)
        window = MainWindow(self.system)
        window.show()
        sys.exit(app.exec())

    def recognize_system(self):
        system_name = platform.system()

        if system_name == "Windows":
            return Windows()
        elif system_name == "Darwin":
            return MacOS()
        else:
            return None
