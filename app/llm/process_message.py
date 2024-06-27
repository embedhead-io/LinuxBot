from .openai_integration import ask_llm
from .config import DEFAULT_MODEL, OPENAI_SYSTEM_MESSAGE, OPENAI_SYSTEM_INSTRUCTIONS


def process_message(user_message, chat_log, model=DEFAULT_MODEL):
    if not chat_log:
        chat_log.append(OPENAI_SYSTEM_MESSAGE)

    chat_log.append({"role": "user", "content": user_message})

    if user_message.startswith("?"):
        chat_log[0] = OPENAI_SYSTEM_INSTRUCTIONS
    else:
        chat_log[0] = OPENAI_SYSTEM_MESSAGE

    ans, url, model_used = ask_llm(chat_log, model)

    chat_log.append({"role": "assistant", "content": ans})

    return ans, url, chat_log, model_used
