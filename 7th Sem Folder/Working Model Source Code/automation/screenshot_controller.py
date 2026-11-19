"""
Captures screenshots using mss (fast, minimal dependency footprint).
"""

from datetime import datetime
import mss
import mss.tools

from config.settings import SCREENSHOT_DIR
from utils.logger import get_logger

logger = get_logger(__name__)


def take_screenshot() -> str:
    """
    Captures the primary monitor and saves it as a timestamped PNG.
    Returns the saved file path as a string.
    """
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = SCREENSHOT_DIR / f"screenshot_{timestamp}.png"

    with mss.mss() as sct:
        monitor = sct.monitors[1]  # index 0 is "all monitors combined"; 1 is primary
        screenshot = sct.grab(monitor)
        mss.tools.to_png(screenshot.rgb, screenshot.size, output=str(filepath))

    logger.info(f"Screenshot saved: {filepath}")
    return str(filepath)