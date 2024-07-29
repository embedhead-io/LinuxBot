import os
import json
import markdown
import threading
from PyQt5.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QLabel,
    QListWidget,
    QComboBox,
    QWidget,
    QShortcut,
    QLineEdit,
    QDialog,
    QAction,
    QMenu,
)
from PyQt5.QtGui import (
    QFont,
    QKeySequence,
    QTextCursor,
    QTextFrameFormat,
    QTextCharFormat,
    QColor,
)
from PyQt5.QtCore import Qt, pyqtSlot

from app.core.bot_thread import BotThread
from app.core.custom_text_edit import CustomTextEdit
from app.core.status_label import StatusLabel
from app.llm.config import DEFAULT_MODEL, OPENAI_MODELS, OPENAI_SYSTEM_MESSAGE


class OpalApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.mutex = threading.Lock()
        self.bot_thread_per_chat = {}
        self.chat_log = {"(New Chat)": []}
        self.current_chat = "(New Chat)"
        self.CHAT_LOG_DIR = "app/.chat_logs"
        self.is_dark_mode = False
        self.sidebar_width = 140
        self.init_ui()
        self.load_chat_history()
        self.apply_ui_settings()

    def init_ui(self):
        self.setWindowTitle("Opal")
        self.setGeometry(50, 50, 1000, 700)
        self.create_shortcuts()
        self.create_widgets()
        self.create_layouts()
        self.connect_signals()
        self.setCentralWidget(self.main_widget)
        self.switch_chat(self.current_chat)
        self.set_app_stylesheet()
        index = self.model_selector.findText("gpt-4o", Qt.MatchFixedString)
        if index >= 0:
            self.model_selector.setCurrentIndex(index)

    def apply_ui_settings(self):
        if True:
            self.hide_panels()
        self.set_app_stylesheet()

    def hide_panels(self):
        self.chats_list_widget.hide()
        self.model_selector.hide()
        self.new_chat_button.hide()
        self.rename_chat_button.hide()
        self.delete_chat_button.hide()
        self.toggle_button.setText(">")

    def toggle_mode(self):
        self.is_dark_mode = not self.is_dark_mode
        self.set_app_stylesheet()

    def set_app_stylesheet(self):
        from .styles import light_mode_stylesheet, dark_mode_stylesheet

        self.setStyleSheet(
            dark_mode_stylesheet if self.is_dark_mode else light_mode_stylesheet
        )
        self.mode_toggle_button.setText(
            "Light Mode" if self.is_dark_mode else "Dark Mode"
        )

    def create_shortcuts(self):
        self.create_shortcut("Ctrl+N", self.create_new_chat)
        self.create_shortcut("Ctrl+R", self.rename_current_chat)
        self.create_shortcut("Ctrl+D", self.delete_current_chat)
        self.create_shortcut("Ctrl+Tab", self.toggle_left_panel)
        self.create_shortcut("Ctrl+B", self.cycle_through_chats)
        self.create_shortcut("Ctrl+T", self.toggle_mode)
        self.create_shortcut("Esc", self.close)
        self.create_shortcut("Ctrl+Q", self.close)

    def create_shortcut(self, key_sequence, func):
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
        self.chat_input.setFixedHeight(50)

        self.mode_toggle_button = QPushButton("Dark Mode")
        self.mode_toggle_button.setFont(font)
        self.mode_toggle_button.clicked.connect(self.toggle_mode)

        self.model_selector = QComboBox()
        self.model_selector.setFont(font)
        self.model_selector.addItems([model for model in OPENAI_MODELS])

        self.new_chat_button = QPushButton("New Chat")
        self.new_chat_button.setFont(font)

        self.rename_chat_button = QPushButton("Rename Chat")
        self.rename_chat_button.setFont(font)

        self.delete_chat_button = QPushButton("Delete Chat")
        self.delete_chat_button.setFont(font)

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
        self.left_layout.addStretch(1)

        self.sidebar_widget = QWidget()
        self.sidebar_widget.setLayout(self.left_layout)
        self.sidebar_widget.setFixedWidth(self.sidebar_width)

        self.chat_layout = QVBoxLayout()
        self.chat_layout.addWidget(self.chat_log_display)
        self.chat_layout.addWidget(self.chat_input)
        self.chat_layout.addWidget(self.send_button)
        self.chat_layout.addWidget(self.status_label)

        self.main_layout = QHBoxLayout()
        self.main_layout.addWidget(self.sidebar_widget, 0)
        self.main_layout.addLayout(self.chat_layout, 1)

        self.main_widget = QWidget()
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

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

    def adjust_main_window_width(self):
        if self.sidebar_widget.isVisible():
            new_width = self.initial_chat_width + self.sidebar_width
        else:
            new_width = self.initial_chat_width
        self.setFixedWidth(new_width)

    def connect_signals(self):
        self.toggle_button.clicked.connect(self.toggle_left_panel)
        self.send_button.clicked.connect(self.send_message)
        self.chat_input.returnPressed.connect(self.send_message)
        self.new_chat_button.clicked.connect(self.create_new_chat)
        self.rename_chat_button.clicked.connect(self.rename_current_chat)
        self.delete_chat_button.clicked.connect(self.delete_current_chat)
        self.chats_list_widget.currentItemChanged.connect(
            lambda new_item, _: self.switch_chat(
                new_item.text() if new_item else "(New Chat)"
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

    def post_message(self, message, sender="user", url=""):
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
        chat_name = "(New Chat)"
        self.chats_list_widget.addItem(chat_name)
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

    def switch_chat(self, chat_name, update_ui=True):
        if chat_name:
            self.current_chat = chat_name
            self.setWindowTitle(f"{self.current_chat}")
            if update_ui:
                self.chat_log_display.clear()
                displayed_messages = set()
                if chat_name in self.chat_log:
                    for log in self.chat_log[chat_name]:
                        message_key = f"{log['content']}{log['role']}"
                        if (
                            message_key not in displayed_messages
                            and log["role"] != "system"
                        ):
                            self.update_ui(log["content"], log["role"])
                            displayed_messages.add(message_key)
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

    def adjust_input_size(self):
        doc_height = self.chat_input.document().size().toSize().height()
        self.chat_input.setFixedHeight(doc_height + 20)
        max_height = 150
        if self.chat_input.height() > max_height:
            self.chat_input.setFixedHeight(max_height)

    def update_ui(self, message, sender, url=""):
        cursor = self.chat_log_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        frame_format = QTextFrameFormat()
        frame_format.setPadding(5)
        frame_format.setBorder(1)
        frame_format.setBorderStyle(QTextFrameFormat.BorderStyle_Solid)
        frame_format.setBackground(
            QColor.fromRgb(245, 250, 255, 255)
            if sender == "user"
            else QColor.fromRgb(210, 230, 255, 255)
        )
        frame_format.setBorderBrush(
            QColor.fromRgb(0, 0, 0, 50)
            if sender == "user"
            else QColor.fromRgb(0, 0, 0, 65)
        )
        cursor.insertFrame(frame_format)

        html_message = markdown.markdown(message)
        char_format = QTextCharFormat()
        char_format.setFontPointSize(10)
        char_format.setFontWeight(QFont.Bold)
        prefix = "<b>Me:</b>" if sender == "user" else "<b>Opal:</b>"
        cursor.insertHtml(prefix + html_message)

        if url:
            url_format = QTextCharFormat()
            url_format.setFontPointSize(10)
            url_format.setFontWeight(QFont.Bold)
            url_format.setUnderlineStyle(QTextCharFormat.SingleUnderline)
            url_format.setAnchor(True)
            url_format.setAnchorHref(url)
            url_format.setForeground(QColor.fromRgb(0, 0, 255))
            cursor.insertText(" (URL: ", char_format)
            cursor.insertText(url, url_format)
            cursor.insertText(")", char_format)

        cursor.movePosition(QTextCursor.End)
        self.chat_log_display.setTextCursor(cursor)
        self.chat_log_display.verticalScrollBar().setValue(
            self.chat_log_display.verticalScrollBar().maximum()
        )

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
        screen = self.screen()
        screen_geometry = screen.availableGeometry()
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
