"""Regression checks for the dashboard's visual shell and help affordances."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_SOURCE = (ROOT / "dashboard" / "app.py").read_text(encoding="utf-8")


def test_dashboard_brand_asset_is_packaged_in_the_container():
    logo = ROOT / "dashboard" / "assets" / "communitylab-logo.svg"
    dockerfile = (ROOT / "dashboard" / "Dockerfile").read_text(encoding="utf-8")

    assert logo.is_file()
    assert '<title id="title">CommunityLab</title>' in logo.read_text(encoding="utf-8")
    assert "COPY dashboard/assets ./assets" in dockerfile


def test_sidebar_exposes_contextual_help_and_project_links():
    expected_labels = (
        "¿Cómo empezar?",
        "Manual de usuario",
        "Guía de prueba",
        "Archivos de prueba",
        "API y documentación técnica",
        "Repositorio GitHub",
    )

    for label in expected_labels:
        assert label in DASHBOARD_SOURCE


def test_operational_metadata_is_rendered_as_read_only_content():
    assert "Run ID · sólo lectura" in DASHBOARD_SOURCE
    assert "Estado · sólo lectura" in DASHBOARD_SOURCE
    assert "<small>API</small><strong>Operativa</strong>" in DASHBOARD_SOURCE
    assert 'st.text_input("Estado"' not in DASHBOARD_SOURCE
    assert 'st.text_input("API"' not in DASHBOARD_SOURCE
