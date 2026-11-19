"""
Takes a parsed intent + the current AssistantContext, decides what to
execute, calls the right controller, updates context, and returns a
spoken response.

This is the ONLY place that knows how intents map to controller calls.
Controllers themselves stay dumb/reusable; the router owns the decisions.
"""

from automation.app_controller import open_app, close_app
from automation.system_controller import (
    get_current_time, lock_computer, open_settings, open_task_manager,
)
from automation.screenshot_controller import take_screenshot
from automation.volume_controller import volume_up, volume_down, mute, unmute
from brain.context_manager import AssistantContext
from utils.logger import get_logger
from automation.browser.browser_controller import open_website
from automation.browser import youtube_controller

logger = get_logger(__name__)


def route_command(parsed: dict, context: AssistantContext) -> str:
    intent = parsed["intent"]
    entity = parsed["entity"]

    context.set_last_intent(intent)

    if intent == "OPEN_APPLICATION":
        if not entity:
            return "Which application would you like me to open?"
        success = open_app(entity)
        if success:
            context.set_application(entity)
            return f"Opening {entity}."
        return f"I couldn't open {entity}."

    if intent == "CLOSE_APPLICATION":
        if not entity:
            return "Which application would you like me to close?"
        success = close_app(entity)
        if success and context.current_application == entity:
            context.set_application(None)
        return f"Closing {entity}." if success else f"{entity} doesn't seem to be running."

    if intent == "GET_TIME":
        return get_current_time()

    if intent == "SCREENSHOT":
        take_screenshot()
        return "Screenshot taken."

    if intent == "VOLUME_UP":
        new_level = volume_up()
        return f"Volume increased to {new_level} percent."

    if intent == "VOLUME_DOWN":
        new_level = volume_down()
        return f"Volume decreased to {new_level} percent."

    if intent == "MUTE":
        mute()
        return "Muted."

    if intent == "UNMUTE":
        unmute()
        return "Unmuted."

    if intent == "LOCK_COMPUTER":
        lock_computer()
        return "Locking the computer."

    if intent == "OPEN_SETTINGS":
        open_settings()
        return "Opening Settings."

    if intent == "OPEN_TASK_MANAGER":
        open_task_manager()
        return "Opening Task Manager."

    if intent == "OPEN_WEBSITE":
        if not entity:
            return "Which website would you like me to open?"
        success = open_website(entity)
        if success:
            context.set_website(entity)
            return f"Opening {entity}."
        return f"I couldn't open {entity}."

    if intent == "SEARCH":
        if not entity:
            return "What would you like me to search for?"

        # Context resolution: explicit target > current website > ask.
        # (No explicit-target voice syntax like "search google for X" yet —
        # that's a natural Phase 9 extension. For now, we resolve purely
        # from current_website.)
        if context.current_website == "youtube":
            success = youtube_controller.search(entity)
            if success:
                context.set_last_search(entity)
                return f"Searching YouTube for {entity}."
            return "I couldn't complete that search."

        return "I'm not sure where to search. Try opening YouTube first."

    if intent == "PLAY_FIRST_RESULT":
        if context.current_website == "youtube":
            success = youtube_controller.play_first_result()
            if success:
                context.update_media_state("playing")
                return "Playing the first result."
            return "I couldn't play that video."
        return "There's no active search result to play."

    if intent == "PLAY":
        if context.current_website == "youtube":
            youtube_controller.play_pause()
            context.update_media_state("playing")
            return "Playing."
        return "I don't know what you want me to play."

    if intent == "PAUSE":
        if context.current_website == "youtube":
            youtube_controller.play_pause()
            context.update_media_state("paused")
            return "Paused."
        return "I don't know what you want me to pause."

    if intent == "NEXT":
        if context.current_website == "youtube":
            youtube_controller.next_video()
            return "Playing next video."
        return "I don't know what you want me to skip."

    if intent == "PREVIOUS":
        if context.current_website == "youtube":
            youtube_controller.previous_video()
            return "Playing previous video."
        return "I don't know what you want me to go back to."

    if intent == "SEEK_FORWARD":
        if context.current_website == "youtube":
            youtube_controller.seek_forward()
            return "Skipping forward."
        return "There's nothing playing to skip forward."

    if intent == "SEEK_BACKWARD":
        if context.current_website == "youtube":
            youtube_controller.seek_backward()
            return "Going back."
        return "There's nothing playing to go back on."

    if intent == "FULLSCREEN":
        if context.current_website == "youtube":
            youtube_controller.fullscreen_toggle()
            return "Entering fullscreen."
        return "There's nothing to make fullscreen."

    if intent == "EXIT_FULLSCREEN":
        if context.current_website == "youtube":
            youtube_controller.fullscreen_toggle()
            return "Exiting fullscreen."
        return "Nothing is in fullscreen."

    logger.warning(f"Unhandled intent: '{intent}' (raw_text='{parsed.get('raw_text')}')")
    return "Sorry, I don't know that command yet."