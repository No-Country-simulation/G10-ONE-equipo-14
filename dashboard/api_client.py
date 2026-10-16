"""HTTP client functions used by the Streamlit curation queue."""

from typing import Any
from uuid import UUID

import requests


def mutation_headers(api_write_key: str | None) -> dict[str, str]:
    """Build authentication headers without logging or persisting the secret."""
    return {"X-API-Key": api_write_key} if api_write_key else {}


def api_error_message(error: requests.RequestException) -> str:
    """Return a safe, human-readable API error without exposing raw HTML."""
    response = getattr(error, "response", None)
    if response is not None:
        try:
            payload = response.json()
            detail = payload.get("detail") if isinstance(payload, dict) else None
            if isinstance(detail, str) and detail.strip():
                return detail.strip()
            if isinstance(detail, list):
                messages = [
                    str(item.get("msg", item)) if isinstance(item, dict) else str(item)
                    for item in detail
                ]
                return "; ".join(messages)
        except (ValueError, TypeError):
            pass
        status_code = getattr(response, "status_code", None)
        if status_code:
            return f"La API respondió con estado {status_code}."
    if isinstance(error, requests.Timeout):
        return "La solicitud excedió el tiempo de espera."
    if isinstance(error, requests.ConnectionError):
        return "No se pudo conectar con la API."
    return "Ocurrió un error al comunicarse con la API."


def get_health(
    api_url: str,
    *,
    timeout: float = 60,
    session: Any = requests,
) -> dict:
    """Wait long enough for a Render Free API cold start and return its health."""
    response = session.get(
        f"{api_url.rstrip('/')}/api/v1/health",
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()


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
    run_id: str | None = None,
    timeout: float = 10,
    session: Any = requests,
) -> list[dict]:
    """Return the persisted review queue from the backend."""
    params = {"status": "PENDING_REVIEW"}
    if run_id:
        params["run_id"] = str(UUID(run_id.strip()))
    response = session.get(
        f"{api_url.rstrip('/')}/api/v1/assets",
        params=params,
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()


def list_open_alerts(
    api_url: str,
    *,
    timeout: float = 10,
    session: Any = requests,
) -> list[dict]:
    response = session.get(
        f"{api_url.rstrip('/')}/api/v1/alerts",
        params={"status": "OPEN"},
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
    api_write_key: str | None = None,
    timeout: float = 10,
    session: Any = requests,
) -> dict:
    response = session.patch(
        f"{api_url.rstrip('/')}/api/v1/assets/{asset_id}",
        json={"title": title, "body": body, "editor": editor},
        headers=mutation_headers(api_write_key),
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
    api_write_key: str | None = None,
    timeout: float = 10,
    session: Any = requests,
) -> dict:
    if decision not in {"approve", "reject"}:
        raise ValueError(f"Unsupported asset decision: {decision}")
    response = session.post(
        f"{api_url.rstrip('/')}/api/v1/assets/{asset_id}/{decision}",
        json={"reviewer": reviewer, "comment": comment},
        headers=mutation_headers(api_write_key),
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()
