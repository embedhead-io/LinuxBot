from .openai_integration import ask_llm
from .config import OPENAI_SYSTEM_MESSAGE, OPENAI_SYSTEM_INSTRUCTIONS


def process_message(user_message, chat_log):
    """
    Processes a user message by interacting with the OpenAI API and updating the chat log.

    Args:
        user_message (str): The message from the user.
        chat_log (list): The current chat log.

    Returns:
        tuple: A tuple containing the assistant's response (str), a URL (if any), and the updated chat log (list).
    """
    if not isinstance(chat_log, list):
        raise ValueError("chat_log must be a list")

    if not chat_log:
        chat_log.append(OPENAI_SYSTEM_MESSAGE)

    chat_log.append({"role": "user", "content": user_message})

    # Set the system instructions based on the user message
    if user_message.startswith("?"):
        chat_log[0] = OPENAI_SYSTEM_INSTRUCTIONS
    else:
        chat_log[0] = OPENAI_SYSTEM_MESSAGE

    # Get the response from the OpenAI API
    ans, url = ask_llm(chat_log)

    # Append the assistant's response to the chat log
    chat_log.append({"role": "assistant", "content": ans})

    return ans, url, chat_log
