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
        "¿Para qué sirven los datos de la carga?",
        "Manual de usuario",
        "Guía de prueba",
        "Archivos de prueba",
        "API y documentación técnica",
        "Repositorio GitHub",
    )

    for label in expected_labels:
        assert label in DASHBOARD_SOURCE

    for explanation in (
        "identifica a quién pertenecen los datos",
        "detección de duplicados",
        "facilita su seguimiento en el tiempo",
        "Estos valores no se obtienen del archivo",
    ):
        assert explanation in DASHBOARD_SOURCE


def test_operational_metadata_is_rendered_as_read_only_content():
    assert "Run ID · sólo lectura" in DASHBOARD_SOURCE
    assert "Estado · sólo lectura" in DASHBOARD_SOURCE
    assert 'st.text_input("Estado"' not in DASHBOARD_SOURCE
    assert 'st.text_input("API"' not in DASHBOARD_SOURCE


def test_run_catalog_exposes_filters_and_manual_fallback():
    for label in (
        "Filtrar por Organización",
        "Filtrar por Comunidad",
        "Ejecución disponible",
        "Abrir ejecución seleccionada",
        "Ingresar un Run ID manualmente",
    ):
        assert label in DASHBOARD_SOURCE

    assert "display_label" in DASHBOARD_SOURCE
    assert "list_runs" in DASHBOARD_SOURCE


def test_repeated_file_offers_recovery_or_reprocessing():
    for label in (
        "Este archivo ya fue procesado",
        "Recuperar ejecución existente",
        "Procesar nuevamente y actualizar resultados",
        "Recuperar esta ejecución",
        "Procesar nuevamente",
    ):
        assert label in DASHBOARD_SOURCE
