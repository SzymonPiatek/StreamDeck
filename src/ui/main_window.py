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
    def __init__(self, system, settings, application):
        super().__init__()

        self.system = system
        self.settings = settings
        self.application = application

        self.setWindowTitle(f"{settings["APP_NAME"]} {self.system.name}")
        self.setGeometry(*settings["APP_GEOMETRY"])
        self.setStyleSheet(open("src/ui/themes/py_dracula_dark.qss", "r").read())

        self.recognized_devices = []
        self.current_device = None

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
        self.device_select.addItems(self.recognized_devices)
        self.device_select.currentIndexChanged.connect(self.on_select_device)
        self.device_select.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

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

        # Main
        self.content_widget = QWidget(self)
        self.content_widget.setStyleSheet("background-color: #222;")
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        self.content_widget.setLayout(self.content_layout)

        self.macro_list = QListWidget()

        self.content_layout.addWidget(self.macro_list)
        self.macros = ["F1", "F2"]
        self.populate_macro_list()

        self.main_layout.addWidget(self.content_widget, 1)

    def populate_macro_list(self):
        for macro in self.macros:
            item = QListWidgetItem(self.macro_list)
            item_widget = QWidget()

            layout = QHBoxLayout()
            layout.setContentsMargins(5, 5, 5, 5)

            key_label = QLabel(macro)

            function_select = QComboBox()
            function_select.addItem("Wybierz funkcję")

            layout.addWidget(key_label)
            layout.addWidget(function_select)
            item_widget.setLayout(layout)

            item.setSizeHint(item_widget.sizeHint())
            self.macro_list.addItem(item)
            self.macro_list.setItemWidget(item, item_widget)

    def refresh_device_list(self):
        self.recognized_devices = self.application.recognize_devices()
        self.device_select.clear()
        self.device_select.addItems(self.recognized_devices)

    def on_select_device(self):
        selected_text = self.device_select.currentText()
        print(selected_text)
