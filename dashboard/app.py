import json
import os
from datetime import date
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
    list_pending_assets,
    mutation_headers,
)


API_URL = os.getenv("API_URL", "http://api:8000").rstrip("/")
API_WRITE_KEY = os.getenv("API_WRITE_KEY")

st.set_page_config(page_title="CommunityLab", page_icon="🧪", layout="wide")
st.title("CommunityLab")
st.caption("Carga y trazabilidad del MVP para comunidades digitales")


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
    st.header("Estado del sistema")
    if health:
        st.success("API disponible")
        st.write(f"PostgreSQL: **{health.get('database', 'desconocido')}**")
        st.caption(API_URL)
    else:
        st.warning("API iniciando o temporalmente no disponible")
        st.caption(
            "Render Free puede tardar cerca de un minuto en despertar. "
            "Esperá unos segundos y recargá la página."
        )
        if health_error:
            st.caption(health_error)

    st.divider()
    st.write("**Disponible ahora**")
    st.caption("Ingesta, IA, oportunidades, generación y curaduría persistente.")

st.subheader("1. Cargar interacciones")
left, middle, right = st.columns(3)
with left:
    organization_id = st.text_input("Organización", value="one")
with middle:
    community_id = st.text_input("Comunidad", value="g10-equipo-14")
with right:
    today = date.today().isocalendar()
    default_period = f"{today.year}-W{today.week:02d}"
    reference_period = st.text_input("Período de referencia", value=default_period)

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

st.subheader("2. Recuperar una ejecución")
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
        use_container_width=True,
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
    st.subheader("3. Resultado persistido")
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
    st.caption(f"Run ID: `{result['run_id']}` · Estado: `{result['status']}`")

    if result.get("record_errors"):
        st.warning("Algunos registros no pudieron procesarse.")
        st.dataframe(result["record_errors"], use_container_width=True)

st.subheader("4. Análisis, oportunidades y curaduría")
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
        st.dataframe(result.get("opportunities", []), use_container_width=True)
    else:
        st.info("Procesá un archivo para ver oportunidades.")
with alerts_tab:
    try:
        open_alerts = list_open_alerts(API_URL) if health else []
        if open_alerts:
            st.warning(f"{len(open_alerts)} alerta(s) interna(s) abierta(s).")
            st.dataframe(open_alerts, use_container_width=True)
        else:
            st.info("No hay alertas internas abiertas.")
    except requests.RequestException as exc:
        st.error(
            f"No se pudieron recuperar las alertas internas: {api_error_message(exc)}"
        )
with assets_tab:
    queue_header, queue_action = st.columns([4, 1])
    queue_header.caption(
        "Cola persistente: los borradores pendientes se recuperan desde PostgreSQL."
    )
    refresh_queue = queue_action.button("Actualizar cola", use_container_width=True)
    if "pending_assets" not in st.session_state or refresh_queue:
        try:
            st.session_state["pending_assets"] = list_pending_assets(API_URL)
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
            save, approve, reject = st.columns(3)
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
            if approve.button("Aprobar", key=f"approve-{asset['id']}"):
                try:
                    decide_asset(
                        API_URL,
                        asset["id"],
                        decision="approve",
                        reviewer="dashboard",
                        api_write_key=API_WRITE_KEY,
                    )
                    st.session_state["pending_assets"] = [
                        item for item in pending_assets if item["id"] != asset["id"]
                    ]
                    st.success("Activo aprobado y retirado de la cola.")
                    st.rerun()
                except requests.RequestException as exc:
                    st.error(f"No se pudo aprobar el activo: {api_error_message(exc)}")
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
