# --- Standard Library Imports ---
import json
import threading

# --- Third-party Imports ---
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import (
    QTextCursor,
    QTextBlockFormat,
    QTextCharFormat,
    QColor,
    QKeySequence,
    QFont,
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
    QMenu,
    QAction,
    QDesktopWidget,
    QDialog,
    QComboBox,
)

# --- Local Imports ---
from config import DEFAULT_MODEL, OPENAI_MODELS
from utils import bot

# --- Constants ---
ROOM_NEW_CHAT = "New Chat"


class BotThread(QThread):
    new_message = pyqtSignal(str, str)

    def __init__(
        self, user_message: str, chat_log: list, selected_model: str = DEFAULT_MODEL
    ):
        super().__init__()
        self.user_message = user_message
        self.chat_log = chat_log
        self.selected_model = selected_model
        self.mutex = threading.Lock()

    def run(self):
        try:
            with self.mutex:
                ans = bot(self.user_message, self.chat_log, self.selected_model)
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
        self.bot_thread_per_room = (
            {}
        )  # New dictionary to hold BotThread instances per room
        self.chat_log = {}
        self.current_room = "New Chat"
        self.init_ui()
        self.load_chat_history()

    def init_ui(self):
        self.setWindowTitle("Opal")
        self.setGeometry(50, 50, 700, 500)

        self.create_shortcuts()
        self.create_widgets()
        self.create_layouts()
        self.connect_signals()
        self.setCentralWidget(self.main_widget)
        self.switch_room(self.current_room)

        # Set the default model from DEFAULT_MODEL in the ComboBox
        index = self.model_selector.findText(DEFAULT_MODEL, Qt.MatchFixedString)
        if index >= 0:
            self.model_selector.setCurrentIndex(index)

        # Hide the left panel widgets when the application starts
        self.rooms_list_widget.hide()
        self.new_chat_button.hide()
        self.rename_chat_button.hide()
        self.model_selector.hide()  # Add this line if you also want to hide the model selector
        self.toggle_button.setText(">")

    def create_shortcuts(self):
        self.create_shortcut("Ctrl+N", self.create_new_chat)
        self.create_shortcut("Ctrl+R", self.rename_current_chat)
        self.create_shortcut("Ctrl+Tab", self.cycle_through_rooms)
        self.create_shortcut("Ctrl+J", self.toggle_left_panel)
        self.create_shortcut("Esc", self.close)
        self.create_shortcut("Ctrl+Q", self.close)

    def create_shortcut(self, key_sequence: str, func):
        shortcut = QShortcut(QKeySequence(key_sequence), self)
        shortcut.activated.connect(func)

    def create_widgets(self):
        font = QFont()
        font.setPointSize(10)

        self.toggle_button = QPushButton("<")
        self.toggle_button.setFont(font)

        self.rooms_list_widget = QListWidget()
        self.rooms_list_widget.setFont(font)

        self.chat_log_display = QTextEdit(readOnly=True)
        self.chat_log_display.setFont(font)

        self.chat_input = QLineEdit()
        self.chat_input.setFont(font)

        self.model_selector = QComboBox()
        self.model_selector.setFont(font)
        self.model_selector.addItems(OPENAI_MODELS)

        self.new_chat_button = QPushButton("New Chat")
        self.new_chat_button.setFont(font)

        self.rename_chat_button = QPushButton("Rename Chat")
        self.rename_chat_button.setFont(font)

        self.scrollbar = self.chat_log_display.verticalScrollBar()

        self.send_button = QPushButton("Send")
        self.send_button.setFont(font)

        self.status_label = StatusLabel()
        self.status_label.setFont(font)

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
        self.left_layout.addWidget(self.model_selector)
        self.left_layout.addWidget(self.new_chat_button)
        self.left_layout.addWidget(self.rename_chat_button)

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
        self.new_chat_button.clicked.connect(self.create_new_chat)
        self.rename_chat_button.clicked.connect(self.rename_current_chat)
        self.rooms_list_widget.currentItemChanged.connect(
            lambda new_item, _: self.switch_room(
                new_item.text() if new_item else "New Chat"
            )
        )

    @pyqtSlot()
    def send_message(self):
        user_message = self.chat_input.text().strip()
        self.chat_input.clear()

        if not user_message:
            return

        self.status_label.setText("Status: Typing...")
        self.post_message(user_message, "user")

        selected_model = self.model_selector.currentText()

        with self.mutex:
            if self.current_room not in self.chat_log:
                self.chat_log[self.current_room] = []

            # Create a new BotThread if not already created for this room
            if self.current_room not in self.bot_thread_per_room:
                self.bot_thread_per_room[self.current_room] = BotThread(
                    user_message, self.chat_log[self.current_room], selected_model
                )
                self.bot_thread_per_room[self.current_room].new_message.connect(
                    self.post_message
                )
                self.bot_thread_per_room[self.current_room].finished.connect(
                    self.reset_status
                )

            else:
                # Update the existing BotThread's information for this room
                self.bot_thread_per_room[self.current_room].user_message = user_message
                self.bot_thread_per_room[self.current_room].chat_log = self.chat_log[
                    self.current_room
                ]
                self.bot_thread_per_room[
                    self.current_room
                ].selected_model = selected_model

            self.bot_thread_per_room[self.current_room].start()

    def post_message(self, message: str, sender: str = "user"):
        with self.mutex:
            if self.current_room not in self.chat_log:
                self.chat_log[self.current_room] = []
            self.chat_log[self.current_room].append(
                {"role": sender, "content": message}
            )

        self.save_chat_history()
        self.update_ui(message, sender)

    def reset_status(self):
        self.status_label.setText("Status: Ready")

    def create_new_chat(self):
        room_name = "New Chat " + str(len(self.chat_log) + 1)
        self.rooms_list_widget.addItem(room_name)
        self.chat_log[room_name] = []
        self.switch_room(room_name)
        self.chat_input.setFocus()

    def rename_current_chat(self):
        current_item = self.rooms_list_widget.currentItem()
        if current_item:
            dialog = QDialog(self)
            dialog.setWindowTitle("Rename Chat")

            layout = QVBoxLayout()

            new_name_input = QLineEdit()
            new_name_input.setText(current_item.text())
            new_name_input.selectAll()

            layout.addWidget(new_name_input)

            confirm_button = QPushButton("Confirm")
            cancel_button = QPushButton("Cancel")

            layout.addWidget(confirm_button)
            layout.addWidget(cancel_button)

            dialog.setLayout(layout)

            confirm_button.clicked.connect(dialog.accept)
            cancel_button.clicked.connect(dialog.reject)

            result = dialog.exec_()
            if result == QDialog.Accepted:
                new_name = new_name_input.text()
                if new_name:
                    old_name = current_item.text()
                    current_item.setText(new_name)
                    self.chat_log[new_name] = self.chat_log.pop(old_name, [])
                    self.switch_room(new_name)

    def switch_room(self, room_name: str, update_ui: bool = True):
        if room_name:
            self.save_chat_history()
            self.current_room = room_name
            self.setWindowTitle(f"Opal - {self.current_room}")

            if update_ui:
                self.chat_log_display.clear()
                displayed_messages = (
                    set()
                )  # Add this line to keep track of displayed messages
                if room_name in self.chat_log:
                    for log in self.chat_log[room_name]:
                        message_key = f"{log['content']}{log['role']}"
                        if message_key not in displayed_messages:  # Add this check
                            self.update_ui(log["content"], log["role"])
                            displayed_messages.add(
                                message_key
                            )  # Mark message as displayed

            items = [
                self.rooms_list_widget.item(i).text()
                for i in range(self.rooms_list_widget.count())
            ]
            if room_name in items:
                row = items.index(room_name)
                self.rooms_list_widget.setCurrentRow(row)
            else:
                self.rooms_list_widget.addItem(room_name)
                self.rooms_list_widget.setCurrentRow(self.rooms_list_widget.count() - 1)

    def cycle_through_rooms(self):
        current_row = self.rooms_list_widget.currentRow()
        next_row = (current_row + 1) % self.rooms_list_widget.count()
        self.rooms_list_widget.setCurrentRow(next_row)
        new_item = self.rooms_list_widget.item(next_row)
        self.switch_room(new_item.text())

    def toggle_left_panel(self):
        if self.rooms_list_widget.isVisible():
            self.rooms_list_widget.hide()
            self.model_selector.hide()
            self.new_chat_button.hide()
            self.rename_chat_button.hide()
            self.toggle_button.setText(">")
        else:
            self.rooms_list_widget.show()
            self.model_selector.show()
            self.new_chat_button.show()
            self.rename_chat_button.show()
            self.toggle_button.setText("<")

    def update_ui(self, message: str, sender: str):
        cursor = self.chat_log_display.textCursor()

        # Block Format for controlling the box around each message
        block_format = QTextBlockFormat()
        block_format.setTopMargin(5)
        block_format.setBottomMargin(5)

        # Char Format for controlling the appearance of the text
        char_format = QTextCharFormat()
        char_format.setFontPointSize(10)  # Font size set to 10
        if sender == "user":
            char_format.setBackground(QColor("#FFFFFF"))  # White for user
        else:
            char_format.setBackground(
                QColor("#F0F0F0")
            )  # Very light grey for assistant

        # Move to the end of the existing text and insert a new block for the message
        cursor.movePosition(QTextCursor.End)
        cursor.insertBlock(block_format)

        # Insert the text itself
        cursor.setCharFormat(char_format)
        prefix = "You: " if sender == "user" else "Opal: "
        cursor.insertText(f"{prefix}{message}")

        # Ensure the latest message is visible
        cursor.movePosition(QTextCursor.End)
        self.chat_log_display.setTextCursor(cursor)
        self.scrollbar.setValue(self.scrollbar.maximum())

    def show_room_context_menu(self, position):
        context_menu = QMenu()
        rename_room_action = QAction("Rename Room", self)
        context_menu.addAction(rename_room_action)
        rename_room_action.triggered.connect(self.rename_current_chat)

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

    def load_chat_history(self):
        try:
            with open("chat_history.json", "r") as f:
                self.chat_log = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, Exception):
            pass

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

    def showEvent(self, event):
        screen_geometry = QDesktopWidget().availableGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)
        self.chat_input.setFocus()


if __name__ == "__main__":
    app = QApplication([])
    window = OpalApp()
    window.show()
    app.exec_()
