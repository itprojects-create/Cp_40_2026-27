"""
Thin wrapper around sounddevice for recording audio.
Kept separate from speech_to_text.py so the recording mechanism
can change later (e.g. streaming/VAD-based) without touching STT code.
"""

import sounddevice as sd
import numpy as np
from config.settings import SAMPLE_RATE, CHANNELS
from utils.logger import get_logger

logger = get_logger(__name__)


def list_input_devices() -> None:
    """Prints all available audio input devices with their index."""
    devices = sd.query_devices()
    print("\nAvailable input devices:")
    for i, device in enumerate(devices):
        if device["max_input_channels"] > 0:
            print(f"  [{i}] {device['name']}")


def record_audio(duration_seconds: float) -> np.ndarray:
    """
    Records audio from the default microphone for a fixed duration.
    Returns a NumPy array of float32 samples, mono, at SAMPLE_RATE.
    """
    logger.info(f"Recording for {duration_seconds} seconds...")
    audio = sd.rec(
        int(duration_seconds * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="float32",
    )
    sd.wait()  # block until recording finishes
    logger.info("Recording finished.")
    return audio.flatten()