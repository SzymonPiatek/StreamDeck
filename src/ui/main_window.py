import os
from functools import partial

from PyQt6.QtCore import QRect
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QComboBox,
    QPushButton,
    QListWidget,
    QListWidgetItem,
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

        add_new_macro_button = self.button_with_icon(
            text="Dodaj makro", icon="src/ui/icons/plus-solid.svg", on_click=self.add_macro_section
        )

        refresh_device_select_button = self.button_with_icon(
            text="Odśwież", icon="src/ui/icons/rotate-solid.svg", on_click=self.refresh_device_list
        )

        self.navbar.addWidget(self.device_select)
        self.navbar.addWidget(refresh_device_select_button)
        self.navbar.addWidget(add_new_macro_button)
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

    def button_with_icon(self, text, icon, on_click):
        component = QPushButton(text)
        component.setIcon(QIcon(icon))
        component.clicked.connect(on_click)
        component.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        component.setMinimumHeight(30)

        return component

    def add_macro_section(self):
        if not self.application.current_device:
            return

        new_macro = {"key": "", "function": ""}
        self.application.macros.append(new_macro)

        self.application.save_macro("", "")

        self.populate_macro_list()

    def refresh_device_list(self):
        self.application.recognized_devices = self.application.system.recognize_devices()
        self.device_select.clear()
        self.device_select.addItems([device.name for device in self.application.recognized_devices])

        data = self.application.load_device_config()

        serializable_data = []

        for device in self.application.recognized_devices:
            device_dict = {
                "device": device.name,
                "device_id": device.id,
                "device_type": device.type,
                "macros": next((entry["macros"] for entry in data if entry["device"] == device.name), []),
            }

            serializable_data.append(device_dict)

        self.application.device_config.save_file(serializable_data)

    def on_select_device(self):
        selected_device = self.device_select.currentText()
        self.application.current_device = selected_device
        self.application.macros = self.application.load_macros_for_device(selected_device) or []
        self.populate_macro_list()

    def populate_macro_list(self):
        self.macro_list.clear()

        for macro in self.application.macros:
            item = QListWidgetItem(self.macro_list)
            item_widget = QWidget()

            layout = QHBoxLayout()
            layout.setContentsMargins(5, 5, 5, 5)

            key_button = QPushButton(macro["key"] if macro["key"] else "Ustaw klawisz")
            key_button.clicked.connect(partial(self.application.system.listen_for_key, macro, key_button))

            function_select = QComboBox()
            function_select.addItem("Wybierz funkcję")
            for function in self.application.system.functions:
                function_select.addItem(function["name"])

            function_select.setCurrentText(macro.get("function", "Wybierz funkcję"))

            function_select.currentIndexChanged.connect(
                lambda _, k=macro["key"], f=function_select: self.on_macro_change(k, f.currentText())
            )

            delete_button = QPushButton()
            delete_button.setIcon(QIcon("src/ui/icons/trash-solid.svg"))
            delete_button.setFixedSize(30, 30)
            delete_button.clicked.connect(partial(self.delete_macro, macro))

            layout.addWidget(key_button)
            layout.addWidget(function_select)
            layout.addWidget(delete_button)

            item_widget.setLayout(layout)

            item.setSizeHint(item_widget.sizeHint())
            self.macro_list.addItem(item)
            self.macro_list.setItemWidget(item, item_widget)

    def on_macro_change(self, key, function_name):
        self.application.save_macro(key, function_name)
        self.application.macros = self.application.load_macros_for_device(self.application.current_device)

    def delete_macro(self, macro):
        if not self.application.current_device:
            return

        data = self.application.load_device_config()

        for entry in data:
            if entry["device"] == self.application.current_device:
                if macro in entry["macros"]:
                    entry["macros"].remove(macro)
                    break

        self.application.device_config.save_file(data)

        if macro in self.application.macros:
            self.application.macros.remove(macro)

        self.populate_macro_list()
