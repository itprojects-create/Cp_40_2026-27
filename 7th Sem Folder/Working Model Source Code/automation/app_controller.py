"""
Handles launching and closing Windows applications.
Uses a whitelist rather than executing arbitrary text as a shell command —
a deliberate safety boundary, not an oversight.
"""

import subprocess
import psutil

from utils.logger import get_logger

logger = get_logger(__name__)

# Friendly name -> the command Windows' `start` can launch by registered name.
APP_COMMANDS = {
    "chrome": "chrome",
    "vscode": "code",
    "notepad": "notepad",
    "explorer": "explorer",
    "spotify": "spotify",
    "taskmanager": "taskmgr",
}

# Friendly name -> actual process name shown in Task Manager (for closing).
PROCESS_NAMES = {
    "chrome": "chrome.exe",
    "vscode": "Code.exe",
    "notepad": "notepad.exe",
    "spotify": "Spotify.exe",
}


def open_app(app_name: str) -> bool:
    app_name = app_name.lower().strip()

    if app_name not in APP_COMMANDS:
        logger.warning(f"Attempted to open unsupported app: '{app_name}'")
        return False

    command = APP_COMMANDS[app_name]
    try:
        subprocess.Popen(f"start {command}", shell=True)
        logger.info(f"Launched app: {app_name}")
        return True
    except Exception as e:
        logger.error(f"Failed to open '{app_name}': {e}")
        return False


def close_app(app_name: str) -> bool:
    app_name = app_name.lower().strip()

    if app_name not in PROCESS_NAMES:
        logger.warning(f"Attempted to close unsupported app: '{app_name}'")
        return False

    process_name = PROCESS_NAMES[app_name]
    closed_any = False

    for proc in psutil.process_iter(["name"]):
        try:
            if proc.info["name"] and proc.info["name"].lower() == process_name.lower():
                proc.terminate()
                closed_any = True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if closed_any:
        logger.info(f"Closed app: {app_name}")
    else:
        logger.info(f"No running process found for: {app_name}")

    return closed_any