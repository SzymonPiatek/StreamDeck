import os

from PyQt6.QtCore import QRect
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QComboBox

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
        self.navbar.setContentsMargins(0, 10, 0, 0)
        self.navbar.setSpacing(10)
        self.navbar.setGeometry(QRect(0, 0, 800, 120))

        self.navbar_widget = QWidget()
        self.navbar_widget.setLayout(self.navbar)

        self.device_select = QComboBox()
        self.device_select.addItems(self.application.recognize_devices())
        self.device_select.currentIndexChanged.connect(self.on_select_device)

        self.navbar.addWidget(self.device_select)
        self.main_layout.addWidget(self.navbar_widget)

        self.main_layout.addSpacing(5)

        # Main
        self.content_widget = QWidget(self)
        self.content_widget.setStyleSheet("background-color: #222;")
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        self.content_widget.setLayout(self.content_layout)

        self.main_layout.addWidget(self.content_widget, 1)

    def on_select_device(self):
        selected_text = self.device_select.currentText()
        print(selected_text)
