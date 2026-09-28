import os

from dotenv import load_dotenv


load_dotenv()


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

VOICE_MODEL = os.getenv(
    "GEMINI_LIVE_MODEL",
    "gemini-2.5-flash-native-audio-preview-12-2025",
)

INPUT_SAMPLE_RATE = 16000
OUTPUT_SAMPLE_RATE = 24000

AUDIO_CHANNELS = 1
AUDIO_SAMPLE_WIDTH = 2

VOICE_SYSTEM_INSTRUCTION = """
You are NOVA AI, a friendly general-purpose AI assistant.

For voice conversations:
- Understand the user's spoken language automatically.
- Reply in the same language the user is speaking whenever possible.
- Support multilingual conversations naturally.
- Keep responses conversational and clear.
- Do not invent information.
- Be friendly and helpful.
"""