"""
Rule-based intent parser. Converts raw transcribed text into a
structured command: {intent, entity, confidence}.

This module ONLY parses — it never executes anything and never
touches context. That separation is what lets this file be swapped
for an LLM-based parser later (Phase 9) without changing anything
downstream (command_router.py, controllers).

confidence is fixed at 0.95 for any rule that matches (arbitrary but
consistent) and 0.0 for no match — a placeholder that becomes meaningful
once/if a real classifier replaces this rule-based version.
"""

import re
from utils.logger import get_logger

logger = get_logger(__name__)

INTENT_PATTERNS = {
    "OPEN_APPLICATION": [
        r"open (chrome|vs code|visual studio code|notepad|explorer|file explorer|spotify|task manager)",
    ],
    "CLOSE_APPLICATION": [
        r"close (chrome|vs code|visual studio code|notepad|explorer|file explorer|spotify|task manager)",
    ],
    "GET_TIME": [
        r"what('?s| is) the time",
        r"what time is it",
        r"current time",
    ],
    "SCREENSHOT": [
        r"take a screenshot",
        r"screenshot",
    ],
    "VOLUME_UP": [
        r"(increase|turn up|raise) (the )?volume",
        r"volume up",
    ],
    "VOLUME_DOWN": [
        r"(decrease|turn down|lower) (the )?volume",
        r"volume down",
    ],
    "MUTE": [
        r"^mute$",
        r"mute (the )?(volume|sound|audio)",
    ],
    "UNMUTE": [
        r"^unmute$",
        r"unmute (the )?(volume|sound|audio)",
    ],
    "LOCK_COMPUTER": [
        r"lock (the )?(computer|pc|screen)",
    ],
    "OPEN_SETTINGS": [
        r"open (windows )?settings",
    ],
    "OPEN_TASK_MANAGER": [
        r"open task manager",
    ],
    "OPEN_WEBSITE": [
        r"open (youtube|google)",
    ],
    "SEARCH": [
        r"search (for )?(.+)",
    ],
    "PLAY_FIRST_RESULT": [
        r"play the first (video|result)",
        r"play first (video|result)",
    ],
    "PLAY": [
        r"^play$",
        r"^resume$",
    ],
    "PAUSE": [
        r"^pause$",
        r"^stop$",
    ],
    "NEXT": [
        r"next (video|song|track)",
        r"^next$",
        r"^skip$",
    ],
    "PREVIOUS": [
        r"previous (video|song|track)",
        r"^previous$",
        r"^back$",
    ],
    "SEEK_FORWARD": [
        r"skip forward",
        r"forward (ten|10) seconds",
    ],
    "SEEK_BACKWARD": [
        r"go back (ten|10) seconds",
        r"skip backward",
    ],
    "FULLSCREEN": [
        r"^full\s*screen$",
        r"go (in(to)? )?full\s*screen",
        r"enter full\s*screen",
    ],
    "EXIT_FULLSCREEN": [
        r"exit full\s*screen",
        r"leave full\s*screen",
        r"get out of full\s*screen",
    ],
}

ENTITY_ALIASES = {
    "vs code": "vscode",
    "visual studio code": "vscode",
    "file explorer": "explorer",
    "task manager": "taskmanager",
}

def _normalize_entity(raw_entity: str) -> str:
    return ENTITY_ALIASES.get(raw_entity, raw_entity)

def parse_intent(text: str) -> dict:
    if not text:
        return {"intent": "UNKNOWN", "entity": None, "confidence": 0.0, "raw_text": text}

    normalized = text.lower().strip().rstrip(".")

    for intent, patterns in INTENT_PATTERNS.items():
        for pattern in patterns:
            match = re.search(pattern, normalized)
            if match:
                entity = None

                # Some patterns (VOLUME_UP etc.) have groups that aren't
                # entities (e.g. optional "the ") — only OPEN/CLOSE_APPLICATION
                # patterns have a meaningful group(1) as an app name.
                if intent in ("OPEN_APPLICATION", "CLOSE_APPLICATION", "OPEN_WEBSITE"):
                    entity = _normalize_entity(match.group(1))
                elif intent == "SEARCH":
                    entity = match.group(2).strip()

                result = {
                    "intent": intent,
                    "entity": entity,
                    "confidence": 0.95,
                    "raw_text": text,
                }
                logger.info(f"Parsed intent: {result}")
                return result

    logger.warning(f"No intent matched for: '{normalized}'")
    return {"intent": "UNKNOWN", "entity": None, "confidence": 0.0, "raw_text": text}