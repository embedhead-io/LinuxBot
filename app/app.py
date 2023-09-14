from PyQt5.QtWidgets import QApplication
from gui import OpalApp
import logging

logging.basicConfig(level=logging.DEBUG)


if __name__ == "__main__":
    app = QApplication([])
    opal = OpalApp()
    opal.show()
    app.exec_()
