"""HTTP client functions used by the Streamlit curation queue."""

from typing import Any
from uuid import UUID

import requests


def get_run(
    api_url: str,
    run_id: str,
    *,
    timeout: float = 10,
    session: Any = requests,
) -> dict:
    """Recover one persisted pipeline execution by UUID."""
    normalized_run_id = str(UUID(run_id.strip()))
    response = session.get(
        f"{api_url.rstrip('/')}/api/v1/runs/{normalized_run_id}",
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()


def list_pending_assets(
    api_url: str,
    *,
    timeout: float = 10,
    session: Any = requests,
) -> list[dict]:
    """Return the persisted review queue from the backend."""
    response = session.get(
        f"{api_url.rstrip('/')}/api/v1/assets",
        params={"status": "PENDING_REVIEW"},
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()


def edit_asset(
    api_url: str,
    asset_id: str,
    *,
    title: str,
    body: str,
    editor: str,
    timeout: float = 10,
    session: Any = requests,
) -> dict:
    response = session.patch(
        f"{api_url.rstrip('/')}/api/v1/assets/{asset_id}",
        json={"title": title, "body": body, "editor": editor},
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()


def decide_asset(
    api_url: str,
    asset_id: str,
    *,
    decision: str,
    reviewer: str,
    comment: str | None = None,
    timeout: float = 10,
    session: Any = requests,
) -> dict:
    if decision not in {"approve", "reject"}:
        raise ValueError(f"Unsupported asset decision: {decision}")
    response = session.post(
        f"{api_url.rstrip('/')}/api/v1/assets/{asset_id}/{decision}",
        json={"reviewer": reviewer, "comment": comment},
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()
