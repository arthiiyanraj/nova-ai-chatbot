import asyncio
import wave

from google.genai import types

from backend.voice.config import VOICE_MODEL
from backend.voice.live_client import create_live_client


async def transcribe_audio(pcm_data: bytes) -> str:
    """
    Send PCM audio to Gemini Live
    and return the complete user transcript.
    """

    client = create_live_client()

    try:
        config = {
            "response_modalities": ["AUDIO"],
            "input_audio_transcription": {},
        }

        async with client.aio.live.connect(
            model=VOICE_MODEL,
            config=config,
        ) as session:

            await session.send_realtime_input(
                audio=types.Blob(
                    data=pcm_data,
                    mime_type="audio/pcm;rate=16000",
                )
            )

            transcript_parts = []

            async for response in session.receive():

                if not response.server_content:
                    continue

                content = response.server_content

                if content.input_transcription:
                    transcript_parts.append(
                        content.input_transcription.text
                    )

                if content.turn_complete:
                    break

            return "".join(transcript_parts).strip()

    finally:
        client.close()


async def generate_voice_response(
    text: str,
    output_file: str = "nova_voice_response.wav",
):
    """
    Send text to Gemini Live
    and save the generated voice response.
    """

    client = create_live_client()

    try:
        config = {
            "response_modalities": ["AUDIO"],
            "system_instruction": (
                "You are NOVA AI, a friendly general-purpose AI assistant. "
                "Reply naturally and conversationally. "
                "Reply in the same language as the user's question whenever possible."
            ),
        }

        async with client.aio.live.connect(
            model=VOICE_MODEL,
            config=config,
        ) as session:

            await session.send_client_content(
                turns=[
                    types.Content(
                        role="user",
                        parts=[
                            types.Part(text=text)
                        ],
                    )
                ],
                turn_complete=True,
            )

            audio_chunks = []

            async for response in session.receive():

                if not response.server_content:
                    continue

                content = response.server_content

                if content.model_turn:

                    for part in content.model_turn.parts:

                        if part.inline_data:

                            audio_chunks.append(
                                part.inline_data.data
                            )

                if content.turn_complete:
                    break

            if not audio_chunks:
                raise RuntimeError(
                    "Gemini did not return any audio."
                )

            audio_data = b"".join(audio_chunks)

            with wave.open(
                output_file,
                "wb",
            ) as wav_file:

                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(24000)
                wav_file.writeframes(audio_data)

            return output_file

    finally:
        client.close()