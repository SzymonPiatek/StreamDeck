import os

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
    def __init__(self, application):
        super().__init__()

        self.application = application

        self.setWindowTitle(f"{self.application.settings['APP_NAME']} {self.application.system.name}")
        self.setGeometry(*self.application.settings["APP_GEOMETRY"])
        self.setStyleSheet(open("src/ui/themes/py_dracula_dark.qss", "r").read())

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        # Navbar
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
        self.refresh_device_select_button.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        self.refresh_device_select_button.setMinimumHeight(30)

        self.navbar.addWidget(self.device_select)
        self.navbar.addWidget(self.refresh_device_select_button)
        self.main_layout.addWidget(self.navbar_widget)

        self.main_layout.addSpacing(5)

        # Macro list
        self.content_widget = QWidget(self)
        self.content_widget.setStyleSheet("background-color: #222;")
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        self.content_widget.setLayout(self.content_layout)

        self.macro_list = QListWidget()
        self.content_layout.addWidget(self.macro_list)
        self.main_layout.addWidget(self.content_widget, 1)

        self.refresh_device_list()
        self.application.start_keyboard_listener()

    def refresh_device_list(self):
        self.application.recognized_devices = self.application.system.recognize_devices()
        self.device_select.clear()
        self.device_select.addItems(self.application.recognized_devices)

        data = self.application.load_device_config()

        existing_devices = {d["device"] for d in data}

        for device in self.application.recognized_devices:
            if device not in existing_devices:
                data.append({"device": device, "macros": []})

        self.application.device_config.save_file(data)

    def on_select_device(self):
        selected_device = self.device_select.currentText()
        self.application.current_device = selected_device
        self.application.macros = self.application.load_macros_for_device(selected_device)
        self.populate_macro_list()

    def populate_macro_list(self):
        self.macro_list.clear()

        for macro in self.application.macros:
            item = QListWidgetItem(self.macro_list)
            item_widget = QWidget()

            layout = QHBoxLayout()
            layout.setContentsMargins(5, 5, 5, 5)

            key_label = QLabel(macro["key"])

            function_select = QComboBox()
            for function in self.application.system.functions:
                function_select.addItem(function["name"])

            function_select.setCurrentText(macro.get("function", "Wybierz funkcję"))

            function_select.currentIndexChanged.connect(
                lambda _, k=macro["key"], f=function_select: self.on_macro_change(k, f.currentText())
            )

            layout.addWidget(key_label)
            layout.addWidget(function_select)
            item_widget.setLayout(layout)

            item.setSizeHint(item_widget.sizeHint())
            self.macro_list.addItem(item)
            self.macro_list.setItemWidget(item, item_widget)

    def on_macro_change(self, key, function):
        self.application.save_macro(key, function)
        self.application.macros = self.application.load_macros_for_device(self.application.current_device)
