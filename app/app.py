from PyQt5.QtWidgets import QApplication
from gui import OpalApp


def main():
    app = QApplication([])
    window = OpalApp()
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()