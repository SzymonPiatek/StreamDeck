import platform
import sys
import threading

from PyQt6.QtWidgets import QApplication

from src.file.file import JSONFile
from src.system.macOS.macOS import MacOS
from src.system.windows.windows import Windows
from src.ui.main_window import Window


class Application:
    def __init__(self, settings):
        self.settings = settings
        self.system = self.recognize_system()

        # Devices
        self.recognized_devices = []
        self.current_device = None
        self.macros = []
        self.listener_thread = None

        # Files
        self.device_config = JSONFile(path="src/data/device_config.json")

    def run(self):
        if not self.system:
            print("Brak obsługi dla tego systemu")
            exit()

        # Window
        app = QApplication(sys.argv)
        window = Window(application=self)
        window.show()

        # Config
        self.device_config.ensure_file_exists()
        self.load_device_config()

        sys.exit(app.exec())

    def load_device_config(self):
        data = self.device_config.load_file()

        return [] if not isinstance(data, list) else data

    def load_macros_for_device(self, device):
        data = self.load_device_config()

        for entry in data:
            if entry["device"] == device:
                return entry.get("macros", [])
        return []

    def save_macro(self, key, function):
        if not self.current_device:
            return

        data = self.load_device_config()

        for entry in data:
            if entry["device"] == self.current_device:
                for macro in entry["macros"]:
                    if macro["key"] == key:
                        macro["function"] = function
                        break
                else:
                    entry["macros"].append({"key": key, "function": function})
                break

        self.device_config.save_file(data=data)

    def execute_macro(self, function_name):
        for func in self.system.functions:
            if func["name"] == function_name:
                func["function"]()
                return

        print(f"DEBUG: Nie znaleziono funkcji '{function_name}'")

    def on_key_press(self, event):
        key_name = event.name
        active_device = self.system.get_active_input_device()

        if not active_device:
            return

        if active_device != self.current_device:
            return

        for macro in self.macros:
            if macro["key"] == key_name:
                self.execute_macro(macro["function"])

    def start_keyboard_listener(self):
        self.listener_thread = threading.Thread(target=self.system.device_listener, daemon=True)
        self.listener_thread.start()

    def recognize_system(self):
        system_name = platform.system()

        if system_name == "Windows":
            return Windows()
        elif system_name == "Darwin":
            return MacOS(application=self)
        else:
            return None
