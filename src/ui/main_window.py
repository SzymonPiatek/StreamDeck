import os
from functools import partial

from PyQt6.QtCore import QRect, QSize
from PyQt6.QtGui import QFontMetrics, QIcon
from PyQt6.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QComboBox,
    QSizePolicy,
    QPushButton,
    QHBoxLayout,
    QLabel,
    QGridLayout,
)

os.environ["QT_FONT_DPI"] = "96"


class Window(QWidget):
    def __init__(self, application):
        super().__init__()

        self.application = application
        self.style_file = "src/ui/themes/py_dracula_dark.qss"

        self.setWindowTitle(f"{self.application.settings['APP_NAME']} {self.application.system.name}")
        self.setGeometry(*self.application.settings["APP_GEOMETRY"])
        self.reload_stylesheet()

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
        self.navbar_widget.setObjectName("navbar")
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

        self.navbar.addWidget(self.device_select, stretch=1)
        self.navbar.addWidget(refresh_device_select_button, stretch=0)
        self.navbar.addWidget(add_new_macro_button, stretch=0)

        self.main_layout.addWidget(self.navbar_widget)

        # Content
        self.content_widget = QWidget(self)
        self.content_widget.setObjectName("content_widget")

        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_widget.setLayout(self.content_layout)

        self.main_layout.addWidget(self.content_widget, 1)

        # Macro list
        self.macro_grid = QGridLayout()
        self.macro_grid.setContentsMargins(0, 0, 0, 0)
        self.macro_grid.setSpacing(8)

        self.content_layout.addLayout(self.macro_grid)

        self.refresh_device_list()
        self.application.start_keyboard_listener()

    def reload_stylesheet(self):
        self.setStyleSheet(open(self.style_file, "r").read())

    def button_with_icon(self, text, icon, on_click):
        button = QPushButton()
        button.setMinimumHeight(30)

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(10, 5, 10, 5)
        button_layout.setSpacing(8)

        icon_label = QLabel()
        icon = QIcon(icon)
        icon_label.setPixmap(icon.pixmap(QSize(18, 18)))

        text_label = QLabel(text)

        button_layout.addWidget(icon_label)
        button_layout.addWidget(text_label)
        button_layout.addStretch()

        button.setLayout(button_layout)
        button.clicked.connect(on_click)

        font_metrics = QFontMetrics(button.font())
        text_width = font_metrics.horizontalAdvance(text)
        total_width = text_width + 50

        button.setMinimumWidth(total_width)

        return button

    def add_macro_section(self):
        if not self.application.current_device:
            return

        new_macro = {"key": "", "function": ""}
        self.application.macros.append(new_macro)

        self.application.save_macro("", "")

        self.populate_macro_list()

    def refresh_device_list(self):
        self.reload_stylesheet()

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
        while self.macro_grid.count():
            item = self.macro_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        num_columns = 2
        row, col = 0, 0

        for macro in self.application.macros:
            item_widget = QWidget()
            layout = QHBoxLayout()

            key_button = QPushButton(macro["key"] if macro["key"] else "Ustaw klawisz")
            key_button.setFixedHeight(30)
            key_button.clicked.connect(partial(self.application.system.listen_for_key, macro, key_button))

            function_select = QComboBox()
            function_select.addItem("Wybierz funkcję")
            for function in self.application.system.functions:
                function_select.addItem(function["name"])

            function_select.setCurrentText(macro.get("function", "Wybierz funkcję"))
            function_select.setFixedHeight(30)
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

            self.macro_grid.addWidget(item_widget, row, col)

            col += 1
            if col >= num_columns:
                col = 0
                row += 1

        self.content_layout.addStretch(1)

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
