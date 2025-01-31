from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout
from PyQt6.QtCore import Qt


class MainWindow(QWidget):
    def __init__(self, system):
        super().__init__()
        self.system = system

        self.setWindowTitle("Stream Deck - PyDracula")
        self.setGeometry(100, 100, 400, 300)
        self.setStyleSheet(open("src/ui/pydracula_style.qss", "r").read())

        layout = QVBoxLayout()

        self.label = QLabel(f"System wykryty: {self.system.name if self.system else 'Nieznany'}")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        self.button = QPushButton("Wykonaj akcję")
        self.button.clicked.connect(self.perform_action)
        layout.addWidget(self.button)

        self.quit_button = QPushButton("Zamknij")
        self.quit_button.clicked.connect(self.close)
        layout.addWidget(self.quit_button)

        self.setLayout(layout)

    def perform_action(self):
        if self.system:
            self.system.event_listener()
        else:
            print("Brak obsługi dla tego systemu.")
