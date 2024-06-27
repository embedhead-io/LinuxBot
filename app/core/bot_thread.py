import logging
from PyQt5.QtCore import QThread, pyqtSignal
from app.llm.process_message import process_message

logging.basicConfig(level=logging.DEBUG)


class BotThread(QThread):
    new_message = pyqtSignal(str, str, str, str)

    def __init__(self, user_message: str, chat_log: dict, selected_model: str):
        super().__init__()
        self.user_message = user_message
        self.chat_log = chat_log
        self.selected_model = selected_model

    def run(self):
        try:
            (
                response_message,
                url,
                self.chat_log,
                model_used,
                response_json,
            ) = process_message(self.user_message, self.chat_log, self.selected_model)
            print(f"Model used: {model_used}")  # Print the model used in the terminal
            print(f"Response JSON: {response_json}")  # Print the full response JSON
            self.new_message.emit(response_message, "assistant", "", url if url else "")
        except Exception as e:
            logging.error(f"Error generating response: {e}")
