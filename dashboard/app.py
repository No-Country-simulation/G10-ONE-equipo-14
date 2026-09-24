import os
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://api:8000")

st.set_page_config(page_title="CommunityLab", page_icon="🧪", layout="wide")
st.title("CommunityLab")
st.caption("Week 1 integration dashboard")

try:
    response = requests.get(f"{API_URL}/api/v1/health", timeout=3)
    response.raise_for_status()
    data = response.json()
    st.success(f"API: {data['status']} | PostgreSQL: {data['database']}")
    st.json(data)
except Exception as exc:
    st.error(f"API unavailable: {exc}")

st.subheader("Integration status")
st.write("Use FastAPI Swagger at http://localhost:8000/docs to test the v1 contracts.")
