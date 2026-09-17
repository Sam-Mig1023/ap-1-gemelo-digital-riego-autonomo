"""
🌾 VRI Digital Twin — Gemelo Digital de Riego Autónomo
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
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
[data-testid="stSidebar"]            {background-color: #0f172a;}
[data-testid="stSidebar"] *          {color: #e2e8f0 !important;}
[data-testid="stMetric"]             {background:#1e293b; border-radius:8px;
                                       padding:10px 14px; border-left:4px solid #22c55e;}
.badge-ok   {background:#16a34a;color:#fff;padding:2px 10px;border-radius:12px;font-size:.8rem;}
.badge-err  {background:#dc2626;color:#fff;padding:2px 10px;border-radius:12px;font-size:.8rem;}
.section-lbl{font-size:.75rem;font-weight:700;color:#94a3b8;
             text-transform:uppercase;letter-spacing:.08em;margin-bottom:4px;}
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
    <div style='background:linear-gradient(135deg,#1e3a5f,#1e40af);
                padding:14px;border-radius:10px;margin-bottom:16px;'>
        <h4 style='color:white;margin:0'>👤 {usuario['nombre']} {usuario['apellido']}</h4>
        <p style='color:#bfdbfe;margin:4px 0 0 0;font-size:.85rem'>{usuario['rol']}</p>
        <p style='color:#93c5fd;margin:2px 0 0 0;font-size:.75rem'>{usuario['email']}</p>
    </div>
    """, unsafe_allow_html=True)

    health = api.get_health()
    if health:
        st.markdown('<span class="badge-ok">● API FastAPI Online</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge-err">● API Offline — modo local</span>', unsafe_allow_html=True)
        if api.last_error():
            st.caption(f"Detalle: {api.last_error()[:80]}")

    st.markdown("---")
    st.markdown('<p class="section-lbl">Módulos</p>', unsafe_allow_html=True)

    menu = [
        ("🏠 Dashboard", "Dashboard"),
        ("🌐 Gemelo Digital 3D", "Gemelo"),
        ("🤖 Agente RL", "AgRL"),
        ("📡 Telemetría", "Telemetria"),
        ("💧 Control de Riego", "Riego"),
        ("📄 Reportes", "Reportes"),
    ]
    if has_permission(usuario["rol"], "ver_bitacora"):
        menu.append(("📝 Bitácora / Auditoría", "Bitacora"))
    if has_permission(usuario["rol"], "gestionar_usuarios"):
        menu.append(("👥 Usuarios", "Usuarios"))

    pagina_actual = st.session_state.get("pagina", "Dashboard")
    for label, key in menu:
        if st.button(label, use_container_width=True, key=f"nav_{key}",
                     type="primary" if pagina_actual == key else "secondary"):
            st.session_state["pagina"] = key
            st.rerun()

    st.markdown("---")
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        db.log_bitacora(usuario["user_id"], "LOGOUT", "Sesión cerrada")
        cerrar_sesion()
        st.rerun()

    st.markdown(f"""
    <p style='text-align:center;color:#475569;font-size:.7rem;margin-top:8px'>
    VRI Digital Twin v1.1.0<br>{datetime.now().strftime('%d/%m/%Y %H:%M')}
    </p>
    """, unsafe_allow_html=True)

if not health:
    st.warning(
        "🔌 **Modo local:** FastAPI no responde. "
        "Los datos salen de SQLite y la inferencia RL usa la regla CWSI local."
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
