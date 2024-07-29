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
    background-color: #121212;
}
QTextEdit {
    background-color: #1E1E1E;
    color: #E0E0E0;
    border: 1px solid #444444;
    padding: 5px;
}
QPushButton {
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #333333, stop:1 #222222);
    color: #CCCCCC;
    border: none;
    padding: 6px 12px;
    font-size: 14px;
    border-radius: 5px;
}
QPushButton:hover {
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #555555, stop:1 #444444);
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
QTextEdit[role="user"] {
    background-color: #2E2E2E;
    color: #E0E0E0;
    border: 1px solid #444444;
    padding: 5px;
}
QTextEdit[role="assistant"] {
    background-color: #2E2E2E;
    color: #E0E0E0;
    border: 1px solid #555555;
    padding: 5px;
}
"""
