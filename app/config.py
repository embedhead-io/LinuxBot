import os
from dotenv import load_dotenv

load_dotenv()


# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# OpenAI Model
OPENAI_MODELS = [
    "gpt-4-0613",
    "gpt-4",
    "gpt-3.5-turbo-16k-0613",
    "gpt-3.5-turbo-16k",
]
OPENAI_MODEL = OPENAI_MODELS[0]

# OpenAI Configurations
OPENAI_RETRY_LIMIT = 3
OPENAI_TEMPERATURE = 0.7
