import os

from dotenv import load_dotenv
from langchain_core.language_models.llms import LLM
from langchain_ollama import ChatOllama
from google import genai

load_dotenv()


class GeminiLLM(LLM):

    @property
    def _llm_type(self):
        return "gemini"

    def _call(
        self,
        prompt,
        stop=None,
        run_manager=None,
        **kwargs,
    ):
        api_key = os.getenv("GEMINI_API_KEY")

        model = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.8-flash",
        )

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not configured."
            )

        client = genai.Client(
            api_key=api_key
        )

        response = client.models.generate_content(
            model=model,
            contents=prompt,
        )

        return response.text


def get_llm():

    provider = os.getenv(
        "LLM_PROVIDER",
        "gemini",
    ).lower()

    if provider == "local":
        return ChatOllama(
            model=os.getenv(
                "LLM_MODEL",
                "qwen3:1.7b",
            ),
            temperature=0.7,
        )

    if provider == "gemini":
        return GeminiLLM()

    raise ValueError(
        f"Unsupported LLM_PROVIDER: {provider}"
    )