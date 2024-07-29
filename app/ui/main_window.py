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

# OK #


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
        # OK, Side is open #

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Opal")
        self.setGeometry(50, 50, 1000, 700)
        self.create_shortcuts()
        self.create_widgets()
        self.create_layouts()
        self.connect_signals()
        self.setCentralWidget(self.main_widget)
        self.load_chat_history()
        self.apply_ui_settings()
        # OK, Side is closed #

    def apply_ui_settings(self):
        """Apply UI settings such as hiding panels and setting the stylesheet."""
        self.hide_panels()
        self.set_app_stylesheet()
        # Updated func #

    def hide_panels(self):
        """Hide UI panels based on certain conditions."""
        self.chats_list_widget.hide()
        self.model_selector.hide()
        self.new_chat_button.hide()
        self.rename_chat_button.hide()
        self.delete_chat_button.hide()
        self.toggle_button.setText(">")
        # Updated func #

    def toggle_mode(self):
        """Toggle between light and dark mode."""
        self.is_dark_mode = not self.is_dark_mode
        self.set_app_stylesheet()
        # Updated func #

    def set_app_stylesheet(self):
        """Set the application stylesheet based on the current mode."""
        from .styles import light_mode_stylesheet, dark_mode_stylesheet

        self.setStyleSheet(
            dark_mode_stylesheet if self.is_dark_mode else light_mode_stylesheet
        )
        self.mode_toggle_button.setText(
            "Light Mode" if self.is_dark_mode else "Dark Mode"
        )
        # Updated func #

    def create_shortcuts(self):
        """Create keyboard shortcuts for the application."""
        shortcuts = {
            "Ctrl+N": self.create_new_chat,
            "Ctrl+R": self.rename_current_chat,
            "Ctrl+D": self.delete_current_chat,
            "Ctrl+Tab": self.toggle_left_panel,
            "Ctrl+B": self.cycle_through_chats,
            "Ctrl+T": self.toggle_mode,
            "Esc": self.close,
            "Ctrl+Q": self.close,
        }
        for key_sequence, func in shortcuts.items():
            self.create_shortcut(key_sequence, func)
            # DOES NOT OPEN WITHOUT ABOVE FUNCS #

    def create_shortcut(self, key_sequence, func):
        """Helper method to create a single shortcut."""
        shortcut = QShortcut(QKeySequence(key_sequence), self)
        shortcut.activated.connect(func)
        # No change #

    def create_widgets(self):
        """Create and configure the widgets for the UI."""
        font = QFont()
        font.setPointSize(10)

        self.toggle_button = self.create_button("<", font)
        self.mode_toggle_button = self.create_button(
            "Dark Mode", font, self.toggle_mode
        )
        self.new_chat_button = self.create_button("New Chat", font)
        self.rename_chat_button = self.create_button("Rename Chat", font)
        self.delete_chat_button = self.create_button("Delete Chat", font)
        self.send_button = self.create_button("Send", font)

        self.chats_list_widget = self.create_list_widget(font)
        self.chat_log_display = self.create_text_edit(font, read_only=True)
        self.chat_input = self.create_custom_text_edit(font)

        self.model_selector = self.create_combo_box(font, OPENAI_MODELS)

        self.status_label = StatusLabel()
        self.status_label.setFont(font)

        self.chats_list_widget.addItem("(New Chat)")
        self.chats_list_widget.setCurrentRow(0)
        self.chats_list_widget.setMaximumWidth(200)
        self.chats_list_widget.setMinimumWidth(200)
        # No change #

    def create_layouts(self):
        """Create and configure the layouts for the UI."""
        self.left_layout = self.create_left_layout()
        self.chat_layout = self.create_chat_layout()

        self.main_layout = QHBoxLayout()
        self.main_layout.addWidget(self.create_sidebar_widget(), 0)
        self.main_layout.addLayout(self.chat_layout, 1)

        self.main_widget = QWidget()
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)
        # Updated func #

    def create_left_layout(self):
        """Create the left layout for the sidebar."""
        layout = QVBoxLayout()
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.chats_list_widget)
        layout.addWidget(self.model_selector)
        layout.addWidget(self.new_chat_button)
        layout.addWidget(self.rename_chat_button)
        layout.addWidget(self.delete_chat_button)
        layout.addStretch(1)
        return layout
        # NEW FUNC!!! #

    def create_button(self, text, font, callback=None):
        """Helper method to create a QPushButton."""
        button = QPushButton(text)
        button.setFont(font)
        if callback:
            button.clicked.connect(callback)
        return button
        # NEW FUNC!!! #

    def create_list_widget(self, font):
        """Helper method to create a QListWidget."""
        list_widget = QListWidget()
        list_widget.setFont(font)
        list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        list_widget.customContextMenuRequested.connect(self.show_chat_context_menu)
        return list_widget
        # NEW FUNC!!! #

    def create_text_edit(self, font, read_only=False):
        """Helper method to create a QTextEdit."""
        text_edit = QTextEdit(readOnly=read_only)
        text_edit.setFont(font)
        return text_edit
        # NEW FUNC!!! #

    def create_custom_text_edit(self, font):
        """Helper method to create a CustomTextEdit."""
        text_edit = CustomTextEdit()
        text_edit.setFont(font)
        text_edit.textChanged.connect(self.adjust_input_size)
        text_edit.setFixedHeight(50)
        return text_edit
        # NEW FUNC!!! #

    def create_combo_box(self, font, items):
        """Helper method to create a QComboBox."""
        combo_box = QComboBox()
        combo_box.setFont(font)
        combo_box.addItems(items)
        return combo_box
        # NEW FUNC!!! #

    def create_chat_layout(self):
        """Create the main chat layout."""
        layout = QVBoxLayout()
        layout.addWidget(self.chat_log_display)
        layout.addWidget(self.chat_input)
        layout.addWidget(self.send_button)
        layout.addWidget(self.status_label)
        return layout
        # NEW FUNC!!! #

    def create_sidebar_widget(self):
        """Create the sidebar widget."""
        sidebar_widget = QWidget()
        sidebar_widget.setLayout(self.left_layout)
        sidebar_widget.setFixedWidth(self.sidebar_width)
        return sidebar_widget
        # NEW FUNC!!! #

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
        """Connect signals to the appropriate slots."""
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
        # Updated func #

    @pyqtSlot()
    def send_message(self):
        """Handle sending a message."""
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
            # Updated func #

    def post_message(self, message, sender="user", url=""):
        """Post a message to the chat log."""
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
        # Updated func #

    def reset_status(self):
        """Reset the status label to ready."""
        self.status_label.setText("Status: Ready")
        # Updated func #

    def create_new_chat(self):
        """Create a new chat."""
        chat_name = "(New Chat)"
        self.chats_list_widget.addItem(chat_name)
        self.chat_log[chat_name] = []
        self.switch_chat(chat_name)
        self.chat_input.setFocus()
        # Updated func #

    def rename_current_chat(self):
        """Rename the current chat."""
        current_item = self.chats_list_widget.currentItem()
        if current_item:
            dialog = self.create_rename_dialog(current_item.text())
            result = dialog.exec_()
            if result == QDialog.Accepted:
                new_name = dialog.new_name_input.text()
                if new_name:
                    self.rename_chat(current_item, new_name)
                    # UPDATED FUNC. VERY DIFFERENT #

    def create_rename_dialog(self, current_name):
        """Create a dialog to rename the chat."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Rename Chat")
        layout = QVBoxLayout()
        dialog.new_name_input = QLineEdit()
        dialog.new_name_input.setText(current_name)
        dialog.new_name_input.selectAll()
        layout.addWidget(dialog.new_name_input)
        confirm_button = QPushButton("Confirm")
        cancel_button = QPushButton("Cancel")
        layout.addWidget(confirm_button)
        layout.addWidget(cancel_button)
        dialog.setLayout(layout)
        confirm_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)
        return dialog
        # NEW FUNC!!! #

    def rename_chat(self, current_item, new_name):
        """Rename a chat in the chat log and update the UI."""
        old_name = current_item.text()
        current_item.setText(new_name)
        self.chat_log[new_name] = self.chat_log.pop(old_name, [])
        self.switch_chat(new_name)
        self.update_chat_log_file(old_name, new_name)
        # NEW FUNC!!! #

    def update_chat_log_file(self, old_name, new_name):
        """Update the chat log file to reflect the new chat name."""
        old_chat_log_path = os.path.join(self.CHAT_LOG_DIR, f"{old_name}.json")
        new_chat_log_path = os.path.join(self.CHAT_LOG_DIR, f"{new_name}.json")
        try:
            with open(old_chat_log_path, "r") as f:
                old_chat_log = json.load(f)
                with open(new_chat_log_path, "w") as f:
                    json.dump(old_chat_log, f)
            if os.path.exists(old_chat_log_path):
                os.remove(old_chat_log_path)
        except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
            print(f"Error updating chat log file: {e}")
        # NEW FUNC!!! #

    def switch_chat(self, chat_name, update_ui=True):
        """Switch to a different chat."""
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
        # Updated func #

    def cycle_through_chats(self):
        """Cycle through chats using Ctrl+B."""
        current_row = self.chats_list_widget.currentRow()
        next_row = (current_row + 1) % self.chats_list_widget.count()
        self.chats_list_widget.setCurrentRow(next_row)
        new_item = self.chats_list_widget.item(next_row)
        self.switch_chat(new_item.text())
        # Updated func #

    def adjust_input_size(self):
        """Adjust the input text edit size based on content."""
        doc_height = self.chat_input.document().size().toSize().height()
        self.chat_input.setFixedHeight(doc_height + 20)
        max_height = 150
        if self.chat_input.height() > max_height:
            self.chat_input.setFixedHeight(max_height)
        # Updated func #

    def update_ui(self, message, sender, url=""):
        """Update the UI with a new message."""
        cursor = self.chat_log_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        frame_format = self.create_frame_format(sender)
        cursor.insertFrame(frame_format)

        html_message = markdown.markdown(message)
        char_format = QTextCharFormat()
        char_format.setFontPointSize(10)
        char_format.setFontWeight(QFont.Bold)
        prefix = "<b>Me:</b>" if sender == "user" else "<b>Opal:</b>"
        cursor.insertHtml(prefix + html_message)

        if url:
            self.insert_url(cursor, url)

        cursor.movePosition(QTextCursor.End)
        self.chat_log_display.setTextCursor(cursor)
        self.chat_log_display.verticalScrollBar().setValue(
            self.chat_log_display.verticalScrollBar().maximum()
        )
        # Updated func #

    def create_frame_format(self, sender):
        """Create the frame format for a message."""
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
        return frame_format
        # NEW FUNC!!! #

    def insert_url(self, cursor, url):
        """Insert a URL into the chat log."""
        url_format = QTextCharFormat()
        url_format.setFontPointSize(10)
        url_format.setFontWeight(QFont.Bold)
        url_format.setUnderlineStyle(QTextCharFormat.SingleUnderline)
        url_format.setAnchor(True)
        url_format.setAnchorHref(url)
        url_format.setForeground(QColor.fromRgb(0, 0, 255))
        cursor.insertText(" (URL: ", url_format)
        cursor.insertText(url, url_format)
        cursor.insertText(")", url_format)
        # NEW FUNC!!! #

    def show_chat_context_menu(self, position):
        """Show the context menu for a chat."""
        context_menu = QMenu()
        rename_chat_action = QAction("Rename chat", self)
        context_menu.addAction(rename_chat_action)
        rename_chat_action.triggered.connect(self.rename_current_chat)
        delete_chat_action = QAction("Delete chat", self)
        context_menu.addAction(delete_chat_action)
        delete_chat_action.triggered.connect(self.delete_current_chat)
        context_menu.exec_(self.chats_list_widget.mapToGlobal(position))
        # NEW FUNC!!! #

    def delete_current_chat(self):
        """Delete the current chat."""
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
        # Updated func #

    def load_chat_history(self):
        """Load chat history from files."""
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
        # Updated func #

    def save_chat_history(self, chat, new_message):
        """Save the chat history to a file."""
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
        # Updated func #

    def showEvent(self, event):
        """Override showEvent to center the window."""
        screen = self.screen()
        screen_geometry = screen.availableGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)
        self.chat_input.setFocus()
        # Updated func #

    def closeEvent(self, event):
        """Override closeEvent to handle chat log cleanup."""
        if self.current_chat == "(New Chat)":
            file_path = os.path.join(self.CHAT_LOG_DIR, f"{self.current_chat}.json")
            if os.path.exists(file_path):
                os.remove(file_path)
        event.accept()
        # Updated func #
