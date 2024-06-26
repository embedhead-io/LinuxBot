## utils.py
import logging
import openai
import random
import time

from config import (
    ERROR_MESSAGE,
)
from llm import (
    DEFAULT_MODEL,
    OPENAI_RETRY_LIMIT,
    OPENAI_SYSTEM_INSTRUCTIONS,
    OPENAI_SYSTEM_MESSAGE,
    OPENAI_TEMPERATURE,
)

logging.basicConfig(level=logging.DEBUG)

client = openai.OpenAI()


# Utility functions to work with data and handle retries
def handle_retry(
    retries: int, base_delay: float, max_delay: float, jitter: float
) -> int:
    """
    Handle retry mechanism with exponential backoff and jitter.

    Parameters:
    retries (int): The current number of retries.
    base_delay (float): The base delay in seconds.
    max_delay (float): The maximum delay in seconds.
    jitter (float): The jitter value to add randomness to the delay.

    Returns:
    int: The incremented retry count.
    """
    retries += 1
    delay = base_delay * (2**retries) + jitter * random.random()
    delay = min(delay, max_delay)
    time.sleep(delay)
    return retries


# Functions to interact with OpenAI's API for generating responses
def ask_llm(chat_log: list):
    """
    Generate a response using either the OpenAI API or the Replicate API based on the user's message.

    Parameters:
    chat_log (list): The chat log containing the conversation history.

    Returns:
    tuple: The response message and a URL if applicable.
    """
    ans = None
    url = None

    retries = 0
    base_delay = 2
    max_delay = 10
    jitter = 0.5

    while ans is None and retries < OPENAI_RETRY_LIMIT:
        try:
            ans, url = generate_text(chat_log)
        except openai.APIConnectionError as e:
            logging.error(f"OpenAI API error: {e}")
            retries = handle_retry(retries, base_delay, max_delay, jitter)
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            break

    if ans is None:
        ans = ERROR_MESSAGE

    return ans.strip(), url


def generate_text(chat_log: list):
    """
    Generate a text response using the OpenAI API.

    Parameters:
    chat_log (list): The chat log containing the conversation history.

    Returns:
    tuple: The generated response message and None (since no URL is generated in this function).
    """
    res = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=chat_log,
        temperature=OPENAI_TEMPERATURE,
    )
    ans = res.choices[0].message.content.strip()
    return ans, None


# Functions to work with the chat log
def trim_chat_log(chat_log: list, max_length: int = 100):
    """
    Trim the chat log to a maximum length.

    Parameters:
    chat_log (list): The chat log to trim.
    max_length (int, optional): The maximum length of the chat log. Defaults to 10.

    Returns:
    list: The trimmed chat log.
    """
    if len(chat_log) > max_length:
        chat_log = chat_log[-max_length:]
    return chat_log


def append_to_chat_log(role: str, content: str, chat_log: list = []) -> list:
    """
    Appends a message to the chat log.

    Parameters:
    role (str): The role (user or assistant) of the message sender.
    content (str): The content of the message to append.
    chat_log (list, optional): The chat log to append the message to. Defaults to None.

    Returns:
    list: The updated chat log with the new message appended.
    """
    chat_log.append({"role": role, "content": content})
    return chat_log


def process_message(user_message: str, chat_log: list = []):
    """
    Process the user's message and return a response.

    Parameters:
    user_message (str): The message from the user.
    chat_log (list, optional): The chat log containing the conversation history. Defaults to None.

    Returns:
    tuple: The response message, a URL if applicable, and the updated chat log.
    """
    # If the chat log is an empty list, set chat_log[0] equal to the OPENAI_SYSTEM_MESSAGE.
    if len(chat_log) == 0:
        chat_log.append(OPENAI_SYSTEM_MESSAGE)

    # Append the user's message to the chat log
    chat_log = append_to_chat_log("user", user_message, chat_log)

    # If the user's message begins with "?", set chat_log[0] equal to the OPENAI_SYSTEM_INSTRUCTIONS. Otherwise, default to OPENAI_SYSTEM_MESSAGE.
    if user_message.startswith("?"):
        chat_log[0] = OPENAI_SYSTEM_INSTRUCTIONS
    elif user_message.startswith("!"):
        chat_log[0] = OPENAI_COMEDY_SYSTEM_MESSAGE
    else:
        chat_log[0] = OPENAI_SYSTEM_MESSAGE

    # Generate a response
    ans, url = ask_llm(chat_log)

    # Append the response to the chat log
    chat_log = append_to_chat_log("assistant", ans, chat_log)

    # Trim the chat log
    chat_log = trim_chat_log(chat_log)

    return ans, url, chat_log
