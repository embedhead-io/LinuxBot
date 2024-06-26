from PyQt5.QtWidgets import QApplication
from app.ui.main_window import OpalApp

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    opal = OpalApp()
    opal.show()
    app.exec_()
