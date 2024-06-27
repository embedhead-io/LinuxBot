from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt


class StatusLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setText("Status: Ready")
        self.setAlignment(Qt.AlignCenter)
