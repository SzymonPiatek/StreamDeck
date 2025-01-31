import platform
from src.system.macOS.macOS import MacOS
from src.system.windows.windows import Windows


class Application:
    def __init__(self, name):
        self.name = name
        self.system = self.recognize_system()

    def recognize_system(self):
        system_name = platform.system()

        if system_name == "Windows":
            return Windows
        elif system_name == "Darwin":
            return MacOS
        else:
            return None
