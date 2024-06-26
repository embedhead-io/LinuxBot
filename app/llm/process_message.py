from .openai_integration import ask_llm
from .config import OPENAI_SYSTEM_MESSAGE, OPENAI_SYSTEM_INSTRUCTIONS


def process_message(user_message, chat_log):
    if not chat_log:
        chat_log.append(OPENAI_SYSTEM_MESSAGE)

    chat_log.append({"role": "user", "content": user_message})

    if user_message.startswith("?"):
        chat_log[0] = OPENAI_SYSTEM_INSTRUCTIONS
    else:
        chat_log[0] = OPENAI_SYSTEM_MESSAGE

    ans, url = ask_llm(chat_log)

    chat_log.append({"role": "assistant", "content": ans})

    return ans, url, chat_log
