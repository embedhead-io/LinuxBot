import datetime
import json
import threading
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import (
    QTextCursor,
    QTextBlockFormat,
    QTextCharFormat,
    QColor,
    QKeySequence,
)
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QLineEdit,
    QPushButton,
    QLabel,
    QShortcut,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QAction,
    QDesktopWidget,
)
from utils import bot


class BotThread(QThread):
    new_message = pyqtSignal(str, str)

    def __init__(self, user_message: str, chat_log: list):
        super().__init__()
        self.user_message = user_message
        self.chat_log = chat_log
        self.mutex = threading.Lock()

    def run(self):
        try:
            with self.mutex:
                ans = bot(self.user_message, self.chat_log)
            self.new_message.emit(ans, "assistant")
        except Exception as e:
            print(f"BotThread error: {e}")


class StatusLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setText("Status: Ready")
        self.setAlignment(Qt.AlignCenter)


class OpalApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.mutex = threading.Lock()
        self.bot_thread = None
        self.chat_log = {}
        self.current_room = "New Chat"
        self.init_ui()
        self.load_chat_history()

    def init_ui(self):
        self.setWindowTitle("Opal")
        self.setGeometry(50, 50, 700, 500)
        self.create_widgets()
        self.create_layouts()
        self.connect_signals()
        self.setCentralWidget(self.main_widget)

        quit_shortcut = QShortcut(QKeySequence("Esc"), self)
        quit_shortcut.activated.connect(self.close)

        self.switch_room(self.current_room)

    def create_widgets(self):
        self.toggle_button = QPushButton("<")
        self.rooms_list_widget = QListWidget()
        self.chat_log_display = QTextEdit(readOnly=True)
        self.chat_input = QLineEdit()
        self.new_room_button = QPushButton("New Room")
        self.scrollbar = self.chat_log_display.verticalScrollBar()
        self.send_button = QPushButton("Send")
        self.status_label = StatusLabel()

        self.rooms_list_widget.addItem("New Chat")
        self.rooms_list_widget.setCurrentRow(0)

        self.rooms_list_widget.setMaximumWidth(200)
        self.rooms_list_widget.setMinimumWidth(200)

        self.rooms_list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.rooms_list_widget.customContextMenuRequested.connect(
            self.show_room_context_menu
        )

    def create_layouts(self):
        self.left_layout = QVBoxLayout()
        self.left_layout.addWidget(self.toggle_button)
        self.left_layout.addWidget(self.rooms_list_widget)
        self.left_layout.addWidget(self.new_room_button)

        self.chat_layout = QVBoxLayout()
        self.chat_layout.addWidget(self.chat_log_display)
        self.chat_layout.addWidget(self.chat_input)
        self.chat_layout.addWidget(self.send_button)
        self.chat_layout.addWidget(self.status_label)

        self.main_layout = QHBoxLayout()
        self.main_layout.addLayout(self.left_layout)
        self.main_layout.addLayout(self.chat_layout)

        self.main_widget = QWidget()
        self.main_widget.setLayout(self.main_layout)

    def connect_signals(self):
        self.toggle_button.clicked.connect(self.toggle_left_panel)
        self.send_button.clicked.connect(self.send_message)
        self.chat_input.returnPressed.connect(self.send_message)
        self.new_room_button.clicked.connect(self.create_new_room)
        self.rooms_list_widget.currentItemChanged.connect(
            lambda new_item, _: self.switch_room(
                new_item.text() if new_item else "New Chat"
            )
        )

    def create_new_room(self):
        room_name = "New Chat " + str(len(self.chat_log) + 1)
        self.rooms_list_widget.addItem(room_name)
        self.chat_log[room_name] = []
        self.switch_room(room_name)

    def showEvent(self, event):
        screen_geometry = QDesktopWidget().availableGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def toggle_left_panel(self):
        self.rooms_list_widget.setHidden(not self.rooms_list_widget.isHidden())
        self.toggle_button.setText(">" if self.rooms_list_widget.isHidden() else "<")

    @pyqtSlot()
    def send_message(self):
        user_message = self.chat_input.text().strip()
        self.chat_input.clear()

        if not user_message:
            return

        self.post_message(user_message, "user")

        with self.mutex:
            if self.current_room not in self.chat_log:
                self.chat_log[self.current_room] = []

            self.bot_thread = BotThread(user_message, self.chat_log[self.current_room])
            self.bot_thread.new_message.connect(self.post_message)
            self.bot_thread.start()

    def post_message(self, message: str, sender: str = "user"):
        with self.mutex:
            if self.current_room not in self.chat_log:
                self.chat_log[self.current_room] = []
            self.chat_log[self.current_room].append(
                {"role": sender, "content": message}
            )

        self.save_chat_history()
        self.update_ui(message, sender)

    def update_ui(self, message: str, sender: str):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor = self.chat_log_display.textCursor()
        block_format = QTextBlockFormat()
        char_format = QTextCharFormat()

        block_format.setTopMargin(10)
        block_format.setBottomMargin(10)

        prefix = "You: " if sender == "user" else "Opal: "

        if sender == "user":
            char_format.setBackground(QColor("#cce5ff"))
        else:
            char_format.setBackground(QColor("#ffcccc"))

        cursor.insertBlock(block_format, char_format)
        cursor.insertText(f"{prefix}{message} ({now})")

        cursor.movePosition(QTextCursor.End)
        self.chat_log_display.setTextCursor(cursor)
        self.scrollbar.setValue(self.scrollbar.maximum())

    def switch_room(self, room_name: str):
        if room_name:
            self.save_chat_history()
            self.current_room = room_name
            self.chat_log_display.clear()
            self.load_chat_history()

            for entry in self.chat_log.get(self.current_room, []):
                self.update_ui(entry["content"], entry["role"])

    def save_chat_history(self):
        with self.mutex:
            empty_rooms = [room for room, logs in self.chat_log.items() if not logs]
            for room in empty_rooms:
                del self.chat_log[room]

            try:
                with open("chat_history.json", "w") as f:
                    json.dump(self.chat_log, f)
            except Exception as e:
                print(f"Error saving chat history: {e}")

    def load_chat_history(self):
        try:
            with open("chat_history.json", "r") as f:
                self.chat_log = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, Exception):
            pass

    def show_room_context_menu(self, position):
        context_menu = QMenu()
        delete_room_action = QAction("Delete Room", self)
        context_menu.addAction(delete_room_action)

        delete_room_action.triggered.connect(self.delete_current_room)
        context_menu.exec_(self.rooms_list_widget.mapToGlobal(position))

    def delete_current_room(self):
        current_item = self.rooms_list_widget.currentItem()
        if current_item and current_item.text() != "New Chat":
            self.rooms_list_widget.takeItem(self.rooms_list_widget.row(current_item))
            if current_item.text() in self.chat_log:
                del self.chat_log[current_item.text()]
                self.switch_room("New Chat")


if __name__ == "__main__":
    app = QApplication([])
    window = OpalApp()
    window.show()
    app.exec_()
