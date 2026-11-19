"""
Phase 3 verification script.
Lists available voices, then speaks a couple of test phrases.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from voice.text_to_speech import list_voices, speak


def main():
    list_voices()

    print("\nSpeaking test phrase 1...")
    speak("Hello, I am your Windows voice assistant.")

    print("Speaking test phrase 2...")
    speak("Opening Chrome.")

    print("Done.")


if __name__ == "__main__":
    main()