import os
from dotenv import load_dotenv

load_dotenv()


# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# OpenAI Model
OPENAI_MODEL = "gpt-4-0613"

# OpenAI Configurations
OPENAI_RETRY_LIMIT = 3
OPENAI_TEMPERATURE = 0.8
