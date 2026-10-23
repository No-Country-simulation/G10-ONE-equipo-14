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
    timeout: float = 5,
    session: Any = requests,
) -> dict:
    """Probe readiness briefly; the dashboard retries while Render wakes up."""
    response = session.get(
        f"{api_url.rstrip('/')}/api/v1/health",
        timeout=timeout,
    )
    response.raise_for_status()
    payload = response.json()
    if (
        not isinstance(payload, dict)
        or payload.get("status") != "ok"
        or payload.get("database") != "ok"
    ):
        raise requests.RequestException("La API todavía no está lista.")
    return payload


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


def list_runs(
    api_url: str,
    *,
    organization_id: str | None = None,
    community_id: str | None = None,
    api_write_key: str | None = None,
    limit: int = 100,
    timeout: float = 10,
    session: Any = requests,
) -> list[dict]:
    """Return recent executions available to the authenticated dashboard."""
    params: dict[str, str | int] = {"limit": limit}
    if organization_id:
        params["organization_id"] = organization_id
    if community_id:
        params["community_id"] = community_id
    response = session.get(
        f"{api_url.rstrip('/')}/api/v1/runs",
        params=params,
        headers=mutation_headers(api_write_key),
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
    return list_assets(
        api_url,
        status="PENDING_REVIEW",
        run_id=run_id,
        timeout=timeout,
        session=session,
    )


def list_assets(
    api_url: str,
    *,
    status: str,
    run_id: str | None = None,
    timeout: float = 10,
    session: Any = requests,
) -> list[dict]:
    """Return persisted assets filtered by state and optional run UUID."""
    params = {"status": status}
    if run_id:
        params["run_id"] = str(UUID(run_id.strip()))
    response = session.get(
        f"{api_url.rstrip('/')}/api/v1/assets",
        params=params,
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()


def publish_asset(
    api_url: str,
    asset_id: str,
    *,
    api_write_key: str | None = None,
    timeout: float = 30,
    session: Any = requests,
) -> dict:
    """Publish an approved asset to configured object storage."""
    response = session.post(
        f"{api_url.rstrip('/')}/api/v1/assets/{asset_id}/publish",
        headers=mutation_headers(api_write_key),
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
    return list_alerts(api_url, status="OPEN", timeout=timeout, session=session)


def list_alerts(
    api_url: str,
    *,
    status: str | None = None,
    timeout: float = 10,
    session: Any = requests,
) -> list[dict]:
    """Return alerts in every state, or filter by a specific status."""
    response = session.get(
        f"{api_url.rstrip('/')}/api/v1/alerts",
        # An omitted status defaults to OPEN in the API; empty means all states.
        params={"status": status or ""},
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()


def resolve_alert(
    api_url: str,
    alert_id: str,
    *,
    api_write_key: str | None = None,
    timeout: float = 10,
    session: Any = requests,
) -> dict:
    """Persist the transition from an open alert to a resolved alert."""
    normalized_alert_id = str(UUID(alert_id.strip()))
    response = session.post(
        f"{api_url.rstrip('/')}/api/v1/alerts/{normalized_alert_id}/resolve",
        headers=mutation_headers(api_write_key),
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
