import os

from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QListWidget

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

        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)

        self.render_sidebar()

        self.device_list = QListWidget()
        self.device_list.itemClicked.connect(self.on_device_click)
        self.main_layout.addWidget(self.device_list, 1)

    def render_sidebar(self):
        sidebar = QVBoxLayout()
        sidebar.setContentsMargins(0, 0, 0, 0)
        sidebar.setSpacing(20)

        sidebar_widget = QWidget()
        sidebar_widget.setLayout(sidebar)
        sidebar_widget.setFixedWidth(150)

        devices_button = QPushButton("Urządzenia")
        devices_button.clicked.connect(self.show_devices)

        info_button = QPushButton("Informacje")

        sidebar.addWidget(devices_button)
        sidebar.addWidget(info_button)
        sidebar.addStretch()

        self.main_layout.addWidget(sidebar_widget)

    def show_devices(self):
        self.device_list.clear()

        if hasattr(self.system, "recognize_devices"):
            print("Wykrywanie urządzeń...")
            devices = self.system.recognize_devices()

            for category, device_list in devices.items():
                if device_list:
                    for device in device_list:
                        self.device_list.addItem(device)
        else:
            self.device_list.addItem("Funkcja nie jest dostępna dla tego systemu.")

    def on_device_click(self, item):
        print(f"Kliknięto na: {item.text()}")
