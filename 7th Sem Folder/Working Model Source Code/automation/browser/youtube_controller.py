"""
YouTube-specific browser automation.

Three distinct techniques, chosen per action for reliability:
  - search():           URL construction — no DOM interaction needed.
  - play_first_result(): real DOM query via Playwright — needed to find
                          and click a specific, dynamic element.
  - play/pause/next/etc: YouTube's native keyboard shortcuts — faster
                          and more robust than clicking buttons whose
                          selectors shift with UI updates.

All functions assume the browser is already on a YouTube page (the
router is responsible for calling open_website("youtube") first if
context doesn't already have it).
"""

from urllib.parse import quote

from automation.browser.browser_controller import get_page
from config.settings import YOUTUBE_SEARCH_URL, YOUTUBE_FIRST_RESULT_SELECTOR
from utils.logger import get_logger

logger = get_logger(__name__)


def search(query: str) -> bool:
    """Navigates to YouTube search results for the given query."""
    try:
        page = get_page()
        url = YOUTUBE_SEARCH_URL.format(query=quote(query))
        page.goto(url)
        page.bring_to_front()
        logger.info(f"YouTube search: '{query}'")
        return True
    except Exception as e:
        logger.error(f"YouTube search failed: {e}")
        return False


def play_first_result() -> bool:
    """
    Clicks the first video in the current search results page.
    Assumes search() was already called and results are loaded.
    """
    try:
        page = get_page()
        # wait_for ensures we don't click before results have rendered —
        # a fixed sleep() would be fragile across different connection speeds.
        page.wait_for_selector(YOUTUBE_FIRST_RESULT_SELECTOR, timeout=8000)
        first_result = page.locator(YOUTUBE_FIRST_RESULT_SELECTOR).first
        first_result.click()
        page.bring_to_front()
        logger.info("Playing first YouTube search result.")
        return True
    except Exception as e:
        logger.error(f"Failed to play first result: {e}")
        return False


def _press_key(key: str) -> bool:
    """Shared helper: sends a keyboard shortcut to the active YouTube page."""
    try:
        page = get_page()
        page.bring_to_front()
        page.keyboard.press(key)
        return True
    except Exception as e:
        logger.error(f"Failed to send key '{key}': {e}")
        return False


def play_pause() -> bool:
    """YouTube's spacebar shortcut toggles play/pause."""
    return _press_key(" ")


def next_video() -> bool:
    return _press_key("Shift+N")


def previous_video() -> bool:
    return _press_key("Shift+P")


def seek_forward() -> bool:
    """YouTube's 'l' key skips forward 10 seconds."""
    return _press_key("l")


def seek_backward() -> bool:
    """YouTube's 'j' key skips backward 10 seconds."""
    return _press_key("j")


def volume_up() -> bool:
    return _press_key("ArrowUp")


def volume_down() -> bool:
    return _press_key("ArrowDown")


def mute_toggle() -> bool:
    return _press_key("m")


def fullscreen_toggle() -> bool:
    return _press_key("f")