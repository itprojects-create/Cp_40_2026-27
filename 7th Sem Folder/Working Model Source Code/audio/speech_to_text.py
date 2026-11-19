"""
Wraps faster-whisper. Loads the model once (expensive) and exposes
a single transcribe() function that takes a NumPy audio array and
returns text. Nothing else in the codebase should import faster-whisper
directly — everyone goes through this module.
"""

import time
import numpy as np
from faster_whisper import WhisperModel

from config.settings import WHISPER_MODEL_SIZE, WHISPER_DEVICE, WHISPER_COMPUTE_TYPE
from utils.logger import get_logger

logger = get_logger(__name__)

_model = None  # lazy-loaded singleton


def load_model() -> WhisperModel:
    """
    Loads the Whisper model once and caches it in memory.
    Called automatically on first transcribe() call, but you can
    also call this explicitly at startup to "warm up" before
    the user speaks their first command (avoids a slow first request).
    """
    global _model
    if _model is None:
        logger.info(
            f"Loading Whisper model '{WHISPER_MODEL_SIZE}' "
            f"(device={WHISPER_DEVICE}, compute_type={WHISPER_COMPUTE_TYPE})..."
        )
        start = time.time()
        _model = WhisperModel(
            WHISPER_MODEL_SIZE,
            device=WHISPER_DEVICE,
            compute_type=WHISPER_COMPUTE_TYPE,
        )
        logger.info(f"Model loaded in {time.time() - start:.2f}s")
    return _model


def transcribe(audio: np.ndarray) -> str:
    """
    Transcribes a NumPy float32 mono audio array (16kHz) into text.
    Returns an empty string if nothing intelligible was detected.
    """
    model = load_model()

    start = time.time()
    segments, info = model.transcribe(
        audio,
        language="en",
        beam_size=5,
        vad_filter=True,  # skips silent stretches inside the clip
    )

    text_parts = [segment.text.strip() for segment in segments]
    text = " ".join(text_parts).strip()

    elapsed = time.time() - start
    logger.info(f"Transcription took {elapsed:.2f}s -> '{text}'")

    return text