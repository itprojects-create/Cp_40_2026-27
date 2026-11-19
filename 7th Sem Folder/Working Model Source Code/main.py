"""
Final version: always-listening loop with error resilience and
graceful shutdown.

Design note: a single try/except wraps each full command cycle
(wake word -> transcribe -> route -> speak). This means one failing
command (bad transcription, a controller exception, a timed-out
browser action) logs the error and speaks an apology, then returns
to listening — it does NOT crash the whole assistant. That's the
core reliability requirement for something meant to run continuously.
"""

from audio.microphone import record_audio
from audio.speech_to_text import load_model, transcribe
from audio.wake_word import WakeWordListener
from voice.text_to_speech import speak
from brain.intent_parser import parse_intent
from brain.command_router import route_command
from brain.context_manager import AssistantContext
from automation.browser.browser_controller import shutdown_browser
from config.settings import COMMAND_RECORD_SECONDS
from utils.logger import get_logger

logger = get_logger(__name__)


def run_command_cycle(context: AssistantContext) -> None:
    """
    One full cycle: record command -> transcribe -> parse -> route -> speak.
    Any exception here is caught so a single bad command can't kill
    the assistant.
    """
    audio = record_audio(COMMAND_RECORD_SECONDS)
    text = transcribe(audio)
    print(f"You said: \"{text}\"")

    parsed = parse_intent(text)
    print(f"Parsed: {parsed}")

    response = route_command(parsed, context)
    print(f"Assistant: {response}")
    speak(response)

    print(f"Context: {context.get_current_context()}")


def main():
    print("Starting Windows Voice Assistant...")
    load_model()
    context = AssistantContext()
    wake_listener = WakeWordListener()

    speak("Voice assistant ready.")
    logger.info("Assistant fully initialized. Entering main loop.")

    try:
        while True:
            wake_listener.listen_for_wake_word()
            speak("Yes?")

            try:
                run_command_cycle(context)
            except Exception as e:
                # Catches anything a controller/parser/STT call might raise
                # (Playwright timeouts, psutil access errors, etc.) so a
                # single bad command doesn't take down the whole assistant.
                logger.error(f"Error during command cycle: {e}", exc_info=True)
                speak("Sorry, something went wrong with that command.")

    except KeyboardInterrupt:
        print("\nShutdown requested.")
        logger.info("Shutdown requested via KeyboardInterrupt.")

    finally:
        speak("Goodbye.")
        wake_listener.close()
        shutdown_browser()
        logger.info("All resources released. Assistant stopped cleanly.")


if __name__ == "__main__":
    main()