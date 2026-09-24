import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateTable
from app.db.base import Base
from app.db.models import Interaction

def test_interaction_model_metadata():
    table = Base.metadata.tables["interactions"]
    assert table.c.id.primary_key
    assert not table.c.fingerprint.nullable
    assert {"organization_id", "community_id", "external_id", "fingerprint"}.issubset(table.c.keys())
    sql = str(CreateTable(table).compile(dialect=postgresql.dialect()))
    assert "uq_interactions_fingerprint_per_community" in sql
    assert "ck_interactions_text_nonempty" in sql

# Optional integration test against an isolated PostgreSQL test database.
def test_postgres_rejects_duplicate_fingerprint():
    import os, uuid
    from sqlalchemy.exc import IntegrityError
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set TEST_DATABASE_URL to an isolated PostgreSQL test database")
    engine = create_engine(url)
    with engine.connect() as conn:
        transaction = conn.begin()
        try:
            Base.metadata.create_all(conn, tables=[Interaction.__table__], checkfirst=True)
            row = dict(id=uuid.uuid4(), organization_id="one", community_id=str(uuid.uuid4()), external_id=None,
                       author="Ana", channel="general", type="comment", text="Hello", fingerprint="a"*64)
            conn.execute(Interaction.__table__.insert().values(**row))
            with pytest.raises(IntegrityError):
                with conn.begin_nested():
                    conn.execute(Interaction.__table__.insert().values(**{**row, "id": uuid.uuid4()}))
        finally:
            transaction.rollback()
    engine.dispose()
