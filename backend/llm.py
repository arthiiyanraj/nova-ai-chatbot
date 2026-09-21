import os
import time

from dotenv import load_dotenv

from langchain_core.language_models.llms import LLM
from langchain_ollama import ChatOllama

from google import genai
from google.genai import errors


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
            "gemini-3.1-flash-lite",
        )

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not configured."
            )

        client = genai.Client(
            api_key=api_key
        )

        max_retries = 3

        for attempt in range(max_retries):

            try:

                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                )

                if not response.text:
                    raise ValueError(
                        "Gemini returned an empty response."
                    )

                return response.text

            except errors.ServerError as error:

                if attempt == max_retries - 1:
                    raise RuntimeError(
                        "Gemini server is temporarily unavailable. "
                        "Please try again later."
                    ) from error

                wait_seconds = 2 ** attempt
                time.sleep(wait_seconds)

            except errors.ClientError as error:

                error_text = str(error)

                if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:

                    raise RuntimeError(
                        "Gemini API quota has been exceeded. "
                        "Please wait for the quota to reset "
                        "or use a model with available quota."
                    ) from error

                raise RuntimeError(
                    "Gemini API request failed. "
                    "Please check the API key, model, "
                    "and API settings."
                ) from error

            except Exception as error:

                raise RuntimeError(
                    f"Gemini request failed: {error}"
                ) from error


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