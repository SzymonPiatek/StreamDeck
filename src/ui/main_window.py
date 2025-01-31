import json
import os
import threading

import keyboard
from PyQt6.QtCore import QRect
from PyQt6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QComboBox,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QLabel,
    QSizePolicy,
)

os.environ["QT_FONT_DPI"] = "96"


class Window(QWidget):
    def __init__(self, system, settings, application):
        super().__init__()

        self.system = system
        self.settings = settings
        self.application = application
        self.config_file = "src/data/config.json"

        self.setWindowTitle(f"{settings['APP_NAME']} {self.system.name}")
        self.setGeometry(*settings["APP_GEOMETRY"])
        self.setStyleSheet(open("src/ui/themes/py_dracula_dark.qss", "r").read())

        self.recognized_devices = []
        self.current_device = None
        self.macros = []
        self.listener_thread = None

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.navbar = QHBoxLayout()
        self.navbar.setContentsMargins(10, 10, 10, 10)
        self.navbar.setSpacing(10)
        self.navbar.setGeometry(QRect(0, 0, 800, 120))

        self.navbar_widget = QWidget()
        self.navbar_widget.setLayout(self.navbar)

        self.device_select = QComboBox()
        self.device_select.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.device_select.currentIndexChanged.connect(self.on_select_device)

        self.refresh_device_select_button = QPushButton("Odśwież")
        self.refresh_device_select_button.clicked.connect(self.refresh_device_list)
        self.refresh_device_select_button.setSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred
        )
        self.refresh_device_select_button.setMinimumHeight(30)

        self.navbar.addWidget(self.device_select)
        self.navbar.addWidget(self.refresh_device_select_button)
        self.main_layout.addWidget(self.navbar_widget)

        self.main_layout.addSpacing(5)

        self.content_widget = QWidget(self)
        self.content_widget.setStyleSheet("background-color: #222;")
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        self.content_widget.setLayout(self.content_layout)

        self.macro_list = QListWidget()
        self.content_layout.addWidget(self.macro_list)
        self.main_layout.addWidget(self.content_widget, 1)

        self.ensure_config_file_exists()
        self.load_config()
        self.refresh_device_list()
        self.start_keyboard_listener()

    def on_key_press(self, event):
        key_name = event.name
        print(f"DEBUG: Wykryto naciśnięcie klawisza: {key_name}")

        for macro in self.macros:
            if macro["key"] == key_name:
                self.execute_macro(macro["function"])

    def execute_macro(self, function):
        if function == "Volume -":
            self.system.volume_down()
        elif function == "Volume +":
            self.system.volume_up()
        elif function == "Mute/unmute":
            self.system.mute_unmute()

    def start_keyboard_listener(self):
        self.listener_thread = threading.Thread(target=self.listen_for_keys, daemon=True)
        self.listener_thread.start()

    def listen_for_keys(self):
        try:
            keyboard.on_press(self.on_key_press)
            keyboard.wait()
        except Exception as e:
            print(f"DEBUG: Błąd podczas nasłuchiwania klawiszy: {e}")

    def ensure_config_file_exists(self):
        if not os.path.exists(self.config_file) or os.stat(self.config_file).st_size == 0:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump([], f, indent=4, ensure_ascii=False)

    def refresh_device_list(self):
        self.recognized_devices = self.application.recognize_devices()
        self.device_select.clear()
        self.device_select.addItems(self.recognized_devices)

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = []

        existing_devices = {d["device"] for d in data}

        for device in self.recognized_devices:
            if device not in existing_devices:
                data.append({"device": device, "macros": []})

        self.save_json(data)

    def on_select_device(self):
        selected_device = self.device_select.currentText()
        self.current_device = selected_device
        self.macros = self.load_macros_for_device(selected_device)
        self.populate_macro_list()

    def populate_macro_list(self):
        self.macro_list.clear()

        for macro in self.macros:
            item = QListWidgetItem(self.macro_list)
            item_widget = QWidget()

            layout = QHBoxLayout()
            layout.setContentsMargins(5, 5, 5, 5)

            key_label = QLabel(macro["key"])

            function_select = QComboBox()
            for function in self.settings["MACRO_FUNCTIONS"]:
                function_select.addItem(function)

            function_select.setCurrentText(macro.get("function", "Wybierz funkcję"))
            function_select.currentIndexChanged.connect(
                lambda _, k=macro["key"], f=function_select: self.save_macro(k, f.currentText())
            )

            layout.addWidget(key_label)
            layout.addWidget(function_select)
            item_widget.setLayout(layout)

            item.setSizeHint(item_widget.sizeHint())
            self.macro_list.addItem(item)
            self.macro_list.setItemWidget(item, item_widget)

    def save_macro(self, key, function):
        if not self.current_device:
            return

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = []

        for entry in data:
            if entry["device"] == self.current_device:
                for macro in entry["macros"]:
                    if macro["key"] == key:
                        macro["function"] = function
                        break
                else:
                    entry["macros"].append({"key": key, "function": function})
                break

        self.save_json(data)

    def load_macros_for_device(self, device):
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                return []
            for entry in data:
                if entry["device"] == device:
                    return entry.get("macros", [])
        except (FileNotFoundError, json.JSONDecodeError):
            return []
        return []

    def save_json(self, data):
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def load_config(self):
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                return []
        except (FileNotFoundError, json.JSONDecodeError):
            return []

        return data
