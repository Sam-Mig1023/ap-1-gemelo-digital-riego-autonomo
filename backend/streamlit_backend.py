# streamlit_backend.py – Backend UI built with Streamlit.
"""
Este módulo lanza una aplicación Streamlit (puerto 8501 por defecto) que actúa como
*frontend* del backend FastAPI.  Su propósito es:
1. Exponer una UI sencilla para pruebas manuales.
2. Consumir los endpoints de la API FastAPI (por ej. /health, /predict).
3. Tener su propio puerto, independiente del cliente React.
"""

import streamlit as st
import httpx

# ------------------------------------------------------------
# Configuración de la API FastAPI
# ------------------------------------------------------------
API_HOST = st.secrets.get("API_HOST", "127.0.0.1")
API_PORT = st.secrets.get("API_PORT", "8000")
BASE_URL = f"http://{API_HOST}:{API_PORT}/api/v1"
TIMEOUT = 10.0

def call_api(method: str, path: str, json: dict | None = None):
    """Realiza una petición HTTP a la API FastAPI.
    Devuelve el JSON de la respuesta o un diccionario con la clave ``error``.
    """
    url = f"{BASE_URL}/{path}".rstrip('/')
    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            if method.upper() == "GET":
                resp = client.get(url)
            elif method.upper() == "POST":
                resp = client.post(url, json=json)
            else:
                raise ValueError(f"Método HTTP no soportado: {method}")
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:
        return {"error": str(exc)}

# ------------------------------------------------------------
# UI Streamlit
# ------------------------------------------------------------
st.set_page_config(page_title="VRI Backend – Streamlit UI", layout="wide")
st.title("🚜 VRI Digital Twin – Backend (Streamlit)")

# Sidebar – Configuración rápida de la API
with st.sidebar:
    st.header("Configuración de la API FastAPI")
    host = st.text_input("Host", value=API_HOST)
    port = st.text_input("Puerto", value=API_PORT)
    if st.button("Actualizar URL"):
        st.session_state["api_base"] = f"http://{host}:{port}/api/v1"
        st.success("URL actualizada – recarga la página para aplicar cambios.")

# Health check
st.subheader("🔍 Health Check")
health = call_api("GET", "health")
if health.get("status") == "healthy":
    st.success("API está **healthy**")
    st.json(health)
else:
    st.error("No se pudo contactar la API")
    st.json(health)

# ------------------------------------------------------------
# Ejemplo de endpoint: predicción (placeholder)
# ------------------------------------------------------------
st.subheader("💡 Prueba de predicción (ejemplo)")
with st.form(key="predict_form"):
    dummy_input = st.text_area("Entrada (JSON)", value="{}", height=120)
    submitted = st.form_submit_button("Ejecutar predicción")

if submitted:
    try:
        payload = eval(dummy_input)  # Sólo para demo – en prod usar json.loads
    except Exception:
        payload = {}
    result = call_api("POST", "predict", json=payload)
    st.json(result)

# Footer
st.caption(
    "⚡ Esta UI es solo una herramienta de **testing**.\n"
    "Para usar el frontend React, sigue llamando a la API FastAPI desde la app Vite."
)
