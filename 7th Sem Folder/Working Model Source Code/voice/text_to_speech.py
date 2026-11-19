"""
Wraps pyttsx3 (Windows SAPI5). Loads the engine once and exposes
a single speak() function. Nothing else in the codebase should
import pyttsx3 directly — everyone goes through this module.
"""

import pyttsx3

from config.settings import TTS_RATE, TTS_VOLUME, TTS_VOICE_ID
from utils.logger import get_logger

logger = get_logger(__name__)

_engine = None  # lazy-loaded singleton


def load_engine():
    """
    Initializes the TTS engine once and caches it.
    Re-initializing per-call is a known source of hangs/silent
    failures on Windows, so we avoid that.
    """
    global _engine
    if _engine is None:
        logger.info("Initializing TTS engine...")
        _engine = pyttsx3.init()
        _engine.setProperty("rate", TTS_RATE)
        _engine.setProperty("volume", TTS_VOLUME)

        if TTS_VOICE_ID is not None:
            _engine.setProperty("voice", TTS_VOICE_ID)

    return _engine


def list_voices() -> None:
    """Prints available system voices with their IDs, for config purposes."""
    engine = load_engine()
    voices = engine.getProperty("voices")
    print("\nAvailable voices:")
    for v in voices:
        print(f"  ID: {v.id}")
        print(f"      Name: {v.name}, Languages: {v.languages}")


def speak(text: str) -> None:
    """
    Speaks the given text out loud. Blocks until speech finishes,
    which is fine for now since the assistant is single-threaded —
    we'll revisit this if Phase 8's background loop needs non-blocking speech.
    """
    if not text:
        return

    logger.info(f"Speaking: '{text}'")
    engine = load_engine()
    engine.say(text)
    engine.runAndWait()