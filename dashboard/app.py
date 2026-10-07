import json
import os
from datetime import date
from uuid import uuid4

import requests
import streamlit as st


API_URL = os.getenv("API_URL", "http://api:8000").rstrip("/")

st.set_page_config(page_title="CommunityLab", page_icon="🧪", layout="wide")
st.title("CommunityLab")
st.caption("Carga y trazabilidad del MVP para comunidades digitales")


def api_health() -> dict | None:
    try:
        response = requests.get(f"{API_URL}/api/v1/health", timeout=3)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None


def process_upload(
    uploaded_file,
    organization_id: str,
    community_id: str,
    reference_period: str,
) -> dict:
    idempotency_key = f"dashboard-{uuid4()}"
    headers = {"Idempotency-Key": idempotency_key}
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


health = api_health()
with st.sidebar:
    st.header("Estado local")
    if health:
        st.success("API disponible")
        st.write(f"PostgreSQL: **{health.get('database', 'desconocido')}**")
        st.caption(API_URL)
    else:
        st.error("API no disponible")
        st.caption("Ejecutá `docker compose up -d --build` y recargá la página.")

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
        st.success("Carga procesada correctamente.")
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        st.error(f"El archivo JSON no se pudo leer: {exc}")
    except requests.HTTPError as exc:
        detail = exc.response.text if exc.response is not None else str(exc)
        st.error(f"La API rechazó la carga: {detail}")
    except requests.RequestException as exc:
        st.error(f"No se pudo conectar con la API: {exc}")

result = st.session_state.get("process_result")
if result:
    st.subheader("2. Resultado persistido")
    summary = result["summary"]
    columns = st.columns(4)
    columns[0].metric("Recibidas", summary["received"])
    columns[1].metric("Aceptadas", summary["accepted"])
    columns[2].metric("Duplicadas", summary["duplicates"])
    columns[3].metric("Con errores", summary["errors"])
    st.caption(f"Run ID: `{result['run_id']}` · Estado: `{result['status']}`")

    if result.get("record_errors"):
        st.warning("Algunos registros no pudieron procesarse.")
        st.dataframe(result["record_errors"], use_container_width=True)

st.subheader("3. Análisis, oportunidades y curaduría")
analysis_tab, opportunities_tab, assets_tab = st.tabs(
    ["Análisis", "Oportunidades", "LinkedIn y FAQ"]
)
with analysis_tab:
    st.dataframe(result.get("analyses", []), use_container_width=True) if result else st.info("Procesá un archivo para ver análisis.")
with opportunities_tab:
    st.dataframe(result.get("opportunities", []), use_container_width=True) if result else st.info("Procesá un archivo para ver oportunidades.")
with assets_tab:
    for asset in (result.get("assets", []) if result else []):
        with st.container(border=True):
            title = st.text_input("Título", value=asset["title"], key=f"title-{asset['id']}")
            body = st.text_area("Contenido", value=asset["body"], key=f"body-{asset['id']}")
            st.caption(f"{asset['channel']} · {asset['status']} · versión {asset['version']}")
            save, approve, reject = st.columns(3)
            if save.button("Guardar", key=f"save-{asset['id']}"):
                response = requests.patch(f"{API_URL}/api/v1/assets/{asset['id']}", json={"title": title, "body": body, "editor": "dashboard"}, timeout=10)
                response.raise_for_status(); asset.update(response.json()); st.success("Nueva versión guardada.")
            if approve.button("Aprobar", key=f"approve-{asset['id']}"):
                response = requests.post(f"{API_URL}/api/v1/assets/{asset['id']}/approve", json={"reviewer": "dashboard"}, timeout=10)
                response.raise_for_status(); asset.update(response.json()); st.success("Activo aprobado.")
            if reject.button("Rechazar", key=f"reject-{asset['id']}"):
                response = requests.post(f"{API_URL}/api/v1/assets/{asset['id']}/reject", json={"reviewer": "dashboard"}, timeout=10)
                response.raise_for_status(); asset.update(response.json()); st.warning("Activo rechazado.")
