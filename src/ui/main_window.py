import os

from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QHBoxLayout, QWidget

os.environ["QT_FONT_DPI"] = "96"


class Window(QWidget):
    def __init__(self, system, settings):
        super().__init__()

        self.system = system
        self.settings = settings

        self.setWindowTitle(f"{settings["APP_NAME"]} {self.system.name}")
        self.setGeometry(*settings["APP_GEOMETRY"])
        self.setStyleSheet(open("src/ui/themes/py_dracula_dark.qss", "r").read())

        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)

        self.render_sidebar()

    def render_sidebar(self):
        sidebar = QVBoxLayout()
        sidebar.setContentsMargins(0, 0, 0, 0)
        sidebar.setSpacing(20)

        sidebar_widget = QWidget()
        sidebar_widget.setLayout(sidebar)
        sidebar_widget.setFixedWidth(150)

        devices_button = QPushButton("Urządzenia")
        info_button = QPushButton("Informacje")

        sidebar.addWidget(devices_button)
        sidebar.addWidget(info_button)
        sidebar.addStretch()

        content = QWidget()
        content.setStyleSheet("background-color: #1E1E1E; border-radius: 10px;")

        self.main_layout.addWidget(sidebar_widget)
        self.main_layout.addWidget(content, 1)

    def perform_action(self):
        self.system.event_listener()
