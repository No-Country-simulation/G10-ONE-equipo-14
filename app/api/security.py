"""Minimal protection for API operations that change persisted state."""

from collections import defaultdict, deque
from secrets import compare_digest
from threading import Lock
from time import monotonic

from fastapi import Header, HTTPException, Request, status

from app.core.config import settings


class MutationRateLimiter:
    """In-process fixed-window limiter suitable for the single-instance demo."""

    def __init__(self) -> None:
        self._requests: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def check(self, client_id: str) -> None:
        now = monotonic()
        cutoff = now - settings.mutation_rate_window_seconds
        with self._lock:
            requests = self._requests[client_id]
            while requests and requests[0] <= cutoff:
                requests.popleft()
            if len(requests) >= settings.mutation_rate_limit:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Mutation rate limit exceeded. Try again later.",
                )
            requests.append(now)

    def clear(self) -> None:
        with self._lock:
            self._requests.clear()


mutation_rate_limiter = MutationRateLimiter()


def _require_valid_key(api_key: str | None, detail: str) -> None:
    configured_key = (
        settings.api_write_key.get_secret_value()
        if settings.api_write_key is not None
        else None
    )
    if configured_key and (
        api_key is None or not compare_digest(api_key, configured_key)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
        )


def require_private_access(
    api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> None:
    """Protect non-public read endpoints when a shared key is configured."""
    _require_valid_key(api_key, "A valid X-API-Key header is required.")


def require_mutation_access(
    request: Request,
    api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> None:
    """Reject public writes unless enabled and, when configured, authenticated."""
    if not settings.mutations_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Mutable operations are disabled in this environment.",
        )

    _require_valid_key(
        api_key,
        "A valid X-API-Key header is required for mutable operations.",
    )

    client_id = request.client.host if request.client else "unknown"
    mutation_rate_limiter.check(client_id)
