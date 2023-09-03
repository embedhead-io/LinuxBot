import os
import openai

from config import (
    OPENAI_MODEL,
    OPENAI_TEMPERATURE,
)


def initialize_openai(api_key):
    if not api_key:
        raise ValueError("API key for OpenAI is not set.")
    openai.api_key = api_key


def generate_text(chat_log: list):
    try:
        res = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=chat_log,
            temperature=OPENAI_TEMPERATURE,
        )
        ans = res.choices[0].message.content.strip()
        return ans, None
    except Exception as e:
        return None, str(e)


def append_to_chat_log(role: str, content: str, chat_log: list = []):
    chat_log.append(
        {
            "role": role,
            "content": content,
        }
    )
    return chat_log


def bot(user_message: str, chat_log: list = []):
    if chat_log is None:
        chat_log = []

    chat_log = append_to_chat_log(
        role="user",
        content=user_message,
        chat_log=chat_log,
    )

    ans, err = generate_text(chat_log)
    if err:
        return err

    chat_log = append_to_chat_log(
        role="assistant",
        content=ans,
        chat_log=chat_log,
    )
    return ans


# Initialize OpenAI API key
initialize_openai(os.environ.get('OPENAI_API_KEY'))