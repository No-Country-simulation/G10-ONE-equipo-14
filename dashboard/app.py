import json
import os
from datetime import date
from html import escape
from pathlib import Path
from uuid import uuid4

import requests
import streamlit as st

from api_client import (
    api_error_message,
    decide_asset,
    edit_asset,
    get_health,
    get_run,
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
        padding: .75rem .85rem;
        margin: .4rem 0;
        border: 1px solid var(--cl-border);
        border-radius: 12px;
        background: rgba(255,255,255,.82);
    }
    .cl-readonly small { display: block; color: #64748b; margin-bottom: .2rem; }
    .cl-readonly strong { color: var(--cl-navy); overflow-wrap: anywhere; }
    div[data-testid="stMetric"] {
        border: 1px solid var(--cl-border);
        background: rgba(255, 255, 255, .86);
        padding: 1rem;
        border-radius: 16px;
        box-shadow: 0 7px 20px rgba(15, 23, 42, .04);
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
            timeout=30,
        )
    else:
        interactions = json.loads(content.decode("utf-8-sig"))
        if isinstance(interactions, dict) and "interactions" in interactions:
            payload = interactions
            payload.update(
                organization_id=organization_id,
                community_id=community_id,
                reference_period=reference_period,
            )
            payload.setdefault("requested_assets", ["LINKEDIN", "FAQ"])
        else:
            payload = {
                "schema_version": "v1",
                "organization_id": organization_id,
                "community_id": community_id,
                "reference_period": reference_period,
                "requested_assets": ["LINKEDIN", "FAQ"],
                "interactions": interactions,
            }

        response = requests.post(
            f"{API_URL}/api/v1/process",
            headers=headers,
            json=payload,
            timeout=30,
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

if st.button(
    "Procesar archivo",
    type="primary",
    disabled=uploaded_file is None or health is None,
):
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
st.caption("Ingresá un Run ID sólo cuando necesites recuperar un resultado anterior.")
run_input, run_action = st.columns([4, 1])
with run_input:
    requested_run_id = st.text_input(
        "Run ID",
        placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
        help="Pegá el identificador mostrado después de procesar una carga.",
    )
with run_action:
    st.write("")
    st.write("")
    load_run = st.button(
        "Buscar ejecución",
        disabled=not requested_run_id.strip() or health is None,
        width="stretch",
    )

if load_run:
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
    columns = st.columns(4)
    columns[0].metric("Recibidas", summary["received"])
    columns[1].metric("Aceptadas", summary["accepted"])
    columns[2].metric("Duplicadas", summary["duplicates"])
    columns[3].metric("Con errores", summary["errors"])
    insight_columns = st.columns(3)
    insight_columns[0].metric(
        "Sentimiento predominante",
        summary.get("predominant_sentiment") or "Sin datos",
    )
    insight_columns[1].metric(
        "Temas principales",
        ", ".join(summary.get("top_topics", [])) or "Sin datos",
    )
    insight_columns[2].metric(
        "Tiempo de procesamiento",
        f"{summary.get('processing_time_ms', 0):.2f} ms",
    )
    run_meta, status_meta = st.columns([3, 1])
    run_meta.markdown(
        '<div class="cl-readonly"><small>Run ID · sólo lectura</small>'
        f"<strong>{escape(str(result['run_id']))}</strong></div>",
        unsafe_allow_html=True,
    )
    status_meta.markdown(
        '<div class="cl-readonly"><small>Estado · sólo lectura</small>'
        f"<strong>{escape(str(result['status']))}</strong></div>",
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
    ["Análisis", "Oportunidades", "Alertas internas", "LinkedIn y FAQ"]
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
        st.dataframe(result.get("opportunities", []), width="stretch")
    else:
        st.info("Procesá un archivo para ver oportunidades.")
with alerts_tab:
    try:
        open_alerts = list_open_alerts(API_URL) if health else []
        if open_alerts:
            st.warning(f"{len(open_alerts)} alerta(s) interna(s) abierta(s).")
            st.dataframe(open_alerts, width="stretch")
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

    for asset in pending_assets:
        with st.container(border=True):
            title = st.text_input(
                "Título", value=asset["title"], key=f"title-{asset['id']}"
            )
            body = st.text_area(
                "Contenido", value=asset["body"], key=f"body-{asset['id']}"
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
                disabled=not API_WRITE_KEY,
                help="Requiere API_WRITE_KEY configurada en el dashboard."
                if not API_WRITE_KEY
                else None,
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
                        item for item in pending_assets if item["id"] != asset["id"]
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
                        item for item in pending_assets if item["id"] != asset["id"]
                    ]
                    st.warning("Activo rechazado y retirado de la cola.")
                    st.rerun()
                except requests.RequestException as exc:
                    st.error(f"No se pudo rechazar el activo: {api_error_message(exc)}")

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
                disabled=not API_WRITE_KEY,
                help="Requiere API_WRITE_KEY configurada en el dashboard."
                if not API_WRITE_KEY
                else None,
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
