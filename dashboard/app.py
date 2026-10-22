import json
import os
from datetime import date
from html import escape
from pathlib import Path
from uuid import uuid4

import requests
import streamlit as st
import streamlit.components.v1 as components

from api_client import (
    api_error_message,
    decide_asset,
    edit_asset,
    get_health,
    get_run,
    list_runs,
    list_open_alerts,
    list_assets,
    list_pending_assets,
    mutation_headers,
    publish_asset,
)


API_URL = os.getenv("API_URL", "http://api:8000").rstrip("/")
API_WRITE_KEY = os.getenv("API_WRITE_KEY")
PUBLIC_API_URL = os.getenv(
    "PUBLIC_API_URL",
    "http://localhost:8000" if API_URL == "http://api:8000" else API_URL,
).rstrip("/")
REPOSITORY_URL = "https://github.com/No-Country-simulation/G10-ONE-equipo-14"
MANUAL_URL = f"{REPOSITORY_URL}/blob/main/docs/MANUAL_USUARIO.md"
TEST_GUIDE_URL = (
    f"{REPOSITORY_URL}/blob/main/docs/sets_pruebas/GUIA_PRUEBA_FUNCIONAL.md"
)
TEST_SETS_URL = f"{REPOSITORY_URL}/tree/main/docs/sets_pruebas"
LOGO_PATH = Path(__file__).parent / "assets" / "communitylab-logo.svg"
PROCESS_REQUEST_TIMEOUT = 300


def _short_reference(value):
    """Return a compact identifier suitable for the dashboard summary."""
    if not value:
        return "sin referencia"
    return str(value).split("-")[0]


def _opportunity_kind_label(kind):
    labels = {
        "educational_content": "Contenido educativo",
        "success_content": "Experiencia positiva",
        "support_content": "Contenido de soporte",
    }
    return labels.get(kind, str(kind or "Oportunidad").replace("_", " ").capitalize())


def _opportunity_status_label(status):
    labels = {
        "PENDING": "Pendiente",
        "REVIEW_REQUIRED": "Requiere revisión",
        "BLOCKED": "Bloqueada",
    }
    return labels.get(
        status, str(status or "Estado desconocido").replace("_", " ").capitalize()
    )


def _opportunity_reason_label(reason):
    reason = str(reason or "")
    if "personally identifiable information" in reason:
        return "Contiene datos personales; no debe publicarse."
    if "author opted out" in reason:
        return "La persona no autorizó la publicación."
    if "routed to an internal alert" in reason:
        return "Se derivó a una alerta interna."
    if "confidence is below" in reason:
        return "Requiere revisión humana por baja confianza."
    if "relevance is below" in reason:
        return "Requiere revisión humana por baja relevancia."
    if "Qualified by backend content rules" in reason:
        return "Cumple los criterios para preparar contenido."
    return reason or "Sin explicación disponible."


def _alert_message_label(message):
    if "Negative sentiment or frustration" in str(message or ""):
        return "La interacción expresa una experiencia negativa o frustración."
    return message or "Alerta que requiere atención interna."


def _render_pending_asset_editors(assets_to_render, all_pending_assets):
    for asset in assets_to_render:
        with st.container(border=True):
            title = st.text_input(
                "Título", value=asset["title"], key=f"title-{asset['id']}"
            )
            body = st.text_area(
                "Contenido", value=asset["body"], key=f"body-{asset['id']}"
            )
            if asset["channel"] == "FAQ":
                st.caption(
                    "La respuesta puede incluir orientación general de Gemini. "
                    "Las fuentes muestran de dónde surgió la pregunta; revisá y "
                    "editá el texto antes de aprobarlo."
                )
            st.caption(
                f"{asset['channel']} · {asset['status']} · versión {asset['version']}"
            )
            with st.expander("Evidencia y fuentes"):
                source_ids = asset.get("source_interaction_ids", [])
                if source_ids:
                    st.caption("Interacciones fuente: " + ", ".join(source_ids))
                for evidence in asset.get("evidence", []):
                    st.markdown(f"> {evidence['excerpt']}")
                    st.caption(f"Fuente: {evidence['source_interaction_id']}")
                if not source_ids and not asset.get("evidence"):
                    st.warning("Este activo histórico no contiene fuentes visibles.")
            save, approve_publish, reject = st.columns(3)
            if save.button("Guardar", key=f"save-{asset['id']}"):
                try:
                    asset.update(
                        edit_asset(
                            API_URL,
                            asset["id"],
                            title=title,
                            body=body,
                            editor="dashboard",
                            api_write_key=API_WRITE_KEY,
                        )
                    )
                    st.success("Nueva versión guardada.")
                except requests.RequestException as exc:
                    st.error(f"No se pudo guardar el activo: {api_error_message(exc)}")
            if approve_publish.button(
                "Aprobar y publicar",
                key=f"approve-publish-{asset['id']}",
                type="primary",
            ):
                approved = False
                try:
                    decide_asset(
                        API_URL,
                        asset["id"],
                        decision="approve",
                        reviewer="dashboard",
                        api_write_key=API_WRITE_KEY,
                    )
                    approved = True
                    st.session_state["pending_assets"] = [
                        item for item in all_pending_assets if item["id"] != asset["id"]
                    ]
                    receipt = publish_asset(
                        API_URL,
                        asset["id"],
                        api_write_key=API_WRITE_KEY,
                    )
                    st.session_state["last_publish_receipt"] = receipt
                    st.success(
                        "Activo aprobado y publicado en el almacenamiento configurado."
                    )
                except requests.RequestException as exc:
                    if approved:
                        st.warning(
                            "El activo quedó aprobado, pero no se pudo publicar. "
                            "Podés reintentar desde la sección de aprobados."
                        )
                    st.error(
                        f"No se pudo completar la operación: {api_error_message(exc)}"
                    )
            if reject.button("Rechazar", key=f"reject-{asset['id']}"):
                try:
                    decide_asset(
                        API_URL,
                        asset["id"],
                        decision="reject",
                        reviewer="dashboard",
                        api_write_key=API_WRITE_KEY,
                    )
                    st.session_state["pending_assets"] = [
                        item for item in all_pending_assets if item["id"] != asset["id"]
                    ]
                    st.warning("Activo rechazado y retirado de la cola.")
                    st.rerun()
                except requests.RequestException as exc:
                    st.error(f"No se pudo rechazar el activo: {api_error_message(exc)}")


st.set_page_config(
    page_title="CommunityLab · Inteligencia para comunidades",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root {
        --cl-navy: #0f172a;
        --cl-slate: #475569;
        --cl-border: #dbe4ee;
        --cl-teal: #0f766e;
        --cl-teal-soft: #ecfdf5;
        --cl-blue: #2563eb;
        --cl-surface: #f8fafc;
    }
    .stApp {
        color: var(--cl-navy);
        background:
            radial-gradient(circle at 88% 5%, rgba(37, 99, 235, .08), transparent 24rem),
            linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
    }
    [data-testid="stSidebar"] {
        color: var(--cl-navy);
        background: linear-gradient(180deg, #f8fafc 0%, #eef6f6 100%);
        border-right: 1px solid var(--cl-border);
    }
    [data-testid="stSidebar"] [data-testid="stImage"] img {
        max-width: 240px;
    }
    .block-container {
        max-width: 1280px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }
    .cl-hero {
        padding: 2.1rem 2.25rem;
        margin-bottom: 1.6rem;
        border: 1px solid rgba(15, 118, 110, .18);
        border-radius: 24px;
        background: linear-gradient(115deg, #f0fdfa 0%, #eff6ff 58%, #ffffff 100%);
        box-shadow: 0 18px 45px rgba(15, 23, 42, .07);
    }
    .cl-eyebrow {
        color: var(--cl-teal);
        font-size: .78rem;
        font-weight: 800;
        letter-spacing: .12em;
        text-transform: uppercase;
        margin-bottom: .55rem;
    }
    .cl-hero h1 {
        color: var(--cl-navy);
        font-size: clamp(2rem, 4vw, 3.4rem);
        line-height: 1.03;
        margin: 0 0 .7rem 0;
        letter-spacing: -.04em;
    }
    .cl-hero p {
        color: var(--cl-slate);
        font-size: 1.03rem;
        max-width: 760px;
        margin: 0;
    }
    .cl-status {
        display: flex;
        align-items: center;
        gap: .65rem;
        padding: .75rem .9rem;
        border-radius: 12px;
        font-weight: 700;
        margin: .35rem 0 .65rem 0;
    }
    .cl-status--ok { color: #166534; background: #dcfce7; border: 1px solid #bbf7d0; }
    .cl-status--wait { color: #92400e; background: #fef3c7; border: 1px solid #fde68a; }
    .cl-dot { width: .58rem; height: .58rem; border-radius: 50%; background: currentColor; }
    .cl-readonly {
        padding: 1rem;
        margin: .4rem 0;
        border: 1px solid var(--cl-border);
        border-radius: 16px;
        background: #fff;
        box-shadow: 0 7px 20px rgba(15, 23, 42, .04);
    }
    .cl-readonly small { display: block; color: #64748b; margin-bottom: .2rem; }
    .cl-readonly strong { color: var(--cl-navy); overflow-wrap: anywhere; }
    div[data-testid="stMetric"] {
        border: 1px solid var(--cl-border);
        background: #fff;
        padding: 1rem;
        border-radius: 16px;
        box-shadow: 0 7px 20px rgba(15, 23, 42, .04);
    }
    .cl-summary-card {
        background: #fff !important;
        box-sizing: border-box;
        height: 137px;
        padding: 1rem;
        border: 1px solid var(--cl-border);
        border-radius: 16px;
        box-shadow: 0 7px 20px rgba(15, 23, 42, .04);
        overflow: hidden;
    }
    .cl-summary-label {
        color: #475569;
        font-size: .875rem;
        margin-bottom: .25rem;
    }
    .cl-summary-value {
        color: var(--cl-navy);
        font-size: clamp(1.25rem, 2vw, 2rem);
        line-height: 1.15;
        max-height: 2.3em;
        overflow-wrap: anywhere;
        overflow: hidden;
    }
    .cl-summary-empty {
        color: #64748b;
        font-size: 1rem;
    }
    .cl-summary-status {
        font-size: 1.1rem;
        font-weight: 700;
    }
    .cl-summary-row-spacer {
        height: 1rem;
    }
    .cl-topic-list {
        display: flex;
        flex-wrap: wrap;
        gap: .45rem;
        padding: .15rem 0 .3rem;
        max-height: 70px;
        overflow-y: auto;
    }
    .cl-topic-chip {
        display: inline-flex;
        max-width: 100%;
        padding: .3rem .55rem;
        border: 1px solid var(--cl-border);
        border-radius: 999px;
        background: var(--cl-surface);
        color: var(--cl-slate);
        font-size: .78rem;
        line-height: 1.25;
        white-space: normal;
        overflow-wrap: anywhere;
    }
    div[data-testid="stExpander"], div[data-testid="stFileUploader"] section {
        border-color: var(--cl-border);
        border-radius: 14px;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(90deg, var(--cl-teal), var(--cl-blue));
        color: #ffffff;
        border: none;
        box-shadow: 0 8px 18px rgba(37, 99, 235, .18);
    }
    .stTabs [data-baseweb="tab-list"] { gap: .45rem; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px 10px 0 0;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    h2, h3 { color: var(--cl-navy); letter-spacing: -.02em; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <section class="cl-hero">
      <div class="cl-eyebrow">Inteligencia para comunidades digitales</div>
      <h1>Convertí conversaciones en acciones útiles.</h1>
      <p>Centralizá interacciones, detectá oportunidades y prepará contenido
      trazable con revisión humana antes de su publicación.</p>
    </section>
    """,
    unsafe_allow_html=True,
)


def process_upload(
    uploaded_file,
    organization_id: str,
    community_id: str,
    reference_period: str,
) -> dict:
    idempotency_key = f"dashboard-{uuid4()}"
    headers = {"Idempotency-Key": idempotency_key, **mutation_headers(API_WRITE_KEY)}
    content = uploaded_file.getvalue()

    if uploaded_file.name.lower().endswith(".csv"):
        response = requests.post(
            f"{API_URL}/api/v1/process/csv",
            headers=headers,
            data={
                "organization_id": organization_id,
                "community_id": community_id,
                "reference_period": reference_period,
                "requested_assets": "LINKEDIN,FAQ",
            },
            files={"file": (uploaded_file.name, content, "text/csv")},
            timeout=PROCESS_REQUEST_TIMEOUT,
        )
    else:
        interactions = json.loads(content.decode("utf-8-sig"))
        if isinstance(interactions, dict) and "interactions" in interactions:
            payload = interactions
            payload.update(
                organization_id=organization_id,
                community_id=community_id,
                reference_period=reference_period,
                source_name=uploaded_file.name,
            )
            payload.setdefault("requested_assets", ["LINKEDIN", "FAQ"])
        else:
            payload = {
                "schema_version": "v1",
                "organization_id": organization_id,
                "community_id": community_id,
                "reference_period": reference_period,
                "source_name": uploaded_file.name,
                "requested_assets": ["LINKEDIN", "FAQ"],
                "interactions": interactions,
            }

        response = requests.post(
            f"{API_URL}/api/v1/process",
            headers=headers,
            json=payload,
            timeout=PROCESS_REQUEST_TIMEOUT,
        )

    response.raise_for_status()
    return response.json()


health = None
health_error = None
try:
    health = get_health(API_URL)
except requests.RequestException as error:
    health_error = api_error_message(error)

with st.sidebar:
    st.image(str(LOGO_PATH), width="stretch")
    st.caption("Centro de operación y ayuda")

    st.subheader("Estado del sistema")
    if health:
        st.markdown(
            '<div class="cl-status cl-status--ok"><span class="cl-dot"></span>'
            "Servicios disponibles</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="cl-readonly"><small>API</small><strong>Operativa</strong></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="cl-readonly"><small>PostgreSQL</small>'
            f"<strong>{escape(str(health.get('database', 'desconocido')))}</strong></div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="cl-status cl-status--wait"><span class="cl-dot"></span>'
            "Servicios iniciando</div>",
            unsafe_allow_html=True,
        )
        st.caption(
            "Render Free puede tardar cerca de un minuto en despertar. "
            "Esperá unos segundos y recargá la página."
        )
        if health_error:
            st.caption(health_error)

    with st.expander("¿Cómo empezar?", expanded=False):
        st.markdown(
            "1. Identificá la organización, la comunidad y el período.\n"
            "2. Seleccioná el archivo JSON o CSV con las interacciones.\n"
            "3. Procesá la carga y guardá el Run ID para consultarla luego.\n"
            "4. Revisá los análisis, oportunidades, alertas y borradores."
        )

    with st.expander("¿Para qué sirven los datos de la carga?", expanded=True):
        st.markdown(
            "**Organización** identifica a quién pertenecen los datos y permite "
            "separarlos de los de otras organizaciones. Ejemplo: `one`.\n\n"
            "**Comunidad** identifica el grupo que se analiza. También delimita la "
            "detección de duplicados: una interacción repetida se compara dentro de "
            "la misma comunidad. Ejemplo: `g10-equipo-14`.\n\n"
            "**Período de referencia** indica a qué semana o ciclo corresponde la "
            "carga y facilita su seguimiento en el tiempo. Ejemplo: `2026-W42`.\n\n"
            "Estos valores no se obtienen del archivo: el usuario los completa para "
            "dar contexto y trazabilidad al procesamiento."
        )

    st.subheader("Ayuda y documentación")
    st.link_button("📘 Manual de usuario", MANUAL_URL, width="stretch")
    st.link_button("🧪 Guía de prueba", TEST_GUIDE_URL, width="stretch")
    st.link_button("📂 Archivos de prueba", TEST_SETS_URL, width="stretch")

    st.subheader("Accesos rápidos")
    st.link_button(
        "⚙️ API y documentación técnica",
        f"{PUBLIC_API_URL}/docs",
        width="stretch",
    )
    st.link_button("💻 Repositorio GitHub", REPOSITORY_URL, width="stretch")
    st.markdown("[Ir a cargar interacciones](#1-cargar-interacciones)")
    st.markdown("[Ir a análisis y curaduría](#4-analisis-oportunidades-y-curaduria)")

run_catalog = []
run_catalog_error = None
if health:
    try:
        run_catalog = list_runs(API_URL, api_write_key=API_WRITE_KEY)
    except requests.RequestException as error:
        run_catalog_error = api_error_message(error)

st.subheader("1. Cargar interacciones", anchor="1-cargar-interacciones")
st.caption(
    "Identifican a quién pertenecen las interacciones, qué comunidad se analiza "
    "y a qué período corresponden. Abrí la ayuda lateral para ver ejemplos."
)
left, middle, right = st.columns(3)
with left:
    organization_id = st.text_input(
        "Organización",
        value="one",
        help="Agrupa las comunidades y forma parte de la trazabilidad.",
    )
with middle:
    community_id = st.text_input(
        "Comunidad",
        value="g10-equipo-14",
        help="La deduplicación se aplica dentro de esta comunidad.",
    )
with right:
    today = date.today().isocalendar()
    default_period = f"{today.year}-W{today.week:02d}"
    reference_period = st.text_input(
        "Período de referencia",
        value=default_period,
        help="Etiqueta temporal del lote, por ejemplo 2026-W42.",
    )

uploaded_file = st.file_uploader(
    "Archivo de interacciones",
    type=["json", "csv"],
    help="Podés usar data/sample_interactions.json o data/sample_interactions.csv.",
)

upload_recovery_run_id = ""
process_upload_requested = False
matching_file_runs = []
if uploaded_file is not None:
    uploaded_name = Path(uploaded_file.name).name.casefold()
    matching_file_runs = [
        item
        for item in run_catalog
        if item["organization_id"] == organization_id
        and item["community_id"] == community_id
        and item.get("source_name")
        and Path(str(item["source_name"])).name.casefold() == uploaded_name
    ]

if matching_file_runs:
    st.warning(
        "Este archivo ya fue procesado para la Organización y Comunidad "
        "seleccionadas. Elegí si querés recuperar un resultado o procesarlo "
        "nuevamente."
    )
    matching_runs_by_id = {str(item["run_id"]): item for item in matching_file_runs}
    existing_run_id = st.selectbox(
        "Ejecución anterior del archivo",
        list(matching_runs_by_id),
        format_func=lambda value: matching_runs_by_id[value]["display_label"],
    )
    repeated_file_action = st.radio(
        "¿Qué querés hacer?",
        (
            "Recuperar ejecución existente",
            "Procesar nuevamente y actualizar resultados",
        ),
        horizontal=True,
    )
    if repeated_file_action == "Recuperar ejecución existente":
        if st.button("Recuperar esta ejecución"):
            upload_recovery_run_id = existing_run_id
    else:
        st.caption(
            "Se creará un Run nuevo, se reutilizarán las interacciones ya "
            "guardadas y se volverán a generar análisis y resultados."
        )
        process_upload_requested = st.button(
            "Procesar nuevamente",
            type="primary",
            disabled=health is None,
        )
else:
    process_upload_requested = st.button(
        "Procesar archivo",
        type="primary",
        disabled=uploaded_file is None or health is None,
    )

if process_upload_requested:
    try:
        with st.spinner("Guardando interacciones en PostgreSQL..."):
            st.session_state["process_result"] = process_upload(
                uploaded_file,
                organization_id,
                community_id,
                reference_period,
            )
            st.session_state.pop("pending_assets", None)
        st.success("Carga procesada correctamente.")
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        st.error(f"El archivo JSON no se pudo leer: {exc}")
    except requests.HTTPError as exc:
        detail = api_error_message(exc)
        st.error(f"La API rechazó la carga: {detail}")
    except requests.RequestException as exc:
        st.error(api_error_message(exc))

st.subheader("2. Recuperar una ejecución", anchor="2-recuperar-una-ejecucion")
st.caption(
    "Filtrá por Organización y Comunidad, y elegí una ejecución por su archivo, "
    "fecha y Run ID."
)

selected_run_id = ""
if run_catalog:
    organization_options = ["Todas"] + sorted(
        {item["organization_id"] for item in run_catalog}
    )
    filter_organization, filter_community = st.columns(2)
    with filter_organization:
        selected_organization = st.selectbox(
            "Filtrar por Organización",
            organization_options,
        )

    organization_runs = [
        item
        for item in run_catalog
        if selected_organization == "Todas"
        or item["organization_id"] == selected_organization
    ]
    community_options = ["Todas"] + sorted(
        {item["community_id"] for item in organization_runs}
    )
    with filter_community:
        selected_community = st.selectbox(
            "Filtrar por Comunidad",
            community_options,
        )

    filtered_runs = [
        item
        for item in organization_runs
        if selected_community == "Todas" or item["community_id"] == selected_community
    ]
    runs_by_id = {str(item["run_id"]): item for item in filtered_runs}
    selected_run_id = st.selectbox(
        "Ejecución disponible",
        [""] + list(runs_by_id),
        format_func=lambda value: (
            "Seleccioná una ejecución"
            if not value
            else runs_by_id[value]["display_label"]
        ),
        help="La etiqueta termina siempre con el Run ID completo.",
    )
elif run_catalog_error:
    st.warning(f"No se pudo cargar la lista de ejecuciones: {run_catalog_error}")
elif health:
    st.info("Todavía no hay ejecuciones persistidas para seleccionar.")

load_selected_run = st.button(
    "Abrir ejecución seleccionada",
    disabled=not selected_run_id or health is None,
)

with st.expander("Ingresar un Run ID manualmente"):
    manual_run_id = st.text_input(
        "Run ID manual",
        placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
        help="Usá esta opción si la ejecución no aparece en la lista.",
    )
    load_manual_run = st.button(
        "Buscar Run ID manual",
        disabled=not manual_run_id.strip() or health is None,
    )

if upload_recovery_run_id:
    requested_run_id = upload_recovery_run_id
elif load_selected_run:
    requested_run_id = selected_run_id
elif load_manual_run:
    requested_run_id = manual_run_id
else:
    requested_run_id = ""

if requested_run_id:
    try:
        with st.spinner("Recuperando la ejecución desde PostgreSQL..."):
            st.session_state["process_result"] = get_run(
                API_URL,
                requested_run_id,
            )
        st.success("Ejecución recuperada correctamente.")
    except ValueError:
        st.error("El Run ID debe ser un UUID válido.")
    except requests.HTTPError as exc:
        if exc.response is not None and exc.response.status_code == 404:
            st.error("No existe una ejecución con ese Run ID.")
        elif exc.response is not None and exc.response.status_code == 409:
            st.warning("La ejecución todavía se está procesando.")
        else:
            detail = api_error_message(exc)
            st.error(f"La API no pudo recuperar la ejecución: {detail}")
    except requests.RequestException as exc:
        st.error(api_error_message(exc))

result = st.session_state.get("process_result")
if result:
    st.subheader("3. Resultado persistido", anchor="3-resultado-persistido")
    summary = result["summary"]
    columns = st.columns(5)
    columns[0].metric("Recibidas", summary["received"])
    columns[1].metric("Aceptadas", summary["accepted"])
    columns[2].metric("Duplicadas", summary["duplicates"])
    columns[3].metric("Reprocesadas", summary.get("reprocessed", 0))
    columns[4].metric("Con errores", summary["errors"])
    st.markdown('<div class="cl-summary-row-spacer"></div>', unsafe_allow_html=True)
    insight_columns = st.columns(2)
    sentiment = escape(str(summary.get("predominant_sentiment") or "Sin datos"))
    insight_columns[0].markdown(
        '<div class="cl-summary-card">'
        '<div class="cl-summary-label">Sentimiento predominante</div>'
        f'<div class="cl-summary-value">{sentiment}</div></div>',
        unsafe_allow_html=True,
    )
    top_topics = summary.get("top_topics", [])
    if top_topics:
        topic_chips = "".join(
            f'<span class="cl-topic-chip">{escape(str(topic))}</span>'
            for topic in top_topics
        )
    else:
        topic_chips = '<span class="cl-summary-empty">Sin datos</span>'
    insight_columns[1].markdown(
        '<div class="cl-summary-card">'
        '<div class="cl-summary-label">Temas principales</div>'
        f'<div class="cl-topic-list">{topic_chips}</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="cl-summary-row-spacer"></div>', unsafe_allow_html=True)
    run_meta, status_meta = st.columns(2)
    run_id = str(result["run_id"])
    run_id_json = json.dumps(run_id).replace("<", "\\u003c")
    run_meta_html = f"""
    <div class="run-card">
      <div class="run-label">Run ID · sólo lectura</div>
      <code class="run-value">{escape(run_id)}</code>
      <button class="copy-button" type="button" aria-label="Copiar Run ID">
        Copiar
      </button>
      <span class="copy-feedback" aria-live="polite"></span>
    </div>
    <style>
      * {{ box-sizing: border-box; }}
      body {{ margin: 0; font-family: sans-serif; color: #0f172a; }}
      .run-card {{
        height: 137px; padding: 1rem; position: relative; overflow: hidden;
        border: 1px solid #dbe4ee; border-radius: 16px; background: #fff;
        box-shadow: 0 7px 20px rgba(15, 23, 42, .04);
      }}
      .run-label {{ color: #475569; font-size: .875rem; margin-bottom: .55rem; }}
      .run-value {{
        display: block; max-width: calc(100% - 5.5rem); overflow-wrap: anywhere;
        color: #0f172a; font: .9rem/1.5 monospace;
      }}
      .copy-button {{
        position: absolute; top: .7rem; right: .7rem; display: inline-flex;
        align-items: center; justify-content: center; min-height: 2rem;
        padding: .35rem .65rem; border: 1px solid #dbe4ee; border-radius: 8px;
        background: #fff; color: #0f172a; font: 600 .8rem sans-serif;
        cursor: pointer;
      }}
      .copy-button:hover {{ background: #f8fafc; }}
      .copy-feedback {{ color: #166534; font-size: .8rem; margin-left: .5rem; }}
    </style>
    <script>
      const runId = {run_id_json};
      const copyButton = document.querySelector(".copy-button");
      const copyFeedback = document.querySelector(".copy-feedback");
      async function copyRunId() {{
        let copied = false;
        try {{
          await window.parent.navigator.clipboard.writeText(runId);
          copied = true;
        }} catch (error) {{
          // Fall back for browsers that block clipboard access in iframes.
        }}
        if (!copied) {{
          const textArea = document.createElement("textarea");
          textArea.value = runId;
          textArea.style.position = "fixed";
          textArea.style.opacity = "0";
          document.body.appendChild(textArea);
          textArea.select();
          copied = document.execCommand("copy");
          textArea.remove();
        }}
        copyButton.textContent = copied ? "Copiado" : "Copiar";
        copyFeedback.textContent = copied
          ? "Run ID copiado"
          : "No se pudo copiar";
        window.setTimeout(() => {{
          copyButton.textContent = "Copiar";
          copyFeedback.textContent = "";
        }}, 1800);
      }}
      copyButton.addEventListener("click", copyRunId);
    </script>
    """
    with run_meta:
        components.html(run_meta_html, height=137)
    status_meta.markdown(
        '<div class="cl-summary-card">'
        '<div class="cl-summary-label">Estado · sólo lectura</div>'
        f'<div class="cl-summary-value cl-summary-status">'
        f"{escape(str(result['status']))}</div></div>",
        unsafe_allow_html=True,
    )

    if result.get("record_errors"):
        st.warning("Algunos registros no pudieron procesarse.")
        st.dataframe(result["record_errors"], width="stretch")

st.subheader(
    "4. Análisis, oportunidades y curaduría",
    anchor="4-analisis-oportunidades-y-curaduria",
)
st.caption(
    "Análisis, oportunidades, alertas y evidencias son de consulta. "
    "Sólo el título y contenido de un borrador pendiente pueden editarse."
)
analysis_tab, opportunities_tab, alerts_tab, assets_tab = st.tabs(
    ["Análisis", "Oportunidades", "Alertas internas", "Generación de Contenido"]
)
with analysis_tab:
    if result:
        analyses = result.get("analyses", [])
        if not analyses:
            st.info("La ejecución no contiene análisis.")
        for index, analysis in enumerate(analyses, start=1):
            label = (
                f"{index}. {analysis.get('sentiment', 'sin sentimiento')} · "
                f"confianza {analysis.get('confidence', 0):.2f}"
            )
            with st.expander(label):
                st.write("**Temas:**", ", ".join(analysis.get("topics", [])) or "—")
                st.write(
                    "**Entidades:**", ", ".join(analysis.get("entities", [])) or "—"
                )
                st.caption(
                    f"Modelo: {analysis.get('model', '—')} · "
                    f"Prompt: {analysis.get('prompt_version', '—')}"
                )
                st.write("**Evidencia y fuentes**")
                for evidence in analysis.get("evidence", []):
                    st.markdown(f"> {evidence['excerpt']}")
                    st.caption(
                        f"Interacción fuente: {evidence['source_interaction_id']}"
                    )
    else:
        st.info("Procesá un archivo para ver análisis.")
with opportunities_tab:
    if result:
        opportunities = result.get("opportunities", [])
        if opportunities:
            st.caption(f"{len(opportunities)} oportunidad(es) detectada(s).")
            evidence_by_source = {
                evidence.get("source_interaction_id"): evidence.get("excerpt", "")
                for analysis in result.get("analyses", [])
                for evidence in analysis.get("evidence", [])
            }
            for opportunity in opportunities:
                source_ids = opportunity.get("source_ids", [])
                source_reference = (
                    _short_reference(source_ids[0]) if source_ids else None
                )
                with st.container(border=True):
                    st.markdown(
                        f"**{_opportunity_kind_label(opportunity.get('kind'))}**"
                    )
                    reason = opportunity.get("reason", "")
                    if "Qualified by backend content rules" in str(reason):
                        source_message = (
                            evidence_by_source.get(source_ids[0], "")
                            if source_ids
                            else ""
                        )
                        if source_message:
                            st.markdown(
                                f"<em>“{escape(str(source_message))}”</em>",
                                unsafe_allow_html=True,
                            )
                        else:
                            st.write(_opportunity_reason_label(reason))
                    else:
                        st.write(_opportunity_reason_label(reason))
                    reference_label = (
                        f" · Referencia: `{source_reference}`"
                        if source_reference
                        else ""
                    )
                    st.caption(
                        f"{_opportunity_status_label(opportunity.get('status'))}"
                        f"{reference_label}"
                    )
        else:
            st.info("La ejecución no generó oportunidades.")
    else:
        st.info("Procesá un archivo para ver oportunidades.")
with alerts_tab:
    try:
        open_alerts = list_open_alerts(API_URL) if health else []
        if open_alerts:
            st.warning(f"{len(open_alerts)} alerta(s) interna(s) abierta(s).")
            for alert in open_alerts:
                severity = str(alert.get("severity", "MEDIUM")).upper()
                severity_label = "Alta" if severity == "HIGH" else "Media"
                with st.container(border=True):
                    st.markdown(f"**Alerta de prioridad {severity_label.lower()}**")
                    st.write(_alert_message_label(alert.get("message")))
                    excerpt = alert.get("excerpt")
                    if excerpt:
                        st.markdown(f"> {excerpt}")
                    st.caption(
                        f"Abierta · Referencia: `{_short_reference(alert.get('interaction_id'))}`"
                    )
        else:
            st.info("No hay alertas internas abiertas.")
    except requests.RequestException as exc:
        st.error(
            f"No se pudieron recuperar las alertas internas: {api_error_message(exc)}"
        )
with assets_tab:
    queue_run_id = result.get("run_id") if result else None
    queue_header, queue_action = st.columns([4, 1])
    queue_header.caption(
        "Cola persistente: se muestran los borradores de la ejecución actual."
    )
    refresh_queue = queue_action.button("Actualizar cola", width="stretch")
    queue_changed = st.session_state.get("pending_assets_run_id") != queue_run_id
    if "pending_assets" not in st.session_state or refresh_queue or queue_changed:
        try:
            st.session_state["pending_assets"] = list_pending_assets(
                API_URL,
                run_id=queue_run_id,
            )
            st.session_state["pending_assets_run_id"] = queue_run_id
        except requests.RequestException as exc:
            st.session_state["pending_assets"] = []
            st.error(
                f"No se pudo recuperar la cola de curaduría: {api_error_message(exc)}"
            )

    pending_assets = st.session_state.get("pending_assets", [])
    if not pending_assets:
        st.info("No hay activos pendientes de revisión.")

    linkedin_assets_tab, faq_assets_tab = st.tabs(["LinkedIn", "FAQ"])
    with linkedin_assets_tab:
        linkedin_assets = [
            asset for asset in pending_assets if asset["channel"] == "LINKEDIN"
        ]
        if linkedin_assets:
            _render_pending_asset_editors(linkedin_assets, pending_assets)
        else:
            st.info("No hay borradores de LinkedIn pendientes.")
    with faq_assets_tab:
        faq_assets = [asset for asset in pending_assets if asset["channel"] == "FAQ"]
        if faq_assets:
            _render_pending_asset_editors(faq_assets, pending_assets)
        else:
            st.info("No hay propuestas FAQ pendientes.")

    st.divider()
    st.subheader("Activos aprobados")
    st.caption(
        "Los aprobados permanecen disponibles para publicar o recuperar su recibo, "
        "incluso si una publicación anterior falló."
    )
    try:
        approved_assets = (
            list_assets(
                API_URL,
                status="APPROVED",
                run_id=queue_run_id,
            )
            if health
            else []
        )
    except requests.RequestException as exc:
        approved_assets = []
        st.error(f"No se pudieron recuperar los aprobados: {api_error_message(exc)}")

    if not approved_assets:
        st.info("No hay activos aprobados para esta ejecución.")
    for asset in approved_assets:
        with st.container(border=True):
            st.markdown(f"**{escape(asset['title'])}**")
            st.caption(
                f"{asset['channel']} · versión {asset['version']} · {asset['id']}"
            )
            if st.button(
                "Publicar / recuperar recibo",
                key=f"publish-approved-{asset['id']}",
            ):
                try:
                    st.session_state["last_publish_receipt"] = publish_asset(
                        API_URL,
                        asset["id"],
                        api_write_key=API_WRITE_KEY,
                    )
                    st.success("Recibo de publicación recuperado.")
                    st.rerun()
                except requests.RequestException as exc:
                    st.error(f"No se pudo publicar el activo: {api_error_message(exc)}")

    receipt = st.session_state.get("last_publish_receipt")
    if receipt:
        st.subheader("Recibo de publicación")
        st.caption("Objeto guardado en el almacenamiento configurado")
        receipt_columns = st.columns(2)
        receipt_columns[0].write("**Bucket**")
        receipt_columns[0].code(receipt.get("bucket", "—"))
        receipt_columns[0].write("**Objeto**")
        receipt_columns[0].code(receipt.get("object_key", "—"))
        receipt_columns[1].write("**ETag**")
        receipt_columns[1].code(receipt.get("etag") or "—")
        receipt_columns[1].write("**SHA-256**")
        receipt_columns[1].code(receipt.get("sha256", "—"))
