import platform
from src.system.macOS.macOS import MacOS
from src.system.windows.windows import Windows


class Application:
    def __init__(self, name):
        self.name = name
        self.system = self.recognize_system()

    def run(self):
        if not self.system:
            print("Nieobsługiwany system operacyjny!")
            return

        running = True
        while running:
            self.system.event_listener()

    def recognize_system(self):
        system_name = platform.system()

        if system_name == "Windows":
            return Windows()
        elif system_name == "Darwin":
            return MacOS()
        else:
            return None
