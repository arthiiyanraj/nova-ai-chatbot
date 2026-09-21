import os

from dotenv import load_dotenv


load_dotenv()


LLM_MODEL = os.getenv(
    "LLM_MODEL",
    "qwen3:1.7b"
)