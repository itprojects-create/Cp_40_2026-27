"""
Phase 1 verification script.
Run this directly to confirm:
  1. Python can see your microphone
  2. Recording works
  3. The recorded audio is saved and non-silent
"""

import sys
from pathlib import Path

# allow running this file directly from the tests/ folder
sys.path.append(str(Path(__file__).resolve().parent.parent))

import numpy as np
import soundfile as sf

from audio.microphone import list_input_devices, record_audio
from config.settings import SAMPLE_RATE, RECORD_SECONDS_TEST, BASE_DIR


def main():
    list_input_devices()

    print(f"\nSpeak into your microphone for {RECORD_SECONDS_TEST} seconds...")
    audio = record_audio(RECORD_SECONDS_TEST)

    # Basic sanity check: is the audio actually capturing sound,
    # or is it silent (which usually means wrong device / permissions issue)?
    volume = np.abs(audio).mean()
    print(f"\nAverage volume level: {volume:.5f}")
    if volume < 0.001:
        print("⚠️  Audio looks silent. Check mic permissions or default device.")
    else:
        print("✅ Microphone is capturing audio.")

    output_path = BASE_DIR / "test_recording.wav"
    sf.write(output_path, audio, SAMPLE_RATE)
    print(f"Saved test recording to: {output_path}")


if __name__ == "__main__":
    main()