# Stylesheets for Light and Dark Modes

# Light Mode Stylesheet
light_mode_stylesheet = """
QMainWindow {
    background-color: #F0F0F0;
}
QTextEdit {
    background-color: #FFFFFF;
    color: #000000;
    border: 1px solid #CCCCCC;
}
QPushButton {
    background-color: #007ACC;
    color: #FFFFFF;
    border: none;
    padding: 5px 10px;
    font-size: 14px;
    border-radius: 5px;
}
QPushButton:hover {
    background-color: #005F99;
}
QComboBox {
    background-color: #FFFFFF;
    color: #000000;
    border: 1px solid #CCCCCC;
    padding: 5px;
}
QLabel {
    color: #333333;
}
QListWidget {
    background-color: #FFFFFF;
    color: #000000;
    border: 1px solid #CCCCCC;
}
"""

# Dark Mode Stylesheet
dark_mode_stylesheet = """
QMainWindow {
    background-color: #1E1E1E;
}
QTextEdit {
    background-color: #2E2E2E;
    color: #CCCCCC;
    border: 1px solid #444444;
}
QPushButton {
    background-color: #3A3A3A;
    color: #CCCCCC;
    border: none;
    padding: 5px 10px;
    font-size: 14px;
    border-radius: 5px;
}
QPushButton:hover {
    background-color: #555555;
}
QComboBox {
    background-color: #2E2E2E;
    color: #CCCCCC;
    border: 1px solid #444444;
    padding: 5px;
}
QLabel {
    color: #CCCCCC;
}
QListWidget {
    background-color: #2E2E2E;
    color: #CCCCCC;
    border: 1px solid #444444;
}
"""
