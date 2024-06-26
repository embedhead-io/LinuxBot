from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFontMetrics


class CustomTextEdit(QTextEdit):
    returnPressed = pyqtSignal()

    MAX_VISIBLE_LINES = (
        3  # Maximum number of visible lines before showing the scrollbar
    )
    ADDITIONAL_HEIGHT = 20  # Additional height to account for padding or borders

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.textChanged.connect(self.toggle_scrollbar)
        self.setLineWrapMode(QTextEdit.WidgetWidth)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Calculate the line height based on the current font
        font_metrics = QFontMetrics(self.font())
        line_height = font_metrics.lineSpacing()
        self.setMaximumHeight(
            line_height * self.MAX_VISIBLE_LINES + self.ADDITIONAL_HEIGHT
        )

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if event.modifiers() & Qt.ShiftModifier:
                super().keyPressEvent(event)  # Allow Shift+Enter for a new line
            else:
                self.returnPressed.emit()  # Emit the returnPressed signal
        else:
            super().keyPressEvent(event)

    def toggle_scrollbar(self):
        """Toggle the visibility of the scrollbar based on the number of lines."""
        lines = self.document().blockCount()
        self.setVerticalScrollBarPolicy(
            Qt.ScrollBarAsNeeded
            if lines > self.MAX_VISIBLE_LINES
            else Qt.ScrollBarAlwaysOff
        )
