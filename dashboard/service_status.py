"""Per-session health polling without blocking the dashboard during cold starts."""

from collections.abc import Callable
from dataclasses import dataclass

import requests


POLL_SECONDS = 15
CONNECTED_POLL_SECONDS = 60
CONNECTING_SECONDS = 120


@dataclass
class ServiceStatus:
    health: dict | None = None
    error: requests.RequestException | None = None
    last_checked: float | None = None
    waiting_since: float | None = None

    def timed_out(self, now: float) -> bool:
        return (
            self.waiting_since is not None
            and now - self.waiting_since >= CONNECTING_SECONDS
        )

    def retry(self) -> None:
        """Start a fresh connection window on the next poll."""
        self.last_checked = None
        self.waiting_since = None
        self.error = None

    def poll(self, check_health: Callable[[], dict], *, now: float) -> bool:
        """Check when due; return whether controls need an availability update.

        Called sequentially by a Streamlit fragment. Successful sessions and
        prolonged outages use a slower interval, including on ordinary app reruns.
        """
        interval = (
            CONNECTED_POLL_SECONDS
            if self.health is not None or self.timed_out(now)
            else POLL_SECONDS
        )
        if self.last_checked is not None and now - self.last_checked < interval:
            return False

        was_available = self.health is not None
        self.last_checked = now
        if not was_available and self.waiting_since is None:
            self.waiting_since = now
        try:
            self.health = check_health()
        except requests.RequestException as error:
            self.health = None
            self.error = error
            if was_available:
                self.waiting_since = now
        else:
            self.error = None
            self.waiting_since = None
        return was_available != (self.health is not None)
