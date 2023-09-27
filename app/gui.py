# gui.py
import json
import logging
import os
import threading
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import (
    QTextCursor,
    QTextCharFormat,
    QTextFrameFormat,
    QColor,
    QKeySequence,
    QFont,
    QFontMetrics,
)
from PyQt5.QtWidgets import (
    qApp,
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

from llm import (
    DEFAULT_MODEL,
    OPENAI_MODELS,
    OPENAI_SYSTEM_MESSAGE,
)
from utils import (
    process_message,
)

# Logging
import logging

logging.basicConfig(level=logging.DEBUG)

# Constants
chat_NEW_CHAT = "(New Chat)"

# Settings
hide_panel_on_start = True


class BotThread(QThread):
    new_message = pyqtSignal(str, str, str, str)  # Modify signal to include URL

    def __init__(
        self,
        user_message: str,
        chat_log: dict,
        selected_model: str = DEFAULT_MODEL,
    ):
        super().__init__()
        self.user_message = user_message
        self.chat_log = chat_log
        self.selected_model = selected_model

    def run(self):
        try:
            response_message, url, self.chat_log = process_message(
                self.user_message,
                self.chat_log,
            )
            self.new_message.emit(response_message, "assistant", "", url if url else "")
        except Exception as e:
            logging.error(f"Error generating response: {e}")


class StatusLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setText("Status: Ready")
        self.setAlignment(Qt.AlignCenter)


class CustomTextEdit(QTextEdit):
    returnPressed = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.textChanged.connect(self.toggle_scrollbar)
        self.setLineWrapMode(QTextEdit.WidgetWidth)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Set the maximum height to correspond to 3 lines of text
        font_metrics = QFontMetrics(self.font())
        line_height = font_metrics.lineSpacing()
        self.setMaximumHeight(line_height * 3 + 20)  # Adjust as necessary

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            if event.modifiers() & Qt.ShiftModifier:
                super(CustomTextEdit, self).keyPressEvent(event)  # For a new line
            else:
                self.returnPressed.emit()  # Emitting the signal
        else:
            super(CustomTextEdit, self).keyPressEvent(event)

    def toggle_scrollbar(self):
        # Get the number of lines in the QTextEdit
        lines = self.document().blockCount()

        # Set scrollbar policy based on line count
        if lines > 3:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        else:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)


class OpalApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.mutex = threading.Lock()
        self.bot_thread_per_chat = {}
        self.chat_log = {"(New Chat)": []}  # Initialize chat_log properly
        self.current_chat = "(New Chat)"
        self.CHAT_LOG_DIR = "chat_logs"
        self.is_dark_mode = False
        self.init_ui()
        self.load_chat_history()
        self.apply_ui_settings()

    def init_ui(self):
        self.setWindowTitle("Opal")
        self.setGeometry(
            50,  # X
            50,  # Y
            700,  # Width
            525,  # Height
        )
        self.create_shortcuts()
        self.create_widgets()
        self.create_layouts()
        self.connect_signals()
        self.setCentralWidget(self.main_widget)
        self.switch_chat(self.current_chat)
        self.set_app_stylesheet()
        index = self.model_selector.findText(DEFAULT_MODEL, Qt.MatchFixedString)
        if index >= 0:
            self.model_selector.setCurrentIndex(index)

    def apply_ui_settings(self):
        if hide_panel_on_start:
            self.hide_panels()

        # Apply the initial stylesheet based on the current mode
        self.set_app_stylesheet()

    def hide_panels(self):
        self.chats_list_widget.hide()
        self.model_selector.hide()
        self.new_chat_button.hide()
        self.rename_chat_button.hide()
        self.delete_chat_button.hide()
        self.toggle_button.setText(">")

    def toggle_mode(self):
        # Toggle between light and dark modes
        self.is_dark_mode = not self.is_dark_mode
        self.set_app_stylesheet()

    def set_app_stylesheet(self):
        # Define your light and dark mode stylesheets
        light_mode_stylesheet = """
        QMainWindow {
            background-color: #FFFFFF;
        }

        /* Add more styles for other widgets as needed */
        """

        dark_mode_stylesheet = """
        QMainWindow {
            background-color: #1E1E1E;
        }

        /* Add more styles for other widgets as needed */
        """

        # Set the stylesheet for the entire application based on the current mode
        if self.is_dark_mode:
            qApp.setStyleSheet(dark_mode_stylesheet)
            self.mode_toggle_button.setText("Light Mode")
        else:
            qApp.setStyleSheet(light_mode_stylesheet)
            self.mode_toggle_button.setText("Dark Mode")

    def create_shortcuts(self):
        self.create_shortcut("Ctrl+N", self.create_new_chat)
        self.create_shortcut("Ctrl+R", self.rename_current_chat)
        self.create_shortcut("Ctrl+D", self.delete_current_chat)
        self.create_shortcut("Ctrl+Tab", self.toggle_left_panel)
        self.create_shortcut("Ctrl+B", self.cycle_through_chats)
        self.create_shortcut("Ctrl+T", self.toggle_mode)
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

        self.chats_list_widget = QListWidget()
        self.chats_list_widget.setFont(font)

        self.chat_log_display = QTextEdit(readOnly=True)
        self.chat_log_display.setFont(font)

        self.chat_input = CustomTextEdit()
        self.chat_input.setFont(font)
        self.chat_input.textChanged.connect(self.adjust_input_size)
        self.chat_input.setFixedHeight(50)  # Set an initial height

        # Add a toggle button for light/dark mode
        self.mode_toggle_button = QPushButton("Dark Mode")
        self.mode_toggle_button.setFont(font)
        self.mode_toggle_button.clicked.connect(self.toggle_mode)

        self.model_selector = QComboBox()
        self.model_selector.setFont(font)
        self.model_selector.addItems(OPENAI_MODELS)

        self.new_chat_button = QPushButton("New Chat")
        self.new_chat_button.setFont(font)

        self.rename_chat_button = QPushButton("Rename Chat")
        self.rename_chat_button.setFont(font)

        self.delete_chat_button = QPushButton("Delete Chat")
        self.delete_chat_button.setFont(font)

        self.scrollbar = self.chat_log_display.verticalScrollBar()

        self.send_button = QPushButton("Send")
        self.send_button.setFont(font)

        self.status_label = StatusLabel()
        self.status_label.setFont(font)

        self.chats_list_widget.addItem("(New Chat)")
        self.chats_list_widget.setCurrentRow(0)

        self.chats_list_widget.setMaximumWidth(200)
        self.chats_list_widget.setMinimumWidth(200)

        self.chats_list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.chats_list_widget.customContextMenuRequested.connect(
            self.show_chat_context_menu
        )

    def create_layouts(self):
        self.left_layout = QVBoxLayout()
        self.left_layout.addWidget(self.toggle_button)
        self.left_layout.addWidget(self.chats_list_widget)
        self.left_layout.addWidget(self.model_selector)
        self.left_layout.addWidget(self.new_chat_button)
        self.left_layout.addWidget(self.rename_chat_button)
        self.left_layout.addWidget(self.delete_chat_button)

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
        self.delete_chat_button.clicked.connect(self.delete_current_chat)
        self.chats_list_widget.currentItemChanged.connect(
            lambda new_item, _: self.switch_chat(
                new_item.text() if new_item else "New Chat"
            )
        )

    @pyqtSlot()
    def send_message(self):
        user_message = self.chat_input.toPlainText().strip()
        self.chat_input.clear()

        if not user_message:
            return

        self.status_label.setText("Status: Typing...")
        self.post_message(user_message, "user")

        selected_model = self.model_selector.currentText()

        with self.mutex:
            if self.current_chat not in self.chat_log:
                self.chat_log[self.current_chat] = [OPENAI_SYSTEM_MESSAGE]

            # Append the user message to the chat log
            self.chat_log[self.current_chat].append(
                {"role": "user", "content": user_message}
            )

            if self.current_chat not in self.bot_thread_per_chat:
                self.bot_thread_per_chat[self.current_chat] = BotThread(
                    user_message, self.chat_log[self.current_chat], selected_model
                )
                self.bot_thread_per_chat[self.current_chat].new_message.connect(
                    self.post_message
                )
                self.bot_thread_per_chat[self.current_chat].finished.connect(
                    self.reset_status
                )
            else:
                self.bot_thread_per_chat[self.current_chat].user_message = user_message
                self.bot_thread_per_chat[self.current_chat].chat_log = self.chat_log[
                    self.current_chat
                ]
                self.bot_thread_per_chat[
                    self.current_chat
                ].selected_model = selected_model

            self.bot_thread_per_chat[self.current_chat].start()

    def post_message(self, message: str, sender: str = "user", url: str = ""):
        with self.mutex:
            if self.current_chat not in self.chat_log:
                self.chat_log[self.current_chat] = [OPENAI_SYSTEM_MESSAGE]
            elif not isinstance(self.chat_log[self.current_chat], list):
                self.chat_log[self.current_chat] = [self.chat_log[self.current_chat]]
            self.chat_log[self.current_chat].append(
                {"role": sender, "content": message}
            )

        self.save_chat_history(
            self.current_chat, {"role": sender, "content": message, "url": url}
        )
        self.update_ui(message, sender, url)

    def reset_status(self):
        self.status_label.setText("Status: Ready")

    def create_new_chat(self):
        chat_name = "New Chat " + str(len(self.chat_log) + 1)
        self.chats_list_widget.addItem(chat_name)

        # Initialize chat_log as an empty list for the new chat
        self.chat_log[chat_name] = []

        self.switch_chat(chat_name)
        self.chat_input.setFocus()

    def rename_current_chat(self):
        current_item = self.chats_list_widget.currentItem()
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
                    self.switch_chat(new_name)

                    old_chat_log_path = os.path.join(
                        self.CHAT_LOG_DIR, f"{old_name}.json"
                    )

                    with open(old_chat_log_path, "r") as f:
                        old_chat_log = json.load(f)
                        with open(
                            os.path.join(self.CHAT_LOG_DIR, f"{new_name}.json"), "w"
                        ) as f:
                            json.dump(old_chat_log, f)

                    if os.path.exists(old_chat_log_path):
                        os.remove(old_chat_log_path)

    def switch_chat(self, chat_name: str, update_ui: bool = True):
        if chat_name:
            self.current_chat = chat_name
            self.setWindowTitle(f"{self.current_chat}")

            if update_ui:
                self.chat_log_display.clear()
                displayed_messages = set()  # To keep track of displayed messages
                if chat_name in self.chat_log:
                    for log in self.chat_log[chat_name]:
                        message_key = f"{log['content']}{log['role']}"
                        if (
                            message_key not in displayed_messages
                            and log["role"] != "system"
                        ):
                            self.update_ui(log["content"], log["role"])
                            displayed_messages.add(
                                message_key
                            )  # Mark message as displayed

            items = [
                self.chats_list_widget.item(i).text()
                for i in range(self.chats_list_widget.count())
            ]
            if chat_name in items:
                row = items.index(chat_name)
                self.chats_list_widget.setCurrentRow(row)
            else:
                self.chats_list_widget.addItem(chat_name)
                self.chats_list_widget.setCurrentRow(self.chats_list_widget.count() - 1)

    def cycle_through_chats(self):
        current_row = self.chats_list_widget.currentRow()
        next_row = (current_row + 1) % self.chats_list_widget.count()
        self.chats_list_widget.setCurrentRow(next_row)
        new_item = self.chats_list_widget.item(next_row)
        self.switch_chat(new_item.text())

    def toggle_left_panel(self):
        if self.chats_list_widget.isVisible():
            self.chats_list_widget.hide()
            self.model_selector.hide()
            self.new_chat_button.hide()
            self.rename_chat_button.hide()
            self.delete_chat_button.hide()
            self.toggle_button.setText(">")
        else:
            self.chats_list_widget.show()
            self.model_selector.show()
            self.new_chat_button.show()
            self.rename_chat_button.show()
            self.delete_chat_button.show()
            self.toggle_button.setText("<")

    def adjust_input_size(self):
        # Adjust the height of the chat_input widget based on its content
        doc_height = self.chat_input.document().size().toSize().height()
        self.chat_input.setFixedHeight(doc_height + 20)  # Adjust as needed

        # You might want to set a maximum height to prevent it from growing too large
        max_height = 150
        if self.chat_input.height() > max_height:
            self.chat_input.setFixedHeight(max_height)

    def update_ui(self, message: str, sender: str, url: str = ""):
        cursor = self.chat_log_display.textCursor()

        # Move the cursor to the end of the document to avoid overlapping
        cursor.movePosition(QTextCursor.End)

        frame_format = QTextFrameFormat()
        frame_format.setPadding(5)
        frame_format.setBorder(1)
        frame_format.setBorderStyle(QTextFrameFormat.BorderStyle_Solid)
        if sender == "user":
            frame_format.setBackground(QColor.fromRgb(245, 250, 255, 255))
            frame_format.setBorderBrush(QColor.fromRgb(0, 0, 0, 50))
        else:
            frame_format.setBackground(QColor.fromRgb(210, 230, 255, 255))
            frame_format.setBorderBrush(QColor.fromRgb(0, 0, 0, 65))

        cursor.insertFrame(frame_format)

        char_format = QTextCharFormat()
        char_format.setFontPointSize(10)
        char_format.setFontWeight(QFont.Bold)

        prefix = "Me: " if sender == "user" else "Opal: "
        cursor.insertText(prefix, char_format)

        char_format.setFontPointSize(10)
        char_format.setFontWeight(QFont.Normal)

        cursor.insertText(message, char_format)

        if url:
            cursor.insertText(" (URL: ", char_format)
            url_format = QTextCharFormat()
            url_format.setFontPointSize(10)
            url_format.setFontWeight(QFont.Bold)
            url_format.setUnderlineStyle(QTextCharFormat.SingleUnderline)
            url_format.setAnchor(True)
            url_format.setAnchorHref(url)
            url_format.setForeground(QColor.fromRgb(0, 0, 255))
            cursor.insertText(url, url_format)
            cursor.insertText(")", char_format)

        cursor.movePosition(QTextCursor.End)
        self.chat_log_display.setTextCursor(cursor)
        self.scrollbar.setValue(self.scrollbar.maximum())

    def show_chat_context_menu(self, position):
        context_menu = QMenu()
        rename_chat_action = QAction("Rename chat", self)
        context_menu.addAction(rename_chat_action)
        rename_chat_action.triggered.connect(self.rename_current_chat)

        delete_chat_action = QAction("Delete chat", self)
        context_menu.addAction(delete_chat_action)
        delete_chat_action.triggered.connect(self.delete_current_chat)

        context_menu.exec_(self.chats_list_widget.mapToGlobal(position))

    def delete_current_chat(self):
        current_item = self.chats_list_widget.currentItem()
        if current_item and current_item.text() != "(New Chat)":
            self.chats_list_widget.takeItem(self.chats_list_widget.row(current_item))
            if current_item.text() in self.chat_log:
                del self.chat_log[current_item.text()]
                self.switch_chat("(New Chat)")

            chat_log_path = os.path.join(
                self.CHAT_LOG_DIR, f"{current_item.text()}.json"
            )
            if os.path.exists(chat_log_path):
                os.remove(chat_log_path)

    def load_chat_history(self):
        if not os.path.exists(self.CHAT_LOG_DIR):
            return

        for filename in os.listdir(self.CHAT_LOG_DIR):
            chat_name = filename.rsplit(".", 1)[0]
            self.chats_list_widget.addItem(chat_name)

            chat_log_path = os.path.join(self.CHAT_LOG_DIR, filename)
            try:
                with open(chat_log_path, "r") as f:
                    self.chat_log[chat_name] = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError, Exception):
                pass

        self.switch_chat("(New Chat)")

    def save_chat_history(self, chat, new_message):
        chat_log_path = os.path.join(self.CHAT_LOG_DIR, f"{chat}.json")

        with self.mutex:
            try:
                if not os.path.exists(self.CHAT_LOG_DIR):
                    os.makedirs(self.CHAT_LOG_DIR)

                if os.path.exists(chat_log_path):
                    with open(chat_log_path, "r") as f:
                        existing_chat_log = json.load(f)
                else:
                    existing_chat_log = [OPENAI_SYSTEM_MESSAGE]

                existing_chat_log.append(new_message)

                with open(chat_log_path, "w") as f:
                    json.dump(existing_chat_log, f)

            except Exception as e:
                print(f"Error saving chat history: {e}")

    def showEvent(self, event):
        screen_geometry = QDesktopWidget().availableGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)
        self.chat_input.setFocus()

    def closeEvent(self, event):
        if self.current_chat == "(New Chat)":
            file_path = os.path.join(self.CHAT_LOG_DIR, f"{self.current_chat}.json")
            if os.path.exists(file_path):
                os.remove(file_path)
        event.accept()


if __name__ == "__main__":
    import sys

    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    opal = OpalApp()
    opal.show()
    app.exec_()
