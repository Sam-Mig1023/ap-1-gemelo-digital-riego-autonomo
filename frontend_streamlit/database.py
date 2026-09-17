"""
Base de datos SQLite local — Gemelo Digital de Riego Autónomo
Patrón tomado del proyecto gemelo_digital_minero/utils/database.py del profesor
"""
import sqlite3
import os
import bcrypt
from datetime import datetime, timedelta
import random

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "riego_digital.db")


def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=15, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


# ── Inicializar tablas ─────────────────────────────────────────────────────────

def init_database():
    conn = get_connection()
    c = conn.cursor()

    # Usuarios
    c.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT    UNIQUE NOT NULL,
            password_hash TEXT  NOT NULL,
            nombre      TEXT    NOT NULL,
            apellido    TEXT    NOT NULL,
            email       TEXT    UNIQUE NOT NULL,
            rol         TEXT    NOT NULL CHECK(rol IN ('Administrador','Agronomo','Productor','Tecnico')),
            activo      INTEGER DEFAULT 1,
            ultimo_acceso TIMESTAMP
        )
    """)

    # Bitácora de accesos
    c.execute("""
        CREATE TABLE IF NOT EXISTS bitacora (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id  INTEGER,
            fecha_hora  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            accion      TEXT NOT NULL,
            detalle     TEXT,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    """)

    # Zonas de manejo
    c.execute("""
        CREATE TABLE IF NOT EXISTS zonas (
            id              TEXT PRIMARY KEY,
            nombre          TEXT NOT NULL,
            sector          TEXT NOT NULL,
            area_ha         REAL NOT NULL,
            tipo_suelo      TEXT,
            cultivo         TEXT,
            humedad10       REAL,
            humedad30       REAL,
            humedad60       REAL,
            temp_canopia    REAL,
            cwsi            REAL,
            dosis_mm        REAL,
            latitud         REAL,
            longitud        REAL
        )
    """)

    # Migración: BD ya existente sin coordenadas (gemelo 3D)
    cols = [r[1] for r in c.execute("PRAGMA table_info(zonas)").fetchall()]
    if "latitud" not in cols:
        c.execute("ALTER TABLE zonas ADD COLUMN latitud REAL")
    if "longitud" not in cols:
        c.execute("ALTER TABLE zonas ADD COLUMN longitud REAL")

    # Lecturas de sensores
    c.execute("""
        CREATE TABLE IF NOT EXISTS lecturas_sensores (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            zona_id     TEXT NOT NULL,
            sensor_tipo TEXT NOT NULL,
            valor       REAL NOT NULL,
            unidad      TEXT NOT NULL,
            timestamp   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (zona_id) REFERENCES zonas(id)
        )
    """)

    # Decisiones RL
    c.execute("""
        CREATE TABLE IF NOT EXISTS decisiones_rl (
            id              TEXT PRIMARY KEY,
            zona_id         TEXT NOT NULL,
            dosis_mm        REAL NOT NULL,
            volumen_m3      REAL NOT NULL,
            confianza       REAL NOT NULL,
            estado          TEXT DEFAULT 'pendiente',
            aprobado_por    TEXT,
            razonamiento    TEXT,
            timestamp       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (zona_id) REFERENCES zonas(id)
        )
    """)

    # Ejecuciones de riego
    c.execute("""
        CREATE TABLE IF NOT EXISTS ejecuciones_riego (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            zona_id         TEXT NOT NULL,
            dosis_mm        REAL NOT NULL,
            volumen_m3      REAL NOT NULL,
            tipo            TEXT NOT NULL CHECK(tipo IN ('automatico','manual')),
            ejecutado_por   TEXT,
            timestamp       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (zona_id) REFERENCES zonas(id)
        )
    """)

    conn.commit()
    conn.close()


def _ensure_geo_columns(c):
    cols = [r[1] for r in c.execute("PRAGMA table_info(zonas)").fetchall()]
    if "latitud" not in cols:
        c.execute("ALTER TABLE zonas ADD COLUMN latitud REAL")
    if "longitud" not in cols:
        c.execute("ALTER TABLE zonas ADD COLUMN longitud REAL")


# ── Datos por defecto ──────────────────────────────────────────────────────────

def insert_default_data():
    conn = get_connection()
    c = conn.cursor()
    _ensure_geo_columns(c)

    # Usuarios
    c.execute("SELECT COUNT(*) FROM usuarios")
    if c.fetchone()[0] == 0:
        usuarios = [
            ("admin",      hash_password("admin123"),   "Carlos",  "Mendoza",  "admin@vri.pe",       "Administrador"),
            ("agronomo",   hash_password("agro123"),    "María",   "García",   "maria@vri.pe",        "Agronomo"),
            ("productor",  hash_password("prod123"),    "Juan",    "Torres",   "juan@vri.pe",         "Productor"),
            ("tecnico",    hash_password("tec123"),     "Pedro",   "Ríos",     "pedro@vri.pe",        "Tecnico"),
        ]
        c.executemany("""
            INSERT INTO usuarios (username, password_hash, nombre, apellido, email, rol)
            VALUES (?, ?, ?, ?, ?, ?)
        """, usuarios)

    # Zonas
    c.execute("SELECT COUNT(*) FROM zonas")
    if c.fetchone()[0] == 0:
        # Centroides georreferenciados — Campo San Pablo / Ica (mismo bbox que el frontend React)
        zonas = [
            ("zone-nw", "Zona 1 — Noroeste", "NW", 37.6, "Franco Limosa", "Maíz Amarillo",
             28.5, 32.1, 35.8, 24.3, 0.38, 3.5, -14.06425, -75.73375),
            ("zone-ne", "Zona 2 — Noreste",  "NE", 37.6, "Franco Arcillosa","Maíz Amarillo",
             26.9, 29.5, 33.2, 26.1, 0.61, 5.2, -14.06425, -75.72825),
            ("zone-sw", "Zona 3 — Suroeste", "SW", 37.6, "Franco Limosa", "Maíz Amarillo",
             31.2, 34.0, 37.5, 22.8, 0.22, 2.1, -14.06975, -75.73375),
            ("zone-se", "Zona 4 — Sureste",  "SE", 37.6, "Franco Arenosa", "Maíz Amarillo",
             29.8, 31.5, 34.9, 25.0, 0.49, 4.0, -14.06975, -75.72825),
        ]
        c.executemany("""
            INSERT INTO zonas (id,nombre,sector,area_ha,tipo_suelo,cultivo,
                               humedad10,humedad30,humedad60,temp_canopia,cwsi,dosis_mm,
                               latitud,longitud)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, zonas)

    coords = {
        "zone-nw": (-14.06425, -75.73375),
        "zone-ne": (-14.06425, -75.72825),
        "zone-sw": (-14.06975, -75.73375),
        "zone-se": (-14.06975, -75.72825),
    }
    for zid, (lat, lng) in coords.items():
        c.execute(
            "UPDATE zonas SET latitud = ?, longitud = ? WHERE id = ? AND (latitud IS NULL OR longitud IS NULL)",
            (lat, lng, zid),
        )

    # Lecturas históricas simuladas (últimas 48 h)
    c.execute("SELECT COUNT(*) FROM lecturas_sensores")
    if c.fetchone()[0] == 0:
        random.seed(42)
        zonas_base = {
            "zone-nw": (28.5, 24.3),
            "zone-ne": (26.9, 26.1),
            "zone-sw": (31.2, 22.8),
            "zone-se": (29.8, 25.0),
        }
        for i in range(48):
            ts = (datetime.now() - timedelta(hours=48 - i)).strftime("%Y-%m-%d %H:%M:%S")
            for zid, (hum_base, temp_base) in zonas_base.items():
                hum  = round(hum_base  + random.uniform(-1.5, 1.5), 2)
                temp = round(temp_base + random.uniform(-0.8, 0.8), 2)
                c.execute("""
                    INSERT INTO lecturas_sensores (zona_id, sensor_tipo, valor, unidad, timestamp)
                    VALUES (?, 'humedad_10cm', ?, '%', ?)
                """, (zid, hum, ts))
                c.execute("""
                    INSERT INTO lecturas_sensores (zona_id, sensor_tipo, valor, unidad, timestamp)
                    VALUES (?, 'temp_canopia', ?, '°C', ?)
                """, (zid, temp, ts))

    # Decisiones de demostración (para reportes / historial sin API)
    c.execute("SELECT COUNT(*) FROM decisiones_rl")
    if c.fetchone()[0] == 0:
        seed = [
            ("rl-demo-nw01", "zone-nw", 3.50, 0.132, 0.93, "aprobado", "admin",
             "Humedad suficiente; dosis de mantenimiento."),
            ("rl-demo-ne01", "zone-ne", 5.20, 0.196, 0.88, "pendiente", None,
             "CWSI elevado: riego prioritario en NE."),
        ]
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for row in seed:
            c.execute("""
                INSERT INTO decisiones_rl
                    (id, zona_id, dosis_mm, volumen_m3, confianza, estado, aprobado_por, razonamiento, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (*row, now))

    conn.commit()
    conn.close()


# ── Funciones de consulta ──────────────────────────────────────────────────────

def get_zonas():
    conn = get_connection()
    import pandas as pd
    df = pd.read_sql_query("SELECT * FROM zonas", conn)
    conn.close()
    return df


def get_lecturas(zona_id: str = None, sensor_tipo: str = None, limit: int = 200):
    conn = get_connection()
    import pandas as pd
    query = "SELECT * FROM lecturas_sensores WHERE 1=1"
    params = []
    if zona_id:
        query += " AND zona_id = ?"
        params.append(zona_id)
    if sensor_tipo:
        query += " AND sensor_tipo = ?"
        params.append(sensor_tipo)
    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df


def get_decisiones():
    conn = get_connection()
    import pandas as pd
    df = pd.read_sql_query("SELECT * FROM decisiones_rl ORDER BY timestamp DESC LIMIT 50", conn)
    conn.close()
    return df


def save_decision(decision: dict):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO decisiones_rl
            (id, zona_id, dosis_mm, volumen_m3, confianza, estado, razonamiento, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        decision["id"], decision["zona_id"],
        decision["dosis_mm"], decision["volumen_m3"],
        decision["confianza"], decision.get("estado", "pendiente"),
        decision.get("razonamiento", ""), decision.get("timestamp", datetime.now().isoformat()),
    ))
    conn.commit()
    conn.close()


def update_decision_estado(decision_id: str, estado: str, aprobado_por: str = None):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        UPDATE decisiones_rl SET estado = ?, aprobado_por = ? WHERE id = ?
    """, (estado, aprobado_por, decision_id))
    conn.commit()
    conn.close()


def save_ejecucion(zona_id: str, dosis_mm: float, tipo: str, ejecutado_por: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO ejecuciones_riego (zona_id, dosis_mm, volumen_m3, tipo, ejecutado_por)
        VALUES (?, ?, ?, ?, ?)
    """, (zona_id, dosis_mm, round(dosis_mm * 37.6 / 1000, 3), tipo, ejecutado_por))
    conn.commit()
    conn.close()


def get_ejecuciones(limit: int = 30):
    conn = get_connection()
    import pandas as pd
    df = pd.read_sql_query(
        "SELECT * FROM ejecuciones_riego ORDER BY timestamp DESC LIMIT ?",
        conn, params=(limit,)
    )
    conn.close()
    return df


def log_bitacora(usuario_id: int | None, accion: str, detalle: str = ""):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO bitacora (usuario_id, accion, detalle) VALUES (?, ?, ?)
    """, (usuario_id, accion, detalle))
    conn.commit()
    conn.close()


def get_bitacora(limit: int = 100):
    conn = get_connection()
    import pandas as pd
    df = pd.read_sql_query("""
        SELECT b.fecha_hora, b.accion, b.detalle,
               u.username, u.nombre, u.rol
        FROM bitacora b
        LEFT JOIN usuarios u ON b.usuario_id = u.id
        ORDER BY b.fecha_hora DESC LIMIT ?
    """, conn, params=(limit,))
    conn.close()
    return df


def get_all_users():
    conn = get_connection()
    import pandas as pd
    df = pd.read_sql_query(
        """SELECT id, username, nombre, apellido, email, rol, activo, ultimo_acceso
           FROM usuarios ORDER BY id""",
        conn,
    )
    conn.close()
    return df


def set_user_activo(user_id: int, activo: int):
    conn = get_connection()
    conn.execute("UPDATE usuarios SET activo = ? WHERE id = ?", (activo, user_id))
    conn.commit()
    conn.close()


def cambiar_password(user_id: int, password: str):
    conn = get_connection()
    conn.execute(
        "UPDATE usuarios SET password_hash = ? WHERE id = ?",
        (hash_password(password), user_id),
    )
    conn.commit()
    conn.close()


def cambiar_rol(user_id: int, rol: str):
    conn = get_connection()
    conn.execute("UPDATE usuarios SET rol = ? WHERE id = ?", (rol, user_id))
    conn.commit()
    conn.close()


def registrar_usuario(username, password, nombre, apellido, email, rol):
    conn = get_connection()
    try:
        conn.execute(
            """INSERT INTO usuarios (username, password_hash, nombre, apellido, email, rol)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (username, hash_password(password), nombre, apellido, email, rol),
        )
        conn.commit()
        return True, "Usuario registrado"
    except sqlite3.IntegrityError as e:
        return False, f"Usuario o email duplicado: {e}"
    finally:
        conn.close()


def insert_lectura(zona_id: str, sensor_tipo: str, valor: float, unidad: str):
    conn = get_connection()
    conn.execute(
        """INSERT INTO lecturas_sensores (zona_id, sensor_tipo, valor, unidad)
           VALUES (?, ?, ?, ?)""",
        (zona_id, sensor_tipo, valor, unidad),
    )
    conn.commit()
    conn.close()


def get_alertas_zonas():
    """Alertas de estrés hídrico a partir de CWSI y humedad 10 cm."""
    df = get_zonas()
    alertas = []
    if df.empty:
        return alertas
    for _, z in df.iterrows():
        if z["cwsi"] >= 0.6:
            alertas.append({
                "nivel": "critico",
                "zona": z["sector"],
                "mensaje": f"CWSI {z['cwsi']:.2f} — riego urgente en {z['nombre']}",
            })
        elif z["humedad10"] < 25:
            alertas.append({
                "nivel": "alto",
                "zona": z["sector"],
                "mensaje": f"Humedad 10 cm {z['humedad10']:.1f}% bajo PMP en {z['nombre']}",
            })
        elif z["cwsi"] >= 0.4:
            alertas.append({
                "nivel": "moderado",
                "zona": z["sector"],
                "mensaje": f"Estrés moderado (CWSI {z['cwsi']:.2f}) en {z['nombre']}",
            })
    return alertas


def get_resumen_bitacora(limit: int = 200):
    import pandas as pd
    df = get_bitacora(limit=limit)
    if df.empty:
        return pd.DataFrame(columns=["accion", "n"])
    return df.groupby("accion").size().reset_index(name="n").sort_values("n", ascending=False)
