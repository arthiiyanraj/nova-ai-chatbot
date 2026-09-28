from backend.answer_engine import generate_answer

from backend.voice.service import (
    transcribe_audio,
    generate_voice_response,
)


async def process_voice(
    pcm_data: bytes,
    user_id,
    chat_messages,
    active_pdf_id=None,
    output_file="nova_voice_response.wav",
):
    """
    Complete NOVA voice pipeline.

    Audio
        ↓
    Speech-to-Text
        ↓
    NOVA Answer Engine
        ↓
    Text-to-Speech
        ↓
    Voice Audio
    """

    # 1. Speech-to-Text
    transcript = await transcribe_audio(
        pcm_data
    )

    transcript = transcript.strip()

    if not transcript:
        return {
            "transcript": "",
            "answer": (
                "I couldn't understand the audio. "
                "Please try again."
            ),
            "route": "GENERAL",
            "web_sources": [],
            "audio_file": None,
        }

    # 2. Existing NOVA Answer Engine
    result = generate_answer(
        question=transcript,
        user_id=user_id,
        chat_messages=chat_messages,
        active_pdf_id=active_pdf_id,
    )

    answer = result["answer"]

    # 3. Text-to-Speech
    audio_file = await generate_voice_response(
        answer,
        output_file,
    )

    # 4. Return complete result
    return {
        "transcript": transcript,
        "answer": answer,
        "route": result["route"],
        "web_sources": result["web_sources"],
        "audio_file": audio_file,
    }