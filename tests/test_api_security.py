from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from pydantic import SecretStr

from app.api.security import (
    mutation_rate_limiter,
    require_mutation_access,
    require_private_access,
)
from app.core.config import settings


def _client() -> TestClient:
    test_app = FastAPI()

    @test_app.post("/write", dependencies=[Depends(require_mutation_access)])
    def write():
        return {"ok": True}

    @test_app.get("/read")
    def read():
        return {"ok": True}

    @test_app.get("/private", dependencies=[Depends(require_private_access)])
    def private_read():
        return {"ok": True}

    return TestClient(test_app)


def test_public_reads_remain_available_when_mutations_are_disabled():
    previous = settings.mutations_enabled
    settings.mutations_enabled = False
    try:
        with _client() as client:
            assert client.get("/read").status_code == 200
            assert client.post("/write").status_code == 403
    finally:
        settings.mutations_enabled = previous


def test_configured_api_key_is_required_for_mutations():
    previous = settings.api_write_key
    settings.api_write_key = SecretStr("test-secret")
    mutation_rate_limiter.clear()
    try:
        with _client() as client:
            assert client.post("/write").status_code == 401
            assert (
                client.post("/write", headers={"X-API-Key": "wrong"}).status_code == 401
            )
            assert (
                client.post("/write", headers={"X-API-Key": "test-secret"}).status_code
                == 200
            )
    finally:
        settings.api_write_key = previous
        mutation_rate_limiter.clear()


def test_configured_api_key_protects_private_reads_without_rate_limiting():
    previous = settings.api_write_key
    settings.api_write_key = SecretStr("test-secret")
    try:
        with _client() as client:
            assert client.get("/private").status_code == 401
            assert (
                client.get("/private", headers={"X-API-Key": "wrong"}).status_code
                == 401
            )
            assert (
                client.get("/private", headers={"X-API-Key": "test-secret"}).status_code
                == 200
            )
            assert (
                client.get("/private", headers={"X-API-Key": "test-secret"}).status_code
                == 200
            )
    finally:
        settings.api_write_key = previous


def test_mutation_rate_limit_returns_429():
    previous_limit = settings.mutation_rate_limit
    previous_key = settings.api_write_key
    settings.mutation_rate_limit = 1
    settings.api_write_key = None
    mutation_rate_limiter.clear()
    try:
        with _client() as client:
            assert client.post("/write").status_code == 200
            assert client.post("/write").status_code == 429
    finally:
        settings.mutation_rate_limit = previous_limit
        settings.api_write_key = previous_key
        mutation_rate_limiter.clear()
