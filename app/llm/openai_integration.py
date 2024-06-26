from openai import OpenAI

import logging
import time
import random
from .config import (
    DEFAULT_MODEL,
    OPENAI_API_KEY,
    OPENAI_BASE_DELAY,
    OPENAI_JITTER,
    OPENAI_RETRY_LIMIT,
)

# Configure the OpenAI client with the API key
client = OpenAI(api_key=OPENAI_API_KEY)


def ask_llm(chat_log):
    """Function to interact with the OpenAI API, with retry logic for error handling."""
    ans, url = None, None
    retries = 0
    base_delay = OPENAI_BASE_DELAY
    jitter = OPENAI_JITTER

    while ans is None and retries < OPENAI_RETRY_LIMIT:
        try:
            ans, url = generate_text(chat_log)
        except openai.APIConnectionError as e:
            logging.error(f"OpenAI API error: {e}")
            retries += 1
            time.sleep(base_delay * (2**retries) + jitter * random.random())
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            break

    if ans is None:
        ans = "ERROR_MESSAGE"

    return ans.strip(), url


def generate_text(chat_log):
    """Generate a response from the OpenAI API based on the given chat log."""
    res = client.chat.completions.create(model=DEFAULT_MODEL, messages=chat_log)
    ans = res.choices[0].message.content.strip()
    return ans, None
