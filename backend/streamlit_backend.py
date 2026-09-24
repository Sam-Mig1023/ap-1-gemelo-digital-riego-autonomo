# streamlit_backend.py – Backend UI built with Streamlit.
"""
Este módulo lanza una aplicación Streamlit (puerto 8501 por defecto) que actúa como
*frontend* del backend FastAPI.  Su propósito es:
1. Exponer una UI sencilla para pruebas manuales.
2. Consumir los endpoints de la API FastAPI (por ej. /health, /predict).
3. Tener su propio puerto, independiente del cliente React.
"""

import streamlit as st
import requests
import os

# ------------------------------------------------------------
# Configuración de la API FastAPI
# ------------------------------------------------------------
API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = os.getenv("API_PORT", "8000")
BASE_URL = f"http://{API_HOST}:{API_PORT}/api/v1"
TIMEOUT = 10.0

def call_api(method: str, path: str, json: dict | None = None):
    """
    Realiza una petición HTTP a la API FastAPI.
    Devuelve el JSON de la respuesta o un dict con la clave ``error``.
    """
    url = f"{BASE_URL}/{path}".rstrip('/')
    try:
        if method.upper() == "GET":
            resp = requests.get(url, timeout=TIMEOUT)
        elif method.upper() == "POST":
            resp = requests.post(url, json=json, timeout=TIMEOUT)
        else:
            raise ValueError(f"Método HTTP no soportado: {method}")
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:
        return {"error": str(exc)}
    except Exception as exc:
        return {"error": str(exc)}

# ------------------------------------------------------------
# UI Streamlit
# ------------------------------------------------------------
st.set_page_config(page_title="VRI Backend – Streamlit UI", layout="wide")
st.title("🚜 VRI Digital Twin – Backend (Streamlit)")

# Sidebar – Navegación de módulos y configuración API
with st.sidebar:
    st.title("Módulos")
    modules = ["Dashboard", "Gemelo Digital 3D", "Mantenimiento", "Análisis Predictivo", "Motor IA", "Documentación Scrum"]
    selected = st.radio("Selecciona módulo", modules, index=modules.index(st.session_state.get("selected_module", "Dashboard")))
    st.session_state["selected_module"] = selected

    st.markdown("---")
    st.subheader("Configuración de la API FastAPI")
    host = st.text_input("Host", value=API_HOST)
    port = st.text_input("Puerto", value=API_PORT)
    if st.button("Actualizar URL"):
        st.session_state["api_base"] = f"http://{host}:{port}/api/v1"
        st.success("URL actualizada – recarga la página para aplicar cambios.")
# Use the selected module for rendering
module = st.session_state.selected_module

# ---- CSS for module cards ----
st.markdown(
    """
    <style>
    .module-card {
        background: rgba(30,30,30,0.8);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        color: #fff;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# ------------------------------------------------------------
# Módulo: Dashboard (salud y métricas básicas)
# ------------------------------------------------------------
if module == "Dashboard":
    st.subheader("🔍 Health Check")
    health = call_api("GET", "health")
    if health.get("status") == "healthy":
        st.success("API está **healthy**")
        st.json(health)
    else:
        st.error("No se pudo contactar la API")
        st.json(health)
    st.subheader("📊 Estadísticas rápidas")
    stats = call_api("GET", "stats")
    if "error" not in stats:
        try:
            import pandas as pd
            df = pd.DataFrame.from_dict(stats, orient="index", columns=["Valor"])
            st.dataframe(df)
        except Exception:
            st.warning("Pandas not installed; cannot display stats.")

# ------------------------------------------------------------
# Módulo: Gemelo Digital 3D (placeholder con three.js)
# ------------------------------------------------------------
elif module == "Gemelo Digital 3D":
    st.subheader("🛰️ Gemelo Digital – Vista 3D")
    import streamlit.components.v1 as components
    three_js_html = """
    <html>
    <head>
      <script src='https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js'></script>
    </head>
    <body style='margin:0'>
      <canvas id='canvas'></canvas>
      <script>
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({canvas: document.getElementById('canvas')});
        renderer.setSize(window.innerWidth, window.innerHeight);
        const geometry = new THREE.BoxGeometry();
        const material = new THREE.MeshNormalMaterial();
        const cube = new THREE.Mesh(geometry, material);
        scene.add(cube);
        camera.position.z = 3;
        function animate(){
          requestAnimationFrame(animate);
          cube.rotation.x += 0.01;
          cube.rotation.y += 0.01;
          renderer.render(scene, camera);
        }
        animate();
      </script>
    </body>
    </html>
    """
    components.html(three_js_html, height=500, scrolling=False)
    st.caption("Placeholder 3‑D – reemplaza con tu modelo GLTF/OBJ.")

# ------------------------------------------------------------
# Módulo: Mantenimiento
# ------------------------------------------------------------
elif module == "Mantenimiento":
    st.subheader("🛠️ Tareas de Mantenimiento")
    tasks = call_api("GET", "maintenance")
    if tasks and isinstance(tasks, list):
        try:
            import pandas as pd
            df = pd.DataFrame(tasks)
            st.dataframe(df)
        except Exception:
            st.warning("Pandas not installed; cannot display maintenance tasks.")

# ------------------------------------------------------------
# Módulo: Análisis Predictivo
# ------------------------------------------------------------
elif module == "Análisis Predictivo":
    st.subheader("📈 Análisis Predictivo")
    data = call_api("GET", "analytics")
    if data and isinstance(data, dict):
        try:
            import pandas as pd
            import altair as alt
            df = pd.DataFrame(data)
            chart = alt.Chart(df).mark_line().encode(
                x=alt.X(df.columns[0], title="Tiempo"),
                y=alt.Y(df.columns[1], title="Valor")
            )
            st.altair_chart(chart, use_container_width=True)
        except Exception:
            st.warning("Pandas/Altair not installed; cannot display analytics.")

# ------------------------------------------------------------
# Módulo: Motor IA (prompt → respuesta)
# ------------------------------------------------------------
elif module == "Motor IA":
    st.subheader("🤖 Motor IA – Chat sencillo")
    with st.form(key="ai_form"):
        prompt = st.text_area("Prompt", height=150)
        submitted = st.form_submit_button("Enviar")
    if submitted:
        payload = {"prompt": prompt}
        response = call_api("POST", "ai", json=payload)
        st.json(response)

# ------------------------------------------------------------
# Módulo: Documentación Scrum
# ------------------------------------------------------------
elif module == "Documentación Scrum":
    st.subheader("📚 Documentación Scrum")
    md_path = os.path.join(os.path.dirname(__file__), "..", "SCRUM.md")
    try:
        with open(md_path, "r", encoding="utf-8") as f:
            md_content = f.read()
        st.markdown(md_content)
    except Exception:
        st.info("Archivo SCRUM.md no encontrado en la raíz del proyecto.")

# Footer
st.caption(
    "⚡ Esta UI es solo una herramienta de **testing**.\n"
    "Para usar el frontend React, sigue llamando a la API FastAPI desde la app Vite."
)
