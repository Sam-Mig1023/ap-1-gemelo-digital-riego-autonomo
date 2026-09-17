"""
Autenticación con JWT + bcrypt
Patrón: gemelo_digital_minero/modules/auth.py  +  gemelo_educativo_ett/modulo_seguridad/auth.py
"""
import os
import jwt
import streamlit as st
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import database as db

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET", "vri_digital_twin_2026_jwt_secret")
ALGORITHM = "HS256"
TOKEN_EXPIRY = int(os.getenv("JWT_EXPIRY_HOURS", "8"))

PERMISOS = {
    "Administrador": {
        "aprobar_decisiones": True,
        "anular_decisiones": True,
        "ejecutar_riego": True,
        "riego_manual": True,
        "parada_emergencia": True,
        "generar_reportes": True,
        "gestionar_usuarios": True,
        "ver_bitacora": True,
        "inferencia_rl": True,
        "ingestar_telemetria": True,
    },
    "Agronomo": {
        "aprobar_decisiones": True,
        "anular_decisiones": True,
        "ejecutar_riego": True,
        "riego_manual": True,
        "parada_emergencia": True,
        "generar_reportes": True,
        "gestionar_usuarios": False,
        "ver_bitacora": True,
        "inferencia_rl": True,
        "ingestar_telemetria": True,
    },
    "Productor": {
        "aprobar_decisiones": False,
        "anular_decisiones": False,
        "ejecutar_riego": False,
        "riego_manual": False,
        "parada_emergencia": False,
        "generar_reportes": True,
        "gestionar_usuarios": False,
        "ver_bitacora": False,
        "inferencia_rl": True,
        "ingestar_telemetria": False,
    },
    "Tecnico": {
        "aprobar_decisiones": False,
        "anular_decisiones": False,
        "ejecutar_riego": True,
        "riego_manual": True,
        "parada_emergencia": True,
        "generar_reportes": False,
        "gestionar_usuarios": False,
        "ver_bitacora": False,
        "inferencia_rl": True,
        "ingestar_telemetria": True,
    },
}


def generate_token(user_id: int, username: str, rol: str) -> str:
    payload = {
        "user_id": user_id,
        "username": username,
        "rol": rol,
        "exp": datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRY),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def has_permission(rol: str, permiso: str) -> bool:
    return PERMISOS.get(rol, {}).get(permiso, False)


def login(username: str, password: str) -> dict | None:
    conn = db.get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM usuarios WHERE username = ? AND activo = 1", (username,))
    user = c.fetchone()
    conn.close()

    if user and db.verify_password(password, user["password_hash"]):
        db.log_bitacora(user["id"], "LOGIN", "Sesión iniciada desde Streamlit")
        conn2 = db.get_connection()
        conn2.execute(
            "UPDATE usuarios SET ultimo_acceso = CURRENT_TIMESTAMP WHERE id = ?",
            (user["id"],),
        )
        conn2.commit()
        conn2.close()

        token = generate_token(user["id"], user["username"], user["rol"])
        return {
            "token": token,
            "user_id": user["id"],
            "username": user["username"],
            "nombre": user["nombre"],
            "apellido": user["apellido"],
            "email": user["email"],
            "rol": user["rol"],
        }
    if user:
        db.log_bitacora(user["id"], "LOGIN_FALLIDO", "Contraseña incorrecta")
    else:
        db.log_bitacora(None, "LOGIN_FALLIDO", f"Usuario inexistente o inactivo: {username}")
    return None


def sesion_valida() -> bool:
    """Revalida JWT en cada rerun. Si expiró, limpia la sesión."""
    if not st.session_state.get("autenticado"):
        return False
    token = st.session_state.get("token")
    payload = verify_token(token) if token else None
    if payload:
        return True
    cerrar_sesion()
    return False


def mostrar_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style='text-align:center; padding:30px 0 10px 0'>
            <img src='https://img.icons8.com/fluency/96/sprout.png' width='72'/>
            <h1 style='color:#0f172a; margin-top:8px'>VRI Digital Twin</h1>
            <p style='color:#64748b'>Riego Variable Autónomo · Agente RL + Gemelo Digital</p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            st.markdown("### 🔐 Iniciar Sesión")
            username = st.text_input("Usuario", placeholder="Ingrese su usuario")
            password = st.text_input("Contraseña", type="password", placeholder="Contraseña")
            submit = st.form_submit_button("Ingresar", use_container_width=True)

            if submit:
                if not username or not password:
                    st.error("Complete usuario y contraseña")
                else:
                    result = login(username, password)
                    if result:
                        st.session_state.update({
                            "autenticado": True,
                            "usuario": result,
                            "token": result["token"],
                            "permisos": PERMISOS.get(result["rol"], {}),
                        })
                        st.rerun()
                    else:
                        st.error("❌ Usuario o contraseña incorrectos")

        st.info("""
**Usuarios de demostración:**

| Usuario | Contraseña | Rol |
|---|---|---|
| `admin` | `admin123` | 👤 Administrador |
| `agronomo` | `agro123` | 🌿 Agrónomo |
| `productor` | `prod123` | 🏭 Productor |
| `tecnico` | `tec123` | 🔧 Técnico |
""")


def cerrar_sesion():
    claves = ["autenticado", "usuario", "permisos", "ultima_decision", "token", "_pagina_log"]
    for k in claves:
        st.session_state.pop(k, None)
    st.session_state["autenticado"] = False
