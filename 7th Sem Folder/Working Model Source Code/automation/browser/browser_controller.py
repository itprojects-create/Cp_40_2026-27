"""
Manages a single persistent Chrome instance (dedicated profile, remote
debugging enabled) and a Playwright connection to it over CDP.

Design decisions:
- Uses a DEDICATED profile directory (not your default Chrome profile)
  because Chrome only allows one running instance per profile — if your
  regular Chrome happens to already be open, we can't retrofit debug
  flags onto it. A separate profile sidesteps that entirely and still
  persists logins/cookies across assistant runs.
- Chrome + Playwright objects are module-level singletons: launched once,
  reused for every command in the session, not relaunched per-command.
"""

import subprocess
import time
import shutil

from playwright.sync_api import sync_playwright

from config.settings import CHROME_DEBUG_PORT, CHROME_PROFILE_DIR, SUPPORTED_WEBSITES
from utils.logger import get_logger

logger = get_logger(__name__)

_playwright = None
_browser = None
_page = None


def _find_chrome_executable() -> str:
    """
    Locates chrome.exe. Checks common install paths first, falls back
    to relying on it being on PATH.
    """
    common_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    for path in common_paths:
        if shutil.os.path.exists(path):
            return path

    # Fall back to PATH lookup
    found = shutil.which("chrome")
    if found:
        return found

    raise FileNotFoundError(
        "Could not locate chrome.exe. Update CHROME_PROFILE_DIR/common_paths "
        "in browser_controller.py with your install location."
    )


def _launch_chrome_process() -> None:
    """Starts Chrome with the debug port and dedicated profile."""
    chrome_path = _find_chrome_executable()
    CHROME_PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    logger.info(f"Launching Chrome (debug port {CHROME_DEBUG_PORT})...")
    subprocess.Popen([
        chrome_path,
        f"--remote-debugging-port={CHROME_DEBUG_PORT}",
        f"--user-data-dir={CHROME_PROFILE_DIR}",
        "--no-first-run",
        "--no-default-browser-check",
    ])
    # Give Chrome a moment to actually open the debug port before we
    # try to connect — connecting too early throws a connection error.
    time.sleep(2)


def get_page():
    """
    Returns a live Playwright Page object connected to the assistant's
    Chrome instance, launching Chrome first if it isn't already running
    on the debug port.
    """
    global _playwright, _browser, _page

    if _page is not None:
        return _page

    _playwright = sync_playwright().start()

    try:
        # Try attaching to an already-running debug-enabled instance first
        # (e.g. if a previous assistant session left it open).
        _browser = _playwright.chromium.connect_over_cdp(
            f"http://localhost:{CHROME_DEBUG_PORT}"
        )
        logger.info("Attached to existing Chrome debug instance.")
    except Exception:
        _launch_chrome_process()
        _browser = _playwright.chromium.connect_over_cdp(
            f"http://localhost:{CHROME_DEBUG_PORT}"
        )
        logger.info("Launched and attached to new Chrome instance.")

    context = _browser.contexts[0] if _browser.contexts else _browser.new_context()
    _page = context.pages[0] if context.pages else context.new_page()

    return _page


def open_website(website_name: str) -> bool:
    """
    Navigates to a whitelisted website by name (e.g. "youtube", "google").
    Returns True on success.
    """
    website_name = website_name.lower().strip()

    if website_name not in SUPPORTED_WEBSITES:
        logger.warning(f"Attempted to open unsupported website: '{website_name}'")
        return False

    url = SUPPORTED_WEBSITES[website_name]
    try:
        page = get_page()
        page.goto(url)
        page.bring_to_front()
        logger.info(f"Navigated to {website_name} ({url})")
        return True
    except Exception as e:
        logger.error(f"Failed to open '{website_name}': {e}")
        return False


def shutdown_browser() -> None:
    """Cleanly closes the Playwright connection (not Chrome itself)."""
    global _playwright, _browser, _page
    if _playwright is not None:
        _playwright.stop()
        _playwright = None
        _browser = None
        _page = None
        logger.info("Playwright connection closed.")