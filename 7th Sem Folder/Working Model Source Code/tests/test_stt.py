"""
Phase 2 verification script.
Records a voice command and prints the transcribed text,
along with timing so you can judge latency on your machine.
"""

import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from audio.microphone import record_audio
from audio.speech_to_text import load_model, transcribe
from config.settings import COMMAND_RECORD_SECONDS


def main():
    print("Warming up Whisper model (loading into memory)...")
    warm_start = time.time()
    load_model()
    print(f"Model ready in {time.time() - warm_start:.2f}s\n")

    input("Press Enter, then speak your command...")
    audio = record_audio(COMMAND_RECORD_SECONDS)

    print("Transcribing...")
    transcribe_start = time.time()
    text = transcribe(audio)
    transcribe_time = time.time() - transcribe_start

    print(f"\nYou said: \"{text}\"")
    print(f"Transcription time: {transcribe_time:.2f}s")


if __name__ == "__main__":
    main()