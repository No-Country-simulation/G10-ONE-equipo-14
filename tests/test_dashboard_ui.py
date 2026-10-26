"""Regression checks for the dashboard's visual shell and help affordances."""

from pathlib import Path

from dashboard.visualizations import (
    sentiment_distribution_html,
    topics_card_html,
)


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

    assert "docs/manuales/CommunityLab_Manual_Usuario_Final.pdf" in DASHBOARD_SOURCE
    assert "docs/manuales/CommunityLab_Guia_Prueba_Operador.pdf" in DASHBOARD_SOURCE
    assert 'st.link_button("💻 Repositorio GitHub", REPOSITORY_URL' in DASHBOARD_SOURCE


def test_operational_metadata_is_rendered_as_read_only_content():
    assert "Run ID · sólo lectura" in DASHBOARD_SOURCE
    assert "Estado · sólo lectura" not in DASHBOARD_SOURCE
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


def test_main_dashboard_sections_are_collapsible_with_upload_open_by_default():
    assert (
        '"Cargar interacciones",\n    expanded=True,\n    key="process-section-upload",'
        in DASHBOARD_SOURCE
    )
    assert (
        '"Recuperar una ejecución",\n'
        "    expanded=False,\n"
        '    key="process-section-recovery",'
    ) in DASHBOARD_SOURCE
    assert (
        '"Resultado",\n        expanded=True,\n        key="process-section-result",'
    ) in DASHBOARD_SOURCE
    assert (
        "if result:\n"
        "    with st.expander(\n"
        '        "Análisis, oportunidades y curaduría",\n'
        "        expanded=result is not None," in DASHBOARD_SOURCE
    )


def test_main_process_section_titles_are_prominent():
    for key in (
        "upload",
        "recovery",
        "result",
        "analysis",
    ):
        assert (
            f'.st-key-process-section-{key} > div[data-testid="stExpander"] > details > summary'
            in DASHBOARD_SOURCE
        )
    assert '[class*="st-key-process-section-"]' not in DASHBOARD_SOURCE
    assert "font-size: 1.1rem;" in DASHBOARD_SOURCE
    assert "text-transform: uppercase;" in DASHBOARD_SOURCE
    assert (
        "str(analysis.get('sentiment', 'sin sentimiento')).capitalize()"
        in DASHBOARD_SOURCE
    )
    assert ".cl-alert-details summary {" in DASHBOARD_SOURCE
    for key in (
        "process-section-upload",
        "process-section-recovery",
        "process-section-result",
        "process-section-analysis",
    ):
        assert key in DASHBOARD_SOURCE


def test_sentiment_chart_compares_detected_sentiments():
    assert 'sentiment_distribution_html(result.get("analyses", []))' in DASHBOARD_SOURCE
    assert "Sentimiento predominante" not in DASHBOARD_SOURCE
    chart = sentiment_distribution_html(
        [
            {"sentiment": "positive"},
            {"sentiment": "positive"},
            {"sentiment": "neutral"},
            {"sentiment": "negative"},
        ]
    )

    assert "4 análisis" in chart
    assert "Positivo" in chart and 'aria-valuenow="2"' in chart
    assert "Neutral" in chart and chart.count('aria-valuenow="1"') == 2
    assert "Negativo" in chart and chart.count("25.0%</span>") == 2
    assert "50.0%</span>" in chart
    assert chart.count('role="progressbar"') == 3
    assert chart.count("Mayor porcentaje") == 1


def test_sentiment_chart_highlights_tied_highest_percentages():
    chart = sentiment_distribution_html(
        [
            {"sentiment": "positive"},
            {"sentiment": "neutral"},
            {"sentiment": "negative"},
        ]
    )

    assert chart.count("Mayor porcentaje") == 3


def test_sentiment_chart_handles_empty_and_escapes_unexpected_labels():
    empty_chart = sentiment_distribution_html([])
    unexpected_chart = sentiment_distribution_html(
        [{"sentiment": "<script>alert(1)</script>"}]
    )

    assert "No hay datos de sentimiento" in empty_chart
    assert "&lt;script&gt;" in unexpected_chart
    assert "<script>" not in unexpected_chart


def test_insight_cards_are_aligned_with_chart_left_and_topics_right():
    topics = topics_card_html(["FastAPI", "soporte"])
    chart_render = DASHBOARD_SOURCE.index(
        'sentiment_distribution_html(result.get("analyses", []))'
    )
    topics_render = DASHBOARD_SOURCE.index("topics_card_html(top_topics)")
    run_id_render = DASHBOARD_SOURCE.index("components.html(run_meta_html, height=120)")
    right_column = DASHBOARD_SOURCE.index("with insight_columns[1]:")
    right_stack_end = DASHBOARD_SOURCE.index(
        'if result.get("record_errors")', right_column
    )

    assert "Temas principales" in topics
    assert 'class="cl-topic-card"' in topics
    assert 'st.columns(2, gap="large", vertical_alignment="top")' in DASHBOARD_SOURCE
    assert chart_render < right_column < topics_render < run_id_render < right_stack_end
    assert (
        'with st.container(gap="medium"):'
        in DASHBOARD_SOURCE[right_column:right_stack_end]
    )
    assert "Estado · sólo lectura" not in DASHBOARD_SOURCE


def test_result_metrics_and_chart_use_native_vertical_spacing():
    result_layout = DASHBOARD_SOURCE.index('with st.container(gap="small"):')
    metrics = DASHBOARD_SOURCE.index("columns = st.columns(5)", result_layout)
    chart = DASHBOARD_SOURCE.index(
        'sentiment_distribution_html(result.get("analyses", []))',
        metrics,
    )
    bottom_spacing = DASHBOARD_SOURCE.index('st.space("small")', chart)

    assert metrics < chart < bottom_spacing
    assert "cl-summary-row-spacer" not in DASHBOARD_SOURCE
