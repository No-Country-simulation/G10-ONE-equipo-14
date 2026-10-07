from app.core.config import Settings


def test_render_postgres_url_uses_psycopg_v3():
    settings = Settings(database_url="postgresql://user:secret@example.test/communitylab")

    assert settings.database_url == "postgresql+psycopg://user:secret@example.test/communitylab"


def test_explicit_psycopg_url_is_unchanged():
    url = "postgresql+psycopg://user:secret@example.test/communitylab"

    assert Settings(database_url=url).database_url == url
