import numpy as np
import sounddevice as sd
from scipy.signal import resample_poly


INPUT_SAMPLE_RATE = 44100
OUTPUT_SAMPLE_RATE = 16000

INPUT_CHANNELS = 2
OUTPUT_CHANNELS = 1

SAMPLE_WIDTH_BYTES = 2

MICROPHONE_DEVICE = 11


def capture_audio(
    duration_seconds: float = 3.0,
) -> np.ndarray:
    """
    Capture audio from the microphone.

    The microphone is captured using its supported
    2-channel input configuration.
    """

    audio = sd.rec(
        frames=int(
            duration_seconds * INPUT_SAMPLE_RATE
        ),
        samplerate=INPUT_SAMPLE_RATE,
        channels=INPUT_CHANNELS,
        dtype="int16",
        device=MICROPHONE_DEVICE,
    )

    sd.wait()

    # Convert stereo -> mono
    mono_audio = audio.mean(
        axis=1
    ).astype(np.int16)

    return mono_audio


def resample_audio(
    audio: np.ndarray,
    input_rate: int = INPUT_SAMPLE_RATE,
    output_rate: int = OUTPUT_SAMPLE_RATE,
) -> np.ndarray:
    """
    Convert microphone sample rate to
    Gemini's required 16 kHz format.
    """

    if audio.size == 0:
        return np.array(
            [],
            dtype=np.int16,
        )

    audio_float = audio.astype(
        np.float32
    )

    resampled = resample_poly(
        audio_float,
        output_rate,
        input_rate,
    )

    resampled = np.clip(
        resampled,
        -32768,
        32767,
    )

    return resampled.astype(
        np.int16
    )


def audio_to_pcm_bytes(
    audio: np.ndarray,
) -> bytes:
    """
    Convert int16 audio samples
    into raw PCM bytes.
    """

    return audio.astype(
        np.int16
    ).tobytes()