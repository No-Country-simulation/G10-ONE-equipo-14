"""Shared pytest fixtures for CommunityLab backend tests.

These tests intentionally use a dedicated PostgreSQL database:
    postgresql+psycopg://communitylab:communitylab@db:5432/communitylab_test

Do not point TEST_DATABASE_URL at the normal CommunityLab database.
"""

from __future__ import annotations

import os

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.db.base import Base
from app.db import models as db_models  # noqa: F401
from app.db.session import get_db
from app.main import app


TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://communitylab:communitylab@db:5432/communitylab_test",
)

# Safety guard: tests must never use the application's normal database.
if TEST_DATABASE_URL.rstrip("/").endswith("/communitylab"):
    raise RuntimeError(
        "TEST_DATABASE_URL points to the normal 'communitylab' database. "
        "Use a dedicated test database such as 'communitylab_test'."
    )


test_engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


@pytest.fixture(scope="session", autouse=True)
def prepare_test_database():
    """Build the test schema through Alembic and remove it after the session."""
    application_database_url = settings.database_url
    settings.database_url = TEST_DATABASE_URL
    alembic_config = Config("alembic.ini")

    try:
        command.upgrade(alembic_config, "head")
        yield
    finally:
        command.downgrade(alembic_config, "base")
        settings.database_url = application_database_url
        test_engine.dispose()


@pytest.fixture()
def db_session(prepare_test_database):
    """Provide an isolated SQLAlchemy session and clean tables after each test."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()

        # Application code commits during ingestion/idempotency, so a simple
        # transaction rollback is not enough. TRUNCATE with CASCADE handles
        # the intentional assets <-> asset_versions foreign-key cycle.
        with test_engine.begin() as connection:
            preparer = connection.dialect.identifier_preparer
            table_names = ", ".join(
                preparer.format_table(table) for table in Base.metadata.sorted_tables
            )
            connection.exec_driver_sql(
                f"TRUNCATE TABLE {table_names} RESTART IDENTITY CASCADE"
            )


@pytest.fixture()
def client(db_session: Session):
    """FastAPI TestClient using the same test DB session as the test itself."""

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)
