"""Unit tests for the dashboard's persistent curation client."""

import pytest
import requests
from unittest.mock import Mock

from dashboard.api_client import (
    api_error_message,
    decide_asset,
    edit_asset,
    get_health,
    get_run,
    list_alerts,
    list_assets,
    list_open_alerts,
    list_pending_assets,
    list_runs,
    publish_asset,
    resolve_alert,
)


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class FakeSession:
    def __init__(self):
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append(("GET", url, kwargs))
        if url.endswith("/health"):
            return FakeResponse({"status": "ok", "database": "ok"})
        return FakeResponse([{"id": "asset-1", "status": "PENDING_REVIEW"}])

    def patch(self, url, **kwargs):
        self.calls.append(("PATCH", url, kwargs))
        return FakeResponse({"id": "asset-1", "version": 2})

    def post(self, url, **kwargs):
        self.calls.append(("POST", url, kwargs))
        return FakeResponse({"id": "asset-1", "status": "APPROVED"})


def test_list_pending_assets_uses_persisted_queue_endpoint():
    session = FakeSession()

    assets = list_pending_assets("http://api:8000/", session=session)

    assert assets[0]["id"] == "asset-1"
    assert session.calls == [
        (
            "GET",
            "http://api:8000/api/v1/assets",
            {"params": {"status": "PENDING_REVIEW"}, "timeout": 10},
        )
    ]


def test_list_pending_assets_filters_the_current_run():
    session = FakeSession()
    run_id = "bdc11ba4-0b40-4a15-b909-16f2e8fae50a"

    list_pending_assets("http://api:8000", run_id=run_id, session=session)

    assert session.calls == [
        (
            "GET",
            "http://api:8000/api/v1/assets",
            {
                "params": {"status": "PENDING_REVIEW", "run_id": run_id},
                "timeout": 10,
            },
        )
    ]


def test_list_assets_can_recover_approved_assets_for_the_current_run():
    session = FakeSession()
    run_id = "bdc11ba4-0b40-4a15-b909-16f2e8fae50a"

    list_assets(
        "http://api:8000",
        status="APPROVED",
        run_id=run_id,
        session=session,
    )

    assert session.calls[0][2]["params"] == {
        "status": "APPROVED",
        "run_id": run_id,
    }


def test_publish_asset_sends_mutation_key_and_returns_receipt():
    session = FakeSession()

    receipt = publish_asset(
        "http://api:8000/",
        "asset-1",
        api_write_key="shared-secret",
        session=session,
    )

    assert receipt["status"] == "APPROVED"
    assert session.calls == [
        (
            "POST",
            "http://api:8000/api/v1/assets/asset-1/publish",
            {"headers": {"X-API-Key": "shared-secret"}, "timeout": 30},
        )
    ]


def test_health_uses_a_short_probe_for_automatic_cold_start_retries():
    session = FakeSession()

    health = get_health("https://communitylab-api.onrender.com/", session=session)

    assert health == {"status": "ok", "database": "ok"}
    assert session.calls == [
        (
            "GET",
            "https://communitylab-api.onrender.com/api/v1/health",
            {"timeout": 5},
        )
    ]


@pytest.mark.parametrize(
    "payload",
    [None, [], {}, {"status": "ok"}, {"status": "ok", "database": "error"}],
)
def test_health_rejects_responses_that_do_not_confirm_readiness(payload):
    session = Mock()
    session.get.return_value = FakeResponse(payload)

    with pytest.raises(requests.RequestException):
        get_health("http://api:8000", session=session)


@pytest.mark.parametrize("status_code", [200, 503])
def test_health_rejects_html_pages_returned_while_render_is_starting(status_code):
    response = requests.Response()
    response.status_code = status_code
    response._content = b"<html><body>Service starting</body></html>"
    session = Mock()
    session.get.return_value = response

    with pytest.raises(requests.RequestException):
        get_health("http://api:8000", session=session)


@pytest.mark.parametrize(
    "error", [requests.Timeout(), requests.ConnectionError(), requests.HTTPError()]
)
def test_health_propagates_failures_to_the_connection_monitor(error):
    session = Mock()
    session.get.side_effect = error

    with pytest.raises(type(error)):
        get_health("http://api:8000", session=session)


def test_list_open_alerts_uses_separate_internal_endpoint():
    session = FakeSession()
    alerts = list_open_alerts("http://api:8000/", session=session)
    assert alerts
    assert session.calls == [
        (
            "GET",
            "http://api:8000/api/v1/alerts",
            {"params": {"status": "OPEN"}, "timeout": 10},
        )
    ]


@pytest.mark.parametrize("status", [None, "OPEN", "RESOLVED"])
def test_list_alerts_can_include_resolved_alerts(status):
    session = FakeSession()

    alerts = list_alerts("http://api:8000/", status=status, session=session)

    assert alerts
    assert session.calls == [
        (
            "GET",
            "http://api:8000/api/v1/alerts",
            {"params": {"status": status or ""}, "timeout": 10},
        )
    ]


def test_get_run_recovers_a_persisted_execution():
    session = FakeSession()
    run_id = "bdc11ba4-0b40-4a15-b909-16f2e8fae50a"

    result = get_run("http://api:8000/", run_id, session=session)

    assert result[0]["id"] == "asset-1"
    assert session.calls == [
        (
            "GET",
            f"http://api:8000/api/v1/runs/{run_id}",
            {"timeout": 10},
        )
    ]


@pytest.mark.parametrize("api_write_key", [None, "shared-secret"])
def test_resolve_alert_sends_write_key(api_write_key):
    session = FakeSession()
    alert_id = "bdc11ba4-0b40-4a15-b909-16f2e8fae50a"

    resolve_alert(
        "http://api:8000/",
        alert_id,
        api_write_key=api_write_key,
        session=session,
    )

    assert session.calls == [
        (
            "POST",
            f"http://api:8000/api/v1/alerts/{alert_id}/resolve",
            {
                "headers": {"X-API-Key": api_write_key} if api_write_key else {},
                "timeout": 10,
            },
        )
    ]


def test_resolve_alert_rejects_invalid_identifier_without_http_call():
    session = FakeSession()

    with pytest.raises(ValueError):
        resolve_alert("http://api:8000", "invalid", session=session)

    assert session.calls == []


def test_get_run_rejects_an_invalid_uuid_without_http_call():
    session = FakeSession()

    with pytest.raises(ValueError):
        get_run("http://api:8000", "not-a-uuid", session=session)

    assert session.calls == []


def test_list_runs_sends_filters_and_private_header():
    session = FakeSession()

    runs = list_runs(
        "http://api:8000/",
        organization_id="one",
        community_id="g10",
        api_write_key="shared-secret",
        limit=25,
        session=session,
    )

    assert runs
    assert session.calls == [
        (
            "GET",
            "http://api:8000/api/v1/runs",
            {
                "params": {
                    "limit": 25,
                    "organization_id": "one",
                    "community_id": "g10",
                },
                "headers": {"X-API-Key": "shared-secret"},
                "timeout": 10,
            },
        )
    ]


def test_edit_asset_sends_curator_changes():
    session = FakeSession()

    result = edit_asset(
        "http://api:8000",
        "asset-1",
        title="Título",
        body="Contenido",
        editor="Francis",
        session=session,
    )

    assert result["version"] == 2
    assert session.calls[0][0:2] == (
        "PATCH",
        "http://api:8000/api/v1/assets/asset-1",
    )
    assert session.calls[0][2]["json"]["editor"] == "Francis"
    assert session.calls[0][2]["headers"] == {}


def test_edit_asset_sends_api_key_only_when_configured():
    session = FakeSession()
    edit_asset(
        "http://api:8000",
        "asset-1",
        title="Título",
        body="Contenido",
        editor="Francis",
        api_write_key="shared-secret",
        session=session,
    )
    assert session.calls[0][2]["headers"] == {"X-API-Key": "shared-secret"}


def test_decide_asset_rejects_unknown_decision_without_http_call():
    session = FakeSession()

    with pytest.raises(ValueError, match="Unsupported asset decision"):
        decide_asset(
            "http://api:8000",
            "asset-1",
            decision="publish",
            reviewer="Francis",
            session=session,
        )

    assert session.calls == []


def test_decide_asset_posts_review_decision():
    session = FakeSession()

    result = decide_asset(
        "http://api:8000",
        "asset-1",
        decision="approve",
        reviewer="Francis",
        comment="Listo",
        session=session,
    )
    assert result["status"] == "APPROVED"
    assert session.calls[0] == (
        "POST",
        "http://api:8000/api/v1/assets/asset-1/approve",
        {
            "json": {"reviewer": "Francis", "comment": "Listo"},
            "headers": {},
            "timeout": 10,
        },
    )


def test_api_error_message_extracts_fastapi_detail():
    response = requests.Response()
    response.status_code = 409
    response._content = b'{"detail":"Approved assets are immutable."}'
    error = requests.HTTPError(response=response)
    assert api_error_message(error) == "Approved assets are immutable."


def test_api_error_message_handles_validation_and_network_failures():
    response = requests.Response()
    response.status_code = 422
    response._content = b'{"detail":[{"msg":"Field required"}]}'
    assert api_error_message(requests.HTTPError(response=response)) == "Field required"
    assert (
        api_error_message(requests.Timeout())
        == "La solicitud excedió el tiempo de espera."
    )
    assert (
        api_error_message(requests.ConnectionError())
        == "No se pudo conectar con la API."
    )
