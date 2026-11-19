"""
Simple, safe system-info commands. Deliberately minimal in this phase —
volume control and other system actions are added in Phase 6.
"""
import subprocess
import ctypes
from datetime import datetime
from utils.logger import get_logger

logger = get_logger(__name__)


def get_current_time() -> str:
    """Returns the current time as a natural-sounding spoken phrase."""
    now = datetime.now()
    time_str = now.strftime("%I:%M %p").lstrip("0")  # e.g. "2:31 PM" not "02:31 PM"
    logger.info(f"Current time requested: {time_str}")
    return f"It is currently {time_str}"

def lock_computer() -> None:
    """Locks the Windows session immediately using the native user32 call."""
    logger.info("Locking computer")
    ctypes.windll.user32.LockWorkStation()


def open_settings() -> None:
    """Opens the Windows Settings app."""
    logger.info("Opening Windows Settings")
    subprocess.Popen("start ms-settings:", shell=True)


def open_task_manager() -> None:
    """Opens Task Manager."""
    logger.info("Opening Task Manager")
    subprocess.Popen("taskmgr", shell=True)