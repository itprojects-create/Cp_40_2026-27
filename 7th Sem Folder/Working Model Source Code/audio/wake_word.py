"""
Continuous wake-word listening via openWakeWord.

Fully local, no account/API key needed — this replaced an earlier
Porcupine-based version specifically to remove that external
dependency. Same responsibility as before: answer "was the wake
word said, yes/no" only. Whisper is never invoked until this
returns a hit, keeping the idle loop lightweight.
"""

import numpy as np
import pyaudio
from openwakeword.model import Model

from config.settings import WAKE_WORD_MODEL_NAME, WAKE_WORD_THRESHOLD
from utils.logger import get_logger

logger = get_logger(__name__)

FRAME_LENGTH = 1280   # openWakeWord expects 80ms chunks at 16kHz


class WakeWordListener:
    def __init__(self):
        self._model = Model(
            wakeword_models=[WAKE_WORD_MODEL_NAME],
            inference_framework="onnx",
        )
        self._pa = pyaudio.PyAudio()
        self._stream = self._pa.open(
            rate=16000,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=FRAME_LENGTH,
        )
        logger.info(f"Wake word listener initialized (model: {WAKE_WORD_MODEL_NAME}).")

    def listen_for_wake_word(self) -> None:
        """
        Blocks until the wake word is detected, then returns.
        Intended to be called in a loop from main.py.
        """
        logger.info("Listening for wake word...")
        while True:
            pcm_bytes = self._stream.read(FRAME_LENGTH, exception_on_overflow=False)
            pcm = np.frombuffer(pcm_bytes, dtype=np.int16)

            prediction = self._model.predict(pcm)
            score = prediction[WAKE_WORD_MODEL_NAME]

            if score > WAKE_WORD_THRESHOLD:
                logger.info(f"Wake word detected! (score: {score:.2f})")
                return

    def close(self) -> None:
        """Releases mic stream resources. Call on shutdown."""
        if self._stream is not None:
            self._stream.stop_stream()
            self._stream.close()
        if self._pa is not None:
            self._pa.terminate()
        logger.info("Wake word listener resources released.")