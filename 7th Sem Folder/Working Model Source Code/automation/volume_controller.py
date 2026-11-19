"""
Precise system volume control via pycaw, which wraps the real Windows
Core Audio API (IAudioEndpointVolume). Chosen over simulated media-key
presses because it gives exact, readable, settable levels rather than
relative "press up N times" behavior.
"""

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

from config.settings import VOLUME_STEP
from utils.logger import get_logger

logger = get_logger(__name__)


def _get_volume_interface() -> IAudioEndpointVolume:
    """Fetches the interface for the default audio output device."""
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    return cast(interface, POINTER(IAudioEndpointVolume))


def get_volume_percent() -> int:
    """Returns current volume as an integer 0-100."""
    volume = _get_volume_interface()
    scalar = volume.GetMasterVolumeLevelScalar()  # 0.0 to 1.0
    return round(scalar * 100)


def set_volume_percent(percent: int) -> int:
    """Sets volume to an exact percent (0-100), clamped to that range."""
    percent = max(0, min(100, percent))
    volume = _get_volume_interface()
    volume.SetMasterVolumeLevelScalar(percent / 100, None)
    logger.info(f"Volume set to {percent}%")
    return percent


def volume_up() -> int:
    """Increases volume by VOLUME_STEP. Returns the new level."""
    current = get_volume_percent()
    new_level = set_volume_percent(current + int(VOLUME_STEP * 100))
    return new_level


def volume_down() -> int:
    """Decreases volume by VOLUME_STEP. Returns the new level."""
    current = get_volume_percent()
    new_level = set_volume_percent(current - int(VOLUME_STEP * 100))
    return new_level


def mute() -> None:
    volume = _get_volume_interface()
    volume.SetMute(1, None)
    logger.info("Muted")


def unmute() -> None:
    volume = _get_volume_interface()
    volume.SetMute(0, None)
    logger.info("Unmuted")