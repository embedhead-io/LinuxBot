from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt


class StatusLabel(QLabel):
    """A QLabel subclass for displaying status messages in the application."""

    DEFAULT_TEXT = "Status: Ready"
    ALIGNMENT = Qt.AlignCenter

    def __init__(self):
        """Initialize the StatusLabel with default settings."""
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Set up the initial UI properties of the label."""
        self.setText(self.DEFAULT_TEXT)
        self.setAlignment(self.ALIGNMENT)
