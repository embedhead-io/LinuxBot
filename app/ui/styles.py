light_mode_stylesheet = """
QMainWindow {
    background-color: #F0F0F0;
}
QTextEdit {
    background-color: #FFFFFF;
    color: #000000;
    border: 1px solid #CCCCCC;
    padding: 5px;
}
QPushButton {
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #009BDF, stop:1 #007ACC);
    color: #FFFFFF;
    border: none;
    padding: 6px 12px;
    font-size: 14px;
    border-radius: 5px;
}
QPushButton:hover {
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #007ACC, stop:1 #005F99);
    border: 1px solid #007ACC;
}
QPushButton:pressed {
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


dark_mode_stylesheet = """
QMainWindow {
    background-color: #1E1E1E;
}
QTextEdit {
    background-color: #2E2E2E;
    color: #CCCCCC;
    border: 1px solid #444444;
    padding: 5px;
}
QPushButton {
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4A4A4A, stop:1 #3A3A3A);
    color: #CCCCCC;
    border: none;
    padding: 6px 12px;
    font-size: 14px;
    border-radius: 5px;
}
QPushButton:hover {
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3A3A3A, stop:1 #555555);
    border: 1px solid #555555;
}
QPushButton:pressed {
    background-color: #333333;
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
