from google import genai
from google.genai import types

from backend.voice.config import (
    GEMINI_API_KEY,
    VOICE_MODEL,
    VOICE_SYSTEM_INSTRUCTION,
)


def create_live_client():
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    return genai.Client(
        api_key=GEMINI_API_KEY
    )


def get_live_connection():
    client = create_live_client()

    return client.aio.live.connect(
        model=VOICE_MODEL,
        config={
            "response_modalities": ["AUDIO"],
            "input_audio_transcription": (
                types.AudioTranscriptionConfig(
                    language_codes=[]
                )
            ),
            "system_instruction": VOICE_SYSTEM_INSTRUCTION,
        },
    )