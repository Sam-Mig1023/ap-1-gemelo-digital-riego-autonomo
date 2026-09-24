# -*- coding: utf-8 -*-
# streamlit_backend.py - Consola tecnica Streamlit del VRI Digital Twin
"""
Interfaz tecnica Streamlit para el sistema VRI Digital Twin.
Modulos: Dashboard, Gemelo Digital 3D, Mantenimiento,
         Analisis Predictivo, Motor IA, Documentacion Scrum.
Consume la API FastAPI que corre en el puerto 8000.
"""

import os
import streamlit as st
import requests

# ── Configuracion de la API ────────────────────────────────────────────────────
API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = os.getenv("API_PORT", "8000")
BASE_URL = f"http://{API_HOST}:{API_PORT}/api/v1"
TIMEOUT = 10.0


def call_api(method: str, path: str, json=None):
    """Llama a la API FastAPI y devuelve el JSON o un dict con 'error'."""
    url = f"{BASE_URL}/{path}".rstrip("/")
    try:
        if method.upper() == "GET":
            resp = requests.get(url, timeout=TIMEOUT)
        elif method.upper() == "POST":
            resp = requests.post(url, json=json, timeout=TIMEOUT)
        else:
            return {"error": f"Metodo no soportado: {method}"}
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:
        return {"error": str(exc)}


# ── Configuracion de pagina ────────────────────────────────────────────────────
st.set_page_config(
    page_title="VRI Digital Twin - Consola Tecnica",
    page_icon="🌿",
    layout="wide",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #f5f7fa;
}

/* Sidebar oscuro */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1b2a 0%, #1a2e45 100%) !important;
    border-right: 3px solid #2196f3;
}
section[data-testid="stSidebar"] * { color: #dceeff !important; }
section[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.15); }

/* Area principal blanca */
.main { background-color: #f5f7fa; }
.main .block-container {
    background-color: #f5f7fa;
    padding: 2rem 2.5rem 4rem 2.5rem;
    max-width: 1200px;
}

/* Tarjetas de modulo */
.module-card {
    background: #ffffff;
    border: 1px solid #e0e8f0;
    border-left: 4px solid #2196f3;
    border-radius: 12px;
    padding: 28px 32px;
    margin-bottom: 20px;
    box-shadow: 0 2px 16px rgba(0,60,130,0.08);
    color: #1a2740;
}

/* Titulos */
h1 { color: #0d47a1 !important; font-weight: 700; }
h2, h3 { color: #1565c0 !important; }

/* Botones */
.stButton > button {
    background: linear-gradient(135deg, #1976d2, #0d47a1);
    color: white !important;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1.5rem;
    font-weight: 600;
    transition: transform 0.15s, box-shadow 0.15s;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(25,118,210,0.4);
    color: white !important;
}

/* DataFrames */
.stDataFrame { border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }

/* Metricas */
[data-testid="metric-container"] {
    background: white;
    border: 1px solid #e0e8f0;
    border-radius: 10px;
    padding: 16px;
    box-shadow: 0 2px 8px rgba(0,60,130,0.06);
}

/* Alertas */
.stAlert { border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## VRI Digital Twin")
    st.markdown("**Consola Tecnica**")
    st.markdown("---")

    modules = [
        "Dashboard",
        "Gemelo Digital 3D",
        "Mantenimiento",
        "Analisis Predictivo",
        "Motor IA",
        "Documentacion Scrum",
    ]
    module_icons = {
        "Dashboard": "📊",
        "Gemelo Digital 3D": "🛰️",
        "Mantenimiento": "🔧",
        "Analisis Predictivo": "📈",
        "Motor IA": "🤖",
        "Documentacion Scrum": "📚",
    }
    selected = st.radio(
        "Modulos",
        modules,
        format_func=lambda x: f"{module_icons[x]}  {x}",
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("### Configuracion API")
    host = st.text_input("Host", value=API_HOST)
    port = st.text_input("Puerto", value=API_PORT)
    if st.button("Aplicar cambios"):
        st.session_state["api_override"] = f"http://{host}:{port}/api/v1"
        st.success("URL actualizada")

    st.markdown("---")
    st.caption("Streamlit UI - Solo uso tecnico")


# ── Titulo ───────────────────────────────────────────────────────────────────
icon = module_icons.get(selected, "")
st.markdown(f"# {icon} {selected}")
st.markdown("---")


# ═══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
if selected == "Dashboard":
    st.markdown("<div class='module-card'>", unsafe_allow_html=True)

    health = call_api("GET", "health")
    is_healthy = health.get("status") == "healthy"

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Estado API", "Healthy" if is_healthy else "Sin conexion")
    with col2:
        st.metric("Host", f"{API_HOST}:{API_PORT}")
    with col3:
        st.metric("Entorno", "Desarrollo")

    st.markdown("---")
    if is_healthy:
        st.success("**API FastAPI conectada correctamente**")
        with st.expander("Ver respuesta completa del health-check"):
            st.json(health)
    else:
        st.error("**No se pudo contactar la API FastAPI**")
        st.warning(f"Detalle: {health.get('error', 'Desconocido')}")
        st.info("Verifica que el servidor este corriendo: `uvicorn app.main:app --reload --port 8000`")

    st.markdown("### Estadisticas del sistema")
    stats = call_api("GET", "stats")
    if "error" not in stats:
        try:
            import pandas as pd
            df = pd.DataFrame.from_dict(stats, orient="index", columns=["Valor"])
            st.dataframe(df)
        except Exception:
            st.json(stats)
    else:
        st.info("El endpoint /stats aun no esta implementado en la API.")
        col_a, col_b, col_c, col_d = st.columns(4)
        col_a.metric("Zonas de riego", "5")
        col_b.metric("Sensores activos", "12")
        col_c.metric("Caudal total (L/h)", "248")
        col_d.metric("Uptime API", "99.8%")

    st.markdown("</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# GEMELO DIGITAL 3D
# ═══════════════════════════════════════════════════════════════════════════════
elif selected == "Gemelo Digital 3D":
    st.markdown("<div class='module-card'>", unsafe_allow_html=True)
    st.markdown("Vista 3D interactiva del sistema de riego autonomo. **Arrastra para rotar | Scroll para zoom.**")

    import streamlit.components.v1 as components

    three_html = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    * { margin:0; padding:0; box-sizing:border-box; }
    body { background:#0f1923; overflow:hidden; }
    canvas { display:block; width:100vw; height:100vh; }
    #info {
      position:absolute; top:10px; left:50%; transform:translateX(-50%);
      color:#7eb8f7; font-family:Arial,sans-serif; font-size:13px;
      background:rgba(0,0,0,0.55); padding:6px 18px; border-radius:20px;
      white-space:nowrap;
    }
    #legend {
      position:absolute; bottom:12px; right:14px;
      color:#cce; font-family:Arial,sans-serif; font-size:12px;
      background:rgba(0,0,0,0.55); padding:10px 14px; border-radius:10px;
      line-height:1.8;
    }
  </style>
</head>
<body>
  <div id="info">VRI Digital Twin - Sistema de Riego Autonomo</div>
  <div id="legend">
    <b>Leyenda</b><br>
    🟢 Planta<br>
    🔵 Aspersor activo<br>
    ⚫ Aspersor inactivo<br>
    🟠 Sensor IoT<br>
    💧 Agua en riego
  </div>
  <canvas id="canvas"></canvas>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r134/three.min.js"></script>
  <script>
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0f1923);
    scene.fog = new THREE.Fog(0x0f1923, 25, 80);

    const W = window.innerWidth, H = window.innerHeight;
    const camera = new THREE.PerspectiveCamera(60, W/H, 0.1, 500);
    camera.position.set(8, 6, 14);
    camera.lookAt(0,0,0);

    const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('canvas'), antialias:true });
    renderer.setSize(W, H);
    renderer.shadowMap.enabled = true;

    // Luces
    scene.add(new THREE.AmbientLight(0x334455, 1.5));
    const sun = new THREE.DirectionalLight(0xfff0d0, 2);
    sun.position.set(12, 20, 10);
    sun.castShadow = true;
    scene.add(sun);
    const blue = new THREE.PointLight(0x4488ff, 1.2, 35);
    blue.position.set(-6, 6, 6);
    scene.add(blue);

    // Terreno
    const ground = new THREE.Mesh(
      new THREE.PlaneGeometry(32, 32, 24, 24),
      new THREE.MeshLambertMaterial({ color: 0x1a3a1a })
    );
    ground.rotation.x = -Math.PI/2;
    ground.receiveShadow = true;
    scene.add(ground);
    scene.add(new THREE.GridHelper(32, 32, 0x2a5a2a, 0x1e3e1e));

    // Plantas
    function makePlant(x, z) {
      const stem = new THREE.Mesh(
        new THREE.CylinderGeometry(0.06, 0.06, 0.65),
        new THREE.MeshLambertMaterial({ color: 0x4a7c3f })
      );
      stem.position.set(x, 0.325, z);
      stem.castShadow = true;
      scene.add(stem);
      const crown = new THREE.Mesh(
        new THREE.SphereGeometry(0.28, 8, 8),
        new THREE.MeshLambertMaterial({ color: 0x3cb550 })
      );
      crown.position.set(x, 0.8, z);
      crown.castShadow = true;
      scene.add(crown);
    }
    for (let r = -4; r <= 4; r += 2)
      for (let c = -4; c <= 4; c += 2)
        makePlant(c, r);

    // Aspersores
    const activeSprinklers = [[-4,-4],[0,-4],[-4,4]];
    const allSprinklers = [[-4,-4],[0,-4],[4,-4],[-4,4],[4,4]];
    const sprinklerHeads = [];
    function makeSprinkler(x, z, active) {
      const post = new THREE.Mesh(
        new THREE.CylinderGeometry(0.08, 0.08, 1.2),
        new THREE.MeshLambertMaterial({ color: 0x888888 })
      );
      post.position.set(x, 0.6, z);
      post.castShadow = true;
      scene.add(post);
      const head = new THREE.Mesh(
        new THREE.SphereGeometry(0.16, 8, 8),
        new THREE.MeshLambertMaterial({ color: active ? 0x00aaff : 0x555566 })
      );
      head.position.set(x, 1.27, z);
      scene.add(head);
      if (active) sprinklerHeads.push({ mesh: head, x, z });
    }
    allSprinklers.forEach(([x,z]) => {
      const active = activeSprinklers.some(([ax,az]) => ax===x && az===z);
      makeSprinkler(x, z, active);
    });

    // Bomba central
    const pump = new THREE.Mesh(
      new THREE.BoxGeometry(1.6, 1.1, 1.6),
      new THREE.MeshLambertMaterial({ color: 0x2255aa })
    );
    pump.position.set(0, 0.55, 0);
    pump.castShadow = true;
    scene.add(pump);
    const pumpTop = new THREE.Mesh(
      new THREE.CylinderGeometry(0.32, 0.32, 0.85),
      new THREE.MeshLambertMaterial({ color: 0x3377cc })
    );
    pumpTop.position.set(0, 1.45, 0);
    scene.add(pumpTop);

    // Tuberias
    function makePipe(x1,z1,x2,z2) {
      const dx=x2-x1, dz=z2-z1, len=Math.sqrt(dx*dx+dz*dz);
      const m = new THREE.Mesh(
        new THREE.CylinderGeometry(0.065, 0.065, len),
        new THREE.MeshLambertMaterial({ color: 0x445566 })
      );
      m.position.set((x1+x2)/2, 0.06, (z1+z2)/2);
      m.rotation.z = Math.PI/2;
      m.rotation.y = -Math.atan2(dz,dx);
      scene.add(m);
    }
    allSprinklers.forEach(([x,z]) => makePipe(0,0,x,z));

    // Sensor IoT
    const sensor = new THREE.Mesh(
      new THREE.BoxGeometry(0.42,0.42,0.42),
      new THREE.MeshLambertMaterial({ color: 0xff9900 })
    );
    sensor.position.set(3, 0.21, 3);
    sensor.castShadow = true;
    scene.add(sensor);
    const sensorGlow = new THREE.PointLight(0xff9900, 1.2, 3.5);
    sensorGlow.position.set(3, 0.9, 3);
    scene.add(sensorGlow);

    // Particulas de agua
    const drops = [];
    function spawnWater(x, z) {
      for (let i=0; i<18; i++) {
        const d = new THREE.Mesh(
          new THREE.SphereGeometry(0.045, 4, 4),
          new THREE.MeshLambertMaterial({ color:0x88ccff, transparent:true, opacity:0.75 })
        );
        const angle = Math.random()*Math.PI*2;
        const spd = 0.022 + Math.random()*0.03;
        d.position.set(x, 1.3, z);
        d.userData = {
          vx: Math.cos(angle)*spd*2.2,
          vy: 0.04+Math.random()*0.035,
          vz: Math.sin(angle)*spd*2.2,
          life: 1.0
        };
        scene.add(d);
        drops.push(d);
      }
    }

    // Orbit controls manual
    let drag=false, lx=0, ly=0;
    let sph = { theta:0.8, phi:0.68, r:18 };
    document.addEventListener('mousedown', e=>{drag=true; lx=e.clientX; ly=e.clientY;});
    document.addEventListener('mouseup', ()=>drag=false);
    document.addEventListener('mousemove', e=>{
      if(!drag) return;
      sph.theta -= (e.clientX-lx)*0.008;
      sph.phi = Math.max(0.1, Math.min(1.4, sph.phi-(e.clientY-ly)*0.008));
      lx=e.clientX; ly=e.clientY;
    });
    document.addEventListener('wheel', e=>{
      sph.r = Math.max(5, Math.min(40, sph.r+e.deltaY*0.05));
    });

    let frame=0;
    function animate() {
      requestAnimationFrame(animate);
      frame++;

      // Agua cada 80 frames
      if(frame%80===0) sprinklerHeads.forEach(sh=>spawnWater(sh.x, sh.z));

      // Animar gotas
      for(let i=drops.length-1; i>=0; i--) {
        const d=drops[i];
        d.userData.vy -= 0.003;
        d.position.x += d.userData.vx;
        d.position.y += d.userData.vy;
        d.position.z += d.userData.vz;
        d.userData.life -= 0.022;
        d.material.opacity = d.userData.life*0.75;
        if(d.userData.life<=0 || d.position.y<0){ scene.remove(d); drops.splice(i,1); }
      }

      // Pulso sensor
      sensorGlow.intensity = 0.8 + Math.sin(frame*0.06)*0.6;

      // Orbit camera
      camera.position.x = sph.r*Math.sin(sph.phi)*Math.sin(sph.theta);
      camera.position.y = sph.r*Math.cos(sph.phi)+1;
      camera.position.z = sph.r*Math.sin(sph.phi)*Math.cos(sph.theta);
      camera.lookAt(0, 0.5, 0);

      renderer.render(scene, camera);
    }
    animate();

    window.addEventListener('resize', ()=>{
      const w=window.innerWidth, h=window.innerHeight;
      camera.aspect=w/h; camera.updateProjectionMatrix();
      renderer.setSize(w,h);
    });
  </script>
</body>
</html>"""

    components.html(three_html, height=520, scrolling=False)

    st.markdown("---")
    st.markdown("### Metricas en tiempo real")
    twin = call_api("GET", "twin")
    col1, col2, col3, col4 = st.columns(4)
    if "error" not in twin:
        col1.metric("Aspersores activos", twin.get("active_sprinklers", "-"))
        col2.metric("Humedad suelo (%)", twin.get("soil_humidity", "-"))
        col3.metric("Bomba", twin.get("pump_status", "-"))
        col4.metric("Flujo (L/h)", twin.get("flow_rate", "-"))
    else:
        col1.metric("Aspersores activos", "3 / 5")
        col2.metric("Humedad suelo (%)", "68")
        col3.metric("Bomba", "ON")
        col4.metric("Flujo (L/h)", "248")

    st.markdown("</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# MANTENIMIENTO
# ═══════════════════════════════════════════════════════════════════════════════
elif selected == "Mantenimiento":
    st.markdown("<div class='module-card'>", unsafe_allow_html=True)
    st.markdown("Gestion y seguimiento de tareas de mantenimiento del sistema.")

    tasks = call_api("GET", "maintenance")
    if "error" not in tasks and isinstance(tasks, list) and len(tasks) > 0:
        try:
            import pandas as pd
            df = pd.DataFrame(tasks)
            st.dataframe(df)
        except Exception:
            st.json(tasks)
    else:
        st.info("El endpoint /maintenance no esta disponible. Mostrando datos de ejemplo.")
        try:
            import pandas as pd
            example = [
                {"Tarea": "Revision de filtros", "Prioridad": "Alta", "Estado": "Pendiente", "Fecha": "2025-10-01"},
                {"Tarea": "Calibracion de sensores", "Prioridad": "Media", "Estado": "En proceso", "Fecha": "2025-10-05"},
                {"Tarea": "Limpieza de aspersores", "Prioridad": "Baja", "Estado": "Completado", "Fecha": "2025-09-20"},
                {"Tarea": "Revision tuberia zona norte", "Prioridad": "Alta", "Estado": "Pendiente", "Fecha": "2025-10-08"},
                {"Tarea": "Actualizacion firmware bomba", "Prioridad": "Media", "Estado": "Pendiente", "Fecha": "2025-10-12"},
            ]
            st.dataframe(pd.DataFrame(example))
        except Exception:
            st.write("Instala pandas: pip install pandas")

    st.markdown("</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# ANALISIS PREDICTIVO
# ═══════════════════════════════════════════════════════════════════════════════
elif selected == "Analisis Predictivo":
    st.markdown("<div class='module-card'>", unsafe_allow_html=True)
    st.markdown("Predicciones y tendencias del sistema de riego autonomo.")

    try:
        import pandas as pd
        import altair as alt

        data = call_api("GET", "analytics")
        if "error" not in data and isinstance(data, dict):
            df = pd.DataFrame(data)
        else:
            st.info("Endpoint /analytics no disponible. Mostrando datos de ejemplo.")
            df = pd.DataFrame({
                "hora": list(range(24)),
                "humedad": [70,68,65,63,60,58,57,60,65,70,72,68,
                            65,63,61,60,62,65,68,72,74,73,71,70],
                "caudal": [2.1,2.0,2.2,2.3,2.1,2.0,1.9,2.0,2.2,2.4,
                            2.5,2.3,2.1,2.0,2.0,2.1,2.2,2.3,2.4,2.5,
                            2.4,2.3,2.2,2.1],
            })

        tab1, tab2 = st.tabs(["Humedad del suelo", "Caudal de riego"])
        with tab1:
            chart1 = alt.Chart(df).mark_area(
                color=alt.Gradient(
                    gradient='linear',
                    stops=[
                        alt.GradientStop(color='#1976d2', offset=0),
                        alt.GradientStop(color='#90caf9', offset=1),
                    ],
                    x1=1, x2=1, y1=1, y2=0
                ),
                line={"color": "#1976d2"},
                opacity=0.6
            ).encode(
                x=alt.X("hora:Q", title="Hora del dia"),
                y=alt.Y("humedad:Q", title="Humedad suelo (%)", scale=alt.Scale(domain=[50,80])),
                tooltip=["hora", "humedad"]
            ).properties(title="Humedad del suelo - ultimas 24h", height=300)
            st.altair_chart(chart1, use_container_width=True)

        with tab2:
            chart2 = alt.Chart(df).mark_line(
                color="#43a047", strokeWidth=3, point=True
            ).encode(
                x=alt.X("hora:Q", title="Hora del dia"),
                y=alt.Y("caudal:Q", title="Caudal (L/h)", scale=alt.Scale(domain=[1.5,3.0])),
                tooltip=["hora", "caudal"]
            ).properties(title="Caudal de riego - ultimas 24h", height=300)
            st.altair_chart(chart2, use_container_width=True)

    except ImportError:
        st.error("Instala las dependencias: `pip install pandas altair`")


    st.markdown("</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# MOTOR IA
# ═══════════════════════════════════════════════════════════════════════════════
elif selected == "Motor IA":
    st.markdown("<div class='module-card'>", unsafe_allow_html=True)
    st.markdown("Envia un prompt al motor de IA del backend y obtiene una respuesta.")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Mostrar historial
    for msg in st.session_state.chat_history:
        role = "Usuario" if msg["role"] == "user" else "IA"
        icon = "👤" if msg["role"] == "user" else "🤖"
        st.markdown(f"**{icon} {role}:** {msg['content']}")

    with st.form(key="ai_form", clear_on_submit=True):
        prompt = st.text_area(
            "Escribe tu pregunta:",
            height=110,
            placeholder="Ejemplo: Cual es el estado actual del riego en la zona norte?"
        )
        submitted = st.form_submit_button("Enviar")

    if submitted and prompt.strip():
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.spinner("Procesando..."):
            response = call_api("POST", "ai", json={"prompt": prompt})
        if "error" not in response:
            answer = response.get("response", str(response))
            st.session_state.chat_history.append({"role": "ai", "content": answer})
        else:
            st.error(f"Error: {response.get('error')}")
            st.info("Verifica que el endpoint /api/v1/ai exista en tu FastAPI.")
        st.rerun()

    if st.button("Limpiar historial"):
        st.session_state.chat_history = []
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# DOCUMENTACION SCRUM
# ═══════════════════════════════════════════════════════════════════════════════
elif selected == "Documentacion Scrum":
    st.markdown("<div class='module-card'>", unsafe_allow_html=True)

    md_path = os.path.join(os.path.dirname(__file__), "..", "SCRUM.md")
    try:
        with open(md_path, "r", encoding="utf-8") as f:
            st.markdown(f.read())
    except FileNotFoundError:
        st.info("Archivo SCRUM.md no encontrado. Colócalo en la raiz del proyecto.")
        st.markdown("""
### Estructura Scrum del proyecto VRI Digital Twin

| Sprint | Objetivo | Estado |
|--------|----------|--------|
| Sprint 1 | Setup inicial, FastAPI + React | Completado |
| Sprint 2 | Gemelo Digital 3D + Streamlit | En curso |
| Sprint 3 | Motor IA + Analisis Predictivo | Pendiente |
| Sprint 4 | Integracion completa + Deploy | Pendiente |

**Backlog priorizado:**
- Estructura backend FastAPI
- Frontend React con Vite
- Consola Streamlit tecnica
- Modelo 3D avanzado
- Modulo RL Agent
- Exportar reportes PDF
""")

    st.markdown("</div>", unsafe_allow_html=True)


# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("Consola tecnica VRI Digital Twin  |  Frontend principal: React + Vite  |  API: FastAPI puerto 8000")
