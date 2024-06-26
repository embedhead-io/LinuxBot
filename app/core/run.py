from PyQt5.QtWidgets import QApplication
from app.ui.main_window import OpalApp
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    opal = OpalApp()
    opal.show()
    sys.exit(app.exec_())
