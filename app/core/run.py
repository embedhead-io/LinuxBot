import sys
import os

# Add the project root directory to sys.path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from PyQt5.QtWidgets import QApplication
from app.ui.main_window import OpalApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OpalApp()
    sys.exit(app.exec_())
