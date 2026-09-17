"""
VRI Digital Twin — Gemelo Digital de Riego Autónomo
Frontend Streamlit con autenticación JWT + bcrypt, SQLite local y reportes reales.
"""
import streamlit as st
import database as db
import api_client as api
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(
    page_title="VRI Digital Twin",
    page_icon="assets/favicon.png" if os.path.exists("assets/favicon.png") else None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS adaptativo (modo claro y oscuro) ──────────────────────────────────────
st.markdown("""
<style>
/* Variables CSS adaptativas */
:root {
    --primary-color: #2563eb;
    --success-color: #16a34a;
    --warning-color: #d97706;
    --error-color: #dc2626;
    --info-color: #0891b2;
    --neutral-color: #64748b;
    
    --bg-primary: var(--stBackgroundColor, #ffffff);
    --bg-secondary: var(--stSecondaryBackgroundColor, #f8fafc);
    --text-primary: var(--stTextColor, #0f172a);
    --border-color: rgba(148, 163, 184, 0.2);
}

/* Sidebar */
[data-testid="stSidebar"] {
    border-right: 1px solid var(--border-color);
}

/* Tarjeta de métricas */
[data-testid="stMetric"] {
    border-radius: 6px;
    padding: 10px 14px;
    border-left: 3px solid var(--primary-color);
    background-color: var(--bg-secondary);
}

/* Etiqueta de sección en sidebar */
.section-lbl {
    font-size: .7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .08em;
    opacity: .55;
    margin-bottom: 4px;
    color: var(--text-primary);
}

/* Badges de estado */
.badge-ok {
    background: var(--success-color);
    color: #ffffff;
    padding: 2px 10px;
    border-radius: 4px;
    font-size: .78rem;
    font-weight: 600;
    display: inline-block;
}
.badge-err {
    background: var(--error-color);
    color: #ffffff;
    padding: 2px 10px;
    border-radius: 4px;
    font-size: .78rem;
    font-weight: 600;
    display: inline-block;
}

/* Botones de navegación */
[data-testid="stButton"] button {
    border-radius: 5px;
    font-weight: 500;
    transition: all 0.2s ease;
}

[data-testid="stButton"] button:hover {
    transform: translateY(-1px);
}

/* Contenedor de usuario */
.user-card {
    padding: 12px 14px;
    border-radius: 6px;
    margin-bottom: 14px;
    background: rgba(37, 99, 235, 0.08);
    border: 1px solid rgba(37, 99, 235, 0.2);
}
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def inicializar():
    db.init_database()
    db.insert_default_data()
    return True


inicializar()

for key, val in {
    "autenticado": False,
    "usuario": None,
    "permisos": {},
    "ultima_decision": None,
    "token": None,
    "pagina": "Dashboard",
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

from modulos.auth import mostrar_login, cerrar_sesion, has_permission, sesion_valida

if not sesion_valida():
    mostrar_login()
    st.stop()

usuario = st.session_state.usuario

with st.sidebar:
    st.markdown(f"""
    <div class="user-card">
        <div style='font-weight:700;font-size:.95rem'>{usuario['nombre']} {usuario['apellido']}</div>
        <div style='font-size:.8rem;opacity:.7;margin-top:2px'>{usuario['rol']}</div>
        <div style='font-size:.75rem;opacity:.5;margin-top:1px'>{usuario['email']}</div>
    </div>
    """, unsafe_allow_html=True)

    health = api.get_health()
    if health:
        st.markdown('<span class="badge-ok">API Online</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge-err">API Offline — modo local</span>', unsafe_allow_html=True)
        if api.last_error():
            st.caption(f"Error: {api.last_error()[:80]}")

    st.markdown("---")
    st.markdown('<p class="section-lbl">Navegación</p>', unsafe_allow_html=True)

    menu = [
        ("Dashboard", "Dashboard"),
        ("Gemelo Digital", "Gemelo"),
        ("Agente RL", "AgRL"),
        ("Telemetría", "Telemetria"),
        ("Control de Riego", "Riego"),
        ("Reportes", "Reportes"),
    ]
    if has_permission(usuario["rol"], "ver_bitacora"):
        menu.append(("Bitácora", "Bitacora"))
    if has_permission(usuario["rol"], "gestionar_usuarios"):
        menu.append(("Usuarios", "Usuarios"))

    pagina_actual = st.session_state.get("pagina", "Dashboard")
    for label, key in menu:
        if st.button(label, use_container_width=True, key=f"nav_{key}",
                     type="primary" if pagina_actual == key else "secondary"):
            st.session_state["pagina"] = key
            st.rerun()

    st.markdown("---")
    if st.button("Cerrar sesión", use_container_width=True):
        db.log_bitacora(usuario["user_id"], "LOGOUT", "Sesión cerrada")
        cerrar_sesion()
        st.rerun()

    st.markdown(f"""
    <p style='text-align:center;opacity:.4;font-size:.7rem;margin-top:8px;color:var(--text-primary)'>
    VRI Digital Twin v1.1.0<br>{datetime.now().strftime('%d/%m/%Y %H:%M')}
    </p>
    """, unsafe_allow_html=True)

if not health:
    st.info(
        "Modo local activo: FastAPI no responde. "
        "Los datos provienen de SQLite y la inferencia RL usa la regla CWSI local."
    )

pagina = st.session_state.get("pagina", "Dashboard")
if st.session_state.get("_pagina_log") != pagina:
    db.log_bitacora(usuario["user_id"], "NAVEGACION", f"Abrió {pagina}")
    st.session_state["_pagina_log"] = pagina

if pagina == "Dashboard":
    from pages import dashboard
    dashboard.render()
elif pagina == "Gemelo":
    from pages import gemelo_digital
    gemelo_digital.render()
elif pagina == "AgRL":
    from pages import agente_rl
    agente_rl.render()
elif pagina == "Telemetria":
    from pages import telemetria
    telemetria.render()
elif pagina == "Riego":
    from pages import control_riego
    control_riego.render()
elif pagina == "Reportes":
    from pages import reportes
    reportes.render()
elif pagina == "Bitacora":
    from pages import bitacora
    bitacora.render()
elif pagina == "Usuarios":
    from pages import usuarios
    usuarios.render()
else:
    from pages import dashboard
    dashboard.render()