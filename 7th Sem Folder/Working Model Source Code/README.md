# Windows Voice Assistant

A context-aware, locally-running voice assistant for Windows 11 — similar
in spirit to Siri, built with Python. Wake word activation, offline
speech-to-text (Whisper), offline text-to-speech, rule-based intent
parsing, and Windows/browser automation, with a context manager that
lets you give natural follow-up commands ("pause" after "play the first
video") instead of repeating yourself every time.

## Architecture
Microphone -> Wake Word (openWakeWord) -> Whisper STT -> Intent Parser
-> Context Manager -> Command Router -> Controllers -> Text-to-Speech


- **Wake word**: openWakeWord, fully local, no account required
- **Speech-to-text**: faster-whisper (`base.en`, CPU, int8) — local, no cloud calls
- **Text-to-speech**: pyttsx3 (Windows SAPI5) — local
- **Intent parsing**: rule-based regex matching, structured into
  `{intent, entity, confidence}` — swappable for an LLM/classifier later
  without touching the router or controllers
- **Context manager**: tracks current app/website/media state so
  follow-up commands ("pause", "next") resolve without restating context
- **Browser automation**: Playwright connected over CDP to a dedicated
  Chrome profile (not your everyday Chrome) — URL navigation for search,
  DOM interaction for finding/clicking results, native keyboard shortcuts
  for playback controls
- **Windows automation**: `psutil`/`subprocess` for apps, `pycaw` for
  precise system volume, `mss` for screenshots

## Setup

1. Python 3.11, then:
```powershell
   py -3.11 -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
```
2. Download wake word models (one-time):
```powershell
   python -c "import openwakeword; openwakeword.utils.download_models()"
```
3. Run:
```powershell
   python main.py
```
4. Say **"Hey Jarvis"**, then speak a command.

## Supported commands (examples)
Open/close apps, YouTube search + playback + follow-up commands, system
volume, screenshots, lock computer, Task Manager/Settings, time.

## Known limitations / next steps
- Intent parsing is rule-based (regex), not ML-based — documented as a
  deliberate v1 choice; architecture supports swapping in an LLM/Ollama
  later without rewriting the router.
- Only YouTube has a dedicated website controller; Spotify/other sites
  use OS-level media keys for now.
- No system tray icon or Windows-startup integration yet.