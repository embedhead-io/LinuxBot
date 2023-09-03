import os
from dotenv import load_dotenv

load_dotenv()


# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# OpenAI Model
OPENAI_MODELS = [
    "gpt-4-0613",
    "gpt-3.5-turbo-16k-0613",
]
FAST_MODEL = "gpt-3.5-turbo-16k-0613"
SLOW_MODEL = "gpt-4-0613"
DEFAULT_MODEL = SLOW_MODEL

# OpenAI Configurations
OPENAI_RETRY_LIMIT = 3
OPENAI_TEMPERATURE = 0.8

# Chat Log Path
CHAT_LOG_PATH = "chat_history.json"
