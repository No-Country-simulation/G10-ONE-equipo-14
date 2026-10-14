"""Unit tests for the dashboard's persistent curation client."""

import pytest

from dashboard.api_client import decide_asset, edit_asset, get_run, list_pending_assets


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


def test_get_run_rejects_an_invalid_uuid_without_http_call():
    session = FakeSession()

    with pytest.raises(ValueError):
        get_run("http://api:8000", "not-a-uuid", session=session)

    assert session.calls == []


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
            "timeout": 10,
        },
    )
