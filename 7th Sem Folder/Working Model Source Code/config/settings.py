"""
Central configuration. Every module reads settings from here
instead of hardcoding values, so later phases (wake word, model size,
etc.) are one-line changes.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Audio settings
SAMPLE_RATE = 16000          # Whisper expects 16kHz mono
CHANNELS = 1
RECORD_SECONDS_TEST = 3      # used only by Phase 1's mic test

# Logging
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "assistant.log"
# --- Whisper / STT settings ---
# Options: "tiny.en", "base.en", "small.en", "medium.en"
# .en variants are English-only: faster and more accurate than
# multilingual models when you don't need multilingual support.
WHISPER_MODEL_SIZE = "base.en"

# "cpu" or "cuda" (only use "cuda" if you have an NVIDIA GPU + CUDA installed)
WHISPER_DEVICE = "cpu"

# "int8" is fastest on CPU with minimal accuracy loss.
# Use "float16" if WHISPER_DEVICE = "cuda".
WHISPER_COMPUTE_TYPE = "int8"

# How long to record when the user is speaking a command.
# We'll replace this fixed window with silence-detection (VAD) in a later phase.
COMMAND_RECORD_SECONDS = 4

# --- Text-to-Speech settings ---
TTS_RATE = 180        # words per minute; default is usually ~200, slightly slower reads clearer
TTS_VOLUME = 1.0      # 0.0 to 1.0
# Leave as None to use the system default voice.
# We'll print available voice IDs in test_tts.py so you can pick one.
TTS_VOICE_ID = None

# --- Application paths ---
# Windows can usually resolve these by name via `start`, but Chrome/VS Code
# sometimes need explicit paths depending on install method. Adjust if needed.
APP_COMMANDS = {
    "chrome": "chrome",
    "vscode": "code",
    "notepad": "notepad",
    "explorer": "explorer",
}

# --- Screenshot settings ---
SCREENSHOT_DIR = BASE_DIR / "screenshots"

# --- Volume settings ---
VOLUME_STEP = 0.10   # 10% per "increase/decrease volume" command

# --- Browser automation settings ---
CHROME_DEBUG_PORT = 9222
# Dedicated, persistent profile just for the assistant — keeps logins
# between runs without conflicting with your everyday Chrome instance.
CHROME_PROFILE_DIR = BASE_DIR / "chrome_profile"

SUPPORTED_WEBSITES = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
}

# --- YouTube settings ---
YOUTUBE_SEARCH_URL = "https://www.youtube.com/results?search_query={query}"
# Selector for a video result thumbnail link on the search results page.
YOUTUBE_FIRST_RESULT_SELECTOR = "ytd-video-renderer a#video-title"

# --- Wake word settings (openWakeWord) ---
WAKE_WORD_MODEL_NAME = "hey_jarvis"   # pre-trained model bundled with openwakeword
WAKE_WORD_THRESHOLD = 0.5              # 0.0-1.0, higher = fewer false positives