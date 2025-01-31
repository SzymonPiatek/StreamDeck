from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QHBoxLayout, QWidget


class Window(QWidget):
    def __init__(self, system, settings):
        super().__init__()

        self.system = system
        self.settings = settings

        self.setWindowTitle(f"{settings["APP_NAME"]} {self.system.name}")
        self.setGeometry(*settings["APP_GEOMETRY"])
        self.setStyleSheet(open("src/ui/themes/py_dracula_dark.qss", "r").read())

        # Layout
        main_layout = QHBoxLayout()

        sidebar = QVBoxLayout()

        self.devices_button = QPushButton("Urządzenia")
        sidebar.addWidget(self.devices_button)

        self.info_button = QPushButton("Informacje")
        sidebar.addWidget(self.info_button)

        sidebar.addStretch()

        sidebar_widget = QWidget()
        sidebar_widget.setLayout(sidebar)
        sidebar_widget.setFixedWidth(200)

        content = QWidget()
        content.setStyleSheet("background-color: #1E1E1E; border-radius: 10px;")

        # 🔹 Układ główny
        main_layout.addWidget(sidebar_widget)
        main_layout.addWidget(content, 1)

        self.setLayout(main_layout)

    def perform_action(self):
        self.system.event_listener()
