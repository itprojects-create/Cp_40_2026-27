"""
Tracks the assistant's current state across commands: what app/website
is active, what was last searched, media playback state, etc.

Introduced now (Phase 5) even though most fields stay unused until
browser support lands in Phase 6/7 — this is a deliberate architectural
decision so the router never needs a rewrite later. See project notes
on context-awareness being a core feature, not an add-on.

Encapsulated behind methods (not raw attribute access) so validation/
logging can be added later without breaking callers.
"""

from dataclasses import dataclass, field
from typing import Optional
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class AssistantContext:
    current_application: Optional[str] = None
    current_website: Optional[str] = None
    current_media_source: Optional[str] = None
    current_media_state: Optional[str] = None   # "playing" | "paused" | None
    last_search_query: Optional[str] = None
    last_intent: Optional[str] = None

    def set_application(self, app_name: str) -> None:
        logger.info(f"Context: application -> {app_name}")
        self.current_application = app_name
        # Opening a new application implies we've left any website context
        # (e.g. opening VS Code while YouTube was playing in the background
        # shouldn't make "pause" ambiguous — VS Code becomes the active app,
        # though the website context is preserved separately below).

    def set_website(self, website_name: str) -> None:
        logger.info(f"Context: website -> {website_name}")
        self.current_website = website_name
        self.current_application = "browser"

    def set_media_source(self, source: str) -> None:
        logger.info(f"Context: media source -> {source}")
        self.current_media_source = source

    def update_media_state(self, state: str) -> None:
        logger.info(f"Context: media state -> {state}")
        self.current_media_state = state

    def set_last_search(self, query: str) -> None:
        self.last_search_query = query

    def set_last_intent(self, intent: str) -> None:
        self.last_intent = intent

    def clear_website_context(self) -> None:
        logger.info("Context: website cleared")
        self.current_website = None
        self.current_media_source = None
        self.current_media_state = None

    def get_current_context(self) -> dict:
        return {
            "current_application": self.current_application,
            "current_website": self.current_website,
            "current_media_source": self.current_media_source,
            "current_media_state": self.current_media_state,
            "last_search_query": self.last_search_query,
            "last_intent": self.last_intent,
        }