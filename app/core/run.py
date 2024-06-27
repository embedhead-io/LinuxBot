import sys
import os
import logging
from PyQt5.QtWidgets import QApplication
from app.ui.main_window import OpalApp

# Add the project root directory to sys.path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)


# Configure logging
logging.basicConfig(level=logging.DEBUG)


if __name__ == "__main__":
    logging.debug("Starting application")

    # Create the application
    app = QApplication(sys.argv)
    logging.debug("QApplication created")

    # Create the main window
    window = OpalApp()
    logging.debug("Main window created")

    # Show the main window
    window.show()
    logging.debug("Main window shown")

    # Execute the application
    sys.exit(app.exec_())
    logging.debug("Application exited")
