from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFontMetrics


class CustomTextEdit(QTextEdit):
    returnPressed = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.textChanged.connect(self.toggle_scrollbar)
        self.setLineWrapMode(QTextEdit.WidgetWidth)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        font_metrics = QFontMetrics(self.font())
        line_height = font_metrics.lineSpacing()
        self.setMaximumHeight(line_height * 3 + 20)  # Adjust as necessary

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if event.modifiers() & Qt.ShiftModifier:
                super().keyPressEvent(event)  # For a new line
            else:
                self.returnPressed.emit()  # Emitting the signal
        else:
            super().keyPressEvent(event)

    def toggle_scrollbar(self):
        lines = self.document().blockCount()
        self.setVerticalScrollBarPolicy(
            Qt.ScrollBarAsNeeded if lines > 3 else Qt.ScrollBarAlwaysOff
        )
