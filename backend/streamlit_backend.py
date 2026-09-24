# streamlit_backend.py â€“ Consola tÃ©cnica Streamlit del VRI Digital Twin
"""
Interfaz tÃ©cnica Streamlit para el sistema VRI Digital Twin.
MÃ³dulos: Dashboard, Gemelo Digital 3D, Mantenimiento,
         AnÃ¡lisis Predictivo, Motor IA, DocumentaciÃ³n Scrum.
Consume la API FastAPI que corre en el puerto 8000.
"""

import os
import streamlit as st
import requests

# â”€â”€ ConfiguraciÃ³n de la API â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = os.getenv("API_PORT", "8000")
BASE_URL = f"http://{API_HOST}:{API_PORT}/api/v1"
TIMEOUT = 10.0


def call_api(method: str, path: str, json: dict = None) -> dict:
    """Llama a la API FastAPI y devuelve el JSON o un dict con 'error'."""
    url = f"{BASE_URL}/{path}".rstrip("/")
    try:
        if method.upper() == "GET":
            resp = requests.get(url, timeout=TIMEOUT)
        elif method.upper() == "POST":
            resp = requests.post(url, json=json, timeout=TIMEOUT)
        else:
            return {"error": f"MÃ©todo no soportado: {method}"}
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:
        return {"error": str(exc)}


# â”€â”€ ConfiguraciÃ³n de pÃ¡gina â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
st.set_page_config(
    page_title="VRI Digital Twin â€“ Consola TÃ©cnica",
    page_icon="ðŸŒ¿",
    layout="wide",
)

# â”€â”€ CSS â€“ fondo blanco, sidebar oscuro â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #f5f7fa;
}

/* â”€â”€ Sidebar oscuro â”€â”€ */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1b2a 0%, #1a2e45 100%) !important;
    border-right: 3px solid #2196f3;
}
section[data-testid="stSidebar"] * { color: #dceeff !important; }
section[data-testid="stSidebar"] .stRadio div[role="radio"] {
    border-radius: 8px;
    padding: 4px 8px;
    transition: background 0.2s;
}
section[data-testid="stSidebar"] .stRadio div[role="radio"]:hover {
    background: rgba(33,150,243,0.25);
}

/* â”€â”€ Ãrea principal blanca â”€â”€ */
.main { background-color: #f5f7fa; }
.main .block-container {
    background-color: #f5f7fa;
    padding: 2rem 2rem 4rem 2rem;
    max-width: 1200px;
}

/* â”€â”€ Tarjetas de mÃ³dulo â”€â”€ */
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
.module-card h3, .module-card h2 { color: #0d47a1; }

/* â”€â”€ Encabezado de pÃ¡gina â”€â”€ */
h1 { color: #0d47a1 !important; font-weight: 700; }
h2, h3 { color: #1565c0 !important; }

/* â”€â”€ Botones â”€â”€ */
.stButton > button {
    background: linear-gradient(135deg, #1976d2, #0d47a1);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1.5rem;
    font-weight: 600;
    transition: transform 0.15s, box-shadow 0.15s;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(25,118,210,0.4);
}

/* â”€â”€ DataFrames â”€â”€ */
.stDataFrame { border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }

/* â”€â”€ MÃ©tricas â”€â”€ */
[data-testid="metric-container"] {
    background: white;
    border: 1px solid #e0e8f0;
    border-radius: 10px;
    padding: 16px;
    box-shadow: 0 2px 8px rgba(0,60,130,0.06);
}

/* â”€â”€ Info / success / error â”€â”€ */
.stAlert { border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# â”€â”€ Sidebar â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
with st.sidebar:
    st.markdown("## ðŸŒ¿ VRI Digital Twin")
    st.markdown("**Consola TÃ©cnica**")
    st.markdown("---")

    modules = [
        "ðŸ“Š Dashboard",
        "ðŸ›°ï¸ Gemelo Digital 3D",
        "ðŸ› ï¸ Mantenimiento",
        "ðŸ“ˆ AnÃ¡lisis Predictivo",
        "ðŸ¤– Motor IA",
        "ðŸ“š DocumentaciÃ³n Scrum",
    ]
    selected = st.radio("MÃ³dulos", modules, label_visibility="collapsed")

    st.markdown("---")
    st.markdown("### âš™ï¸ API")
    host = st.text_input("Host", value=API_HOST)
    port = st.text_input("Puerto", value=API_PORT)
    if st.button("Aplicar"):
        st.session_state["api_override"] = f"http://{host}:{port}/api/v1"
        st.success("âœ… URL actualizada")

    st.markdown("---")
    st.caption("Streamlit UI â€“ Solo uso tÃ©cnico")


# â”€â”€ TÃ­tulo principal â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
st.markdown(f"# {selected}")

# â”€â”€ MÃ³dulo: Dashboard â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
if "Dashboard" in selected:
    st.markdown("<div class='module-card'>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    health = call_api("GET", "health")
    is_healthy = health.get("status") == "healthy"

    with col1:
        status_icon = "âœ… Healthy" if is_healthy else "âŒ Sin conexiÃ³n"
        st.metric("Estado API", status_icon)
    with col2:
        st.metric("Host", f"{API_HOST}:{API_PORT}")
    with col3:
        st.metric("Base URL", "/api/v1")

    st.markdown("---")
    if is_healthy:
        st.success("**API FastAPI conectada correctamente**")
        with st.expander("Ver respuesta completa"):
            st.json(health)
    else:
        st.error("**No se pudo contactar la API FastAPI**")
        st.warning(f"Error: {health.get('error', 'Desconocido')}")
        st.info("Verifica que el servidor FastAPI estÃ© corriendo en `uvicorn app.main:app --reload --port 8000`")

    st.markdown("### ðŸ“Š EstadÃ­sticas")
    stats = call_api("GET", "stats")
    if "error" not in stats:
        try:
            import pandas as pd
            df = pd.DataFrame.from_dict(stats, orient="index", columns=["Valor"])
            st.dataframe(df, width='content')
        except Exception:
            st.json(stats)
    else:
        st.info("El endpoint `/stats` aÃºn no estÃ¡ disponible.")

    st.markdown("</div>", unsafe_allow_html=True)

# â”€â”€ MÃ³dulo: Gemelo Digital 3D â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
elif "Gemelo Digital" in selected:
    st.markdown("<div class='module-card'>", unsafe_allow_html=True)
    st.markdown("Vista 3D interactiva del sistema de riego autÃ³nomo")

    import streamlit.components.v1 as components

    # Modelo 3D con Three.js + GLTFLoader usando importmap ESM (sin mÃ³dulos)
    three_html = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    * { margin:0; padding:0; box-sizing:border-box; }
    body { background: #0f1923; overflow: hidden; }
    canvas { display: block; width: 100vw; height: 100vh; }
    #info {
      position:absolute; top:10px; left:50%; transform:translateX(-50%);
      color:#7eb8f7; font-family:Inter,sans-serif; font-size:13px;
      background:rgba(0,0,0,0.5); padding:6px 16px; border-radius:20px;
    }
    #error-msg {
      display:none; position:absolute; top:50%; left:50%;
      transform:translate(-50%,-50%);
      color:#ff6b6b; font-family:Inter,sans-serif; font-size:14px;
      text-align:center; background:rgba(0,0,0,0.7);
      padding:20px 30px; border-radius:12px; max-width:400px;
    }
  </style>
</head>
<body>
  <div id="info">ðŸŒ¿ VRI Digital Twin â€“ Sistema de Riego AutÃ³nomo | Arrastra para rotar</div>
  <div id="error-msg"></div>
  <canvas id="canvas"></canvas>

  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r134/three.min.js"></script>
  <script>
    // Escena principal
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0f1923);
    scene.fog = new THREE.Fog(0x0f1923, 20, 100);

    // CÃ¡mara
    const W = window.innerWidth, H = window.innerHeight;
    const camera = new THREE.PerspectiveCamera(60, W / H, 0.1, 500);
    camera.position.set(8, 6, 12);
    camera.lookAt(0, 0, 0);

    // Renderer
    const renderer = new THREE.WebGLRenderer({
      canvas: document.getElementById('canvas'),
      antialias: true
    });
    renderer.setSize(W, H);
    renderer.shadowMap.enabled = true;

    // Luces
    const ambient = new THREE.AmbientLight(0x334455, 1.5);
    scene.add(ambient);
    const dirLight = new THREE.DirectionalLight(0xffffff, 2);
    dirLight.position.set(10, 20, 10);
    dirLight.castShadow = true;
    scene.add(dirLight);
    const blueLight = new THREE.PointLight(0x4488ff, 1.5, 30);
    blueLight.position.set(-5, 5, 5);
    scene.add(blueLight);

    // â”€â”€â”€ Modelo: Campo de riego â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    // Terreno
    const groundGeo = new THREE.PlaneGeometry(30, 30, 20, 20);
    const groundMat = new THREE.MeshLambertMaterial({ color: 0x1a3a1a });
    const ground = new THREE.Mesh(groundGeo, groundMat);
    ground.rotation.x = -Math.PI / 2;
    ground.receiveShadow = true;
    scene.add(ground);

    // Grid
    const grid = new THREE.GridHelper(30, 30, 0x2a5a2a, 0x1e3e1e);
    grid.position.y = 0.01;
    scene.add(grid);

    // FunciÃ³n: crear planta (esfera verde)
    function makePlant(x, z) {
      const stem = new THREE.Mesh(
        new THREE.CylinderGeometry(0.05, 0.05, 0.6),
        new THREE.MeshLambertMaterial({ color: 0x4a7c3f })
      );
      stem.position.set(x, 0.3, z);
      stem.castShadow = true;
      scene.add(stem);

      const top = new THREE.Mesh(
        new THREE.SphereGeometry(0.25, 8, 8),
        new THREE.MeshLambertMaterial({ color: 0x3cb550 })
      );
      top.position.set(x, 0.75, z);
      top.castShadow = true;
      scene.add(top);
    }

    // Filas de plantas
    for (let r = -4; r <= 4; r += 2) {
      for (let c = -4; c <= 4; c += 2) {
        makePlant(c, r);
      }
    }

    // Aspersores (tubo + spray visual)
    function makeSprinkler(x, z, active) {
      const post = new THREE.Mesh(
        new THREE.CylinderGeometry(0.08, 0.08, 1.2),
        new THREE.MeshLambertMaterial({ color: 0x888888 })
      );
      post.position.set(x, 0.6, z);
      post.castShadow = true;
      scene.add(post);

      const head = new THREE.Mesh(
        new THREE.SphereGeometry(0.15, 8, 8),
        new THREE.MeshLambertMaterial({ color: active ? 0x00aaff : 0x555555 })
      );
      head.position.set(x, 1.25, z);
      scene.add(head);
    }

    makeSprinkler(-4, -4, true);
    makeSprinkler(0, -4, true);
    makeSprinkler(4, -4, false);
    makeSprinkler(-4, 4, true);
    makeSprinkler(4, 4, false);

    // Bomba central
    const pump = new THREE.Mesh(
      new THREE.BoxGeometry(1.5, 1, 1.5),
      new THREE.MeshLambertMaterial({ color: 0x2255aa })
    );
    pump.position.set(0, 0.5, 0);
    pump.castShadow = true;
    scene.add(pump);

    const pumpTop = new THREE.Mesh(
      new THREE.CylinderGeometry(0.3, 0.3, 0.8),
      new THREE.MeshLambertMaterial({ color: 0x3377cc })
    );
    pumpTop.position.set(0, 1.4, 0);
    scene.add(pumpTop);

    // TuberÃ­as (tubos entre aspersores)
    function makePipe(x1, z1, x2, z2) {
      const dx = x2 - x1, dz = z2 - z1;
      const len = Math.sqrt(dx * dx + dz * dz);
      const geo = new THREE.CylinderGeometry(0.06, 0.06, len);
      const mat = new THREE.MeshLambertMaterial({ color: 0x444455 });
      const mesh = new THREE.Mesh(geo, mat);
      mesh.position.set((x1 + x2) / 2, 0.05, (z1 + z2) / 2);
      mesh.rotation.z = Math.PI / 2;
      mesh.rotation.y = -Math.atan2(dz, dx);
      scene.add(mesh);
    }

    makePipe(0, 0, -4, -4);
    makePipe(0, 0, 0, -4);
    makePipe(0, 0, 4, -4);
    makePipe(0, 0, -4, 4);
    makePipe(0, 0, 4, 4);

    // Sensor IoT (cubo pequeÃ±o con luz)
    const sensor = new THREE.Mesh(
      new THREE.BoxGeometry(0.4, 0.4, 0.4),
      new THREE.MeshLambertMaterial({ color: 0xff9900 })
    );
    sensor.position.set(3, 0.2, 3);
    scene.add(sensor);
    const sensorLight = new THREE.PointLight(0xff9900, 1, 3);
    sensorLight.position.set(3, 0.8, 3);
    scene.add(sensorLight);

    // â”€â”€â”€ PartÃ­culas de agua â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    const particles = [];
    function spawnDroplets(x, z) {
      for (let i = 0; i < 15; i++) {
        const drop = new THREE.Mesh(
          new THREE.SphereGeometry(0.04, 4, 4),
          new THREE.MeshLambertMaterial({ color: 0x88ccff, transparent: true, opacity: 0.7 })
        );
        const angle = Math.random() * Math.PI * 2;
        const speed = 0.02 + Math.random() * 0.03;
        drop.position.set(x, 1.3, z);
        drop.userData = {
          vx: Math.cos(angle) * speed * 2,
          vy: 0.04 + Math.random() * 0.03,
          vz: Math.sin(angle) * speed * 2,
          life: 1.0
        };
        scene.add(drop);
        particles.push(drop);
      }
    }

    // â”€â”€â”€ Orbit Controls manual â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    let isDragging = false, lastX = 0, lastY = 0;
    let spherical = { theta: 0.8, phi: 0.7, radius: 18 };

    document.addEventListener('mousedown', e => { isDragging = true; lastX = e.clientX; lastY = e.clientY; });
    document.addEventListener('mouseup', () => { isDragging = false; });
    document.addEventListener('mousemove', e => {
      if (!isDragging) return;
      spherical.theta -= (e.clientX - lastX) * 0.008;
      spherical.phi = Math.max(0.1, Math.min(Math.PI / 2, spherical.phi - (e.clientY - lastY) * 0.008));
      lastX = e.clientX; lastY = e.clientY;
    });
    document.addEventListener('wheel', e => {
      spherical.radius = Math.max(5, Math.min(40, spherical.radius + e.deltaY * 0.05));
    });

    // â”€â”€â”€ Loop de animaciÃ³n â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    let frame = 0;
    function animate() {
      requestAnimationFrame(animate);
      frame++;

      // Spawn agua cada 90 frames en aspersores activos
      if (frame % 90 === 0) {
        spawnDroplets(-4, -4);
        spawnDroplets(0, -4);
        spawnDroplets(-4, 4);
      }

      // Animar partÃ­culas
      for (let i = particles.length - 1; i >= 0; i--) {
        const d = particles[i];
        d.userData.vy -= 0.003;
        d.position.x += d.userData.vx;
        d.position.y += d.userData.vy;
        d.position.z += d.userData.vz;
        d.userData.life -= 0.025;
        d.material.opacity = d.userData.life * 0.7;
        if (d.userData.life <= 0) {
          scene.remove(d);
          particles.splice(i, 1);
        }
      }

      // Pulsar luz del sensor
      sensorLight.intensity = 0.8 + Math.sin(frame * 0.05) * 0.5;

      // Orbit camera
      camera.position.x = spherical.radius * Math.sin(spherical.phi) * Math.sin(spherical.theta);
      camera.position.y = spherical.radius * Math.cos(spherical.phi);
      camera.position.z = spherical.radius * Math.sin(spherical.phi) * Math.cos(spherical.theta);
      camera.lookAt(0, 0.5, 0);

      renderer.render(scene, camera);
    }
    animate();

    // Resize
    window.addEventListener('resize', () => {
      const w = window.innerWidth, h = window.innerHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    });
  </script>
</body>
</html>"""

    components.html(three_html, height=560, scrolling=False)

    col1, col2, col3 = st.columns(3)
    twin = call_api("GET", "twin")
    with col1:
        st.metric("ðŸ’§ Aspersores activos", twin.get("active_sprinklers", 3) if "error" not in twin else "â€”")
    with col2:
        st.metric("ðŸŒ¡ï¸ Humedad suelo", twin.get("soil_humidity", "68%") if "error" not in twin else "â€”")
    with col3:
        st.metric("âš¡ Bomba", twin.get("pump_status", "ON") if "error" not in twin else "â€”")

    st.markdown("</div>", unsafe_allow_html=True)

# â”€â”€ MÃ³dulo: Mantenimiento â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
elif "Mantenimiento" in selected:
    st.markdown("<div class='module-card'>", unsafe_allow_html=True)
    st.markdown("GestiÃ³n y seguimiento de tareas de mantenimiento del sistema.")

    tasks = call_api("GET", "maintenance")
    if "error" not in tasks and isinstance(tasks, list) and len(tasks) > 0:
        try:
            import pandas as pd
            df = pd.DataFrame(tasks)
            st.dataframe(df, width='content')
        except Exception:
            st.json(tasks)
    else:
        st.info("â„¹ï¸ No hay tareas de mantenimiento registradas o el endpoint no estÃ¡ disponible.")
        # Datos de ejemplo
        st.markdown("**Tareas de ejemplo:**")
        example = [
            {"Tarea": "RevisiÃ³n filtros", "Prioridad": "Alta", "Estado": "Pendiente", "Fecha": "2025-10-01"},
            {"Tarea": "CalibraciÃ³n sensores", "Prioridad": "Media", "Estado": "En proceso", "Fecha": "2025-10-05"},
            {"Tarea": "Limpieza aspersores", "Prioridad": "Baja", "Estado": "Completado", "Fecha": "2025-09-20"},
        ]
        try:
            import pandas as pd
            st.dataframe(pd.DataFrame(example), width='content')
        except Exception:
            for t in example:
                st.write(t)

    st.markdown("</div>", unsafe_allow_html=True)

# â”€â”€ MÃ³dulo: AnÃ¡lisis Predictivo â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
elif "AnÃ¡lisis" in selected:
    st.markdown("<div class='module-card'>", unsafe_allow_html=True)
    st.markdown("Predicciones y tendencias del sistema de riego autÃ³nomo.")

    data = call_api("GET", "analytics")
    if "error" not in data and isinstance(data, dict):
        try:
            import pandas as pd
            import altair as alt
            df = pd.DataFrame(data)
            chart = alt.Chart(df).mark_line(point=True).encode(
                x=alt.X(df.columns[0], title="Tiempo"),
                y=alt.Y(df.columns[1], title="Valor"),
                color=alt.value("#4488ff"),
            ).properties(width="container", height=300)
            st.altair_chart(chart, width='content')
        except Exception:
            st.json(data)
    else:
        st.info("â„¹ï¸ Endpoint de analÃ­ticas no disponible. Mostrando datos de ejemplo.")
        try:
            import pandas as pd
            import altair as alt
            df = pd.DataFrame({
                "hora": list(range(24)),
                "humedad": [70, 68, 65, 63, 60, 58, 57, 60, 65, 70, 72, 68,
                            65, 63, 61, 60, 62, 65, 68, 72, 74, 73, 71, 70],
                "caudal": [2.1, 2.0, 2.2, 2.3, 2.1, 2.0, 1.9, 2.0, 2.2, 2.4,
                            2.5, 2.3, 2.1, 2.0, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5,
                            2.4, 2.3, 2.2, 2.1],
            })
            chart = alt.Chart(df).mark_line(point=True).encode(
                x=alt.X("hora:Q", title="Hora del dÃ­a"),
                y=alt.Y("humedad:Q", title="Humedad suelo (%)"),
                color=alt.value("#4488ff"),
            ).properties(title="Humedad del suelo â€“ Ãºltimas 24h", width="container", height=300)
            st.altair_chart(chart, width='content')
        except Exception:
            st.warning("Instala pandas y altair: `pip install pandas altair`")

    st.markdown("</div>", unsafe_allow_html=True)

# â”€â”€ MÃ³dulo: Motor IA â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
elif "Motor IA" in selected:
    st.markdown("<div class='module-card'>", unsafe_allow_html=True)
    st.markdown("EnvÃ­a un prompt al motor de IA del backend y obtÃ©n una respuesta.")

    with st.form(key="ai_form"):
        prompt = st.text_area("ðŸ’¬ Escribe tu prompt aquÃ­:", height=130,
                              placeholder="Ej: Â¿CuÃ¡l es el estado del riego en la zona norte?")
        submitted = st.form_submit_button("ðŸš€ Enviar")

    if submitted and prompt.strip():
        with st.spinner("Procesando..."):
            response = call_api("POST", "ai", json={"prompt": prompt})
        if "error" not in response:
            st.success("Respuesta recibida:")
            st.json(response)
        else:
            st.error(f"Error: {response.get('error')}")
            st.info("Verifica que el endpoint `/api/v1/ai` exista en tu FastAPI.")

    st.markdown("</div>", unsafe_allow_html=True)

# â”€â”€ MÃ³dulo: DocumentaciÃ³n Scrum â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
elif "Scrum" in selected:
    st.markdown("<div class='module-card'>", unsafe_allow_html=True)

    md_path = os.path.join(os.path.dirname(__file__), "..", "SCRUM.md")
    try:
        with open(md_path, "r", encoding="utf-8") as f:
            st.markdown(f.read())
    except FileNotFoundError:
        st.info("ðŸ“„ Archivo `SCRUM.md` no encontrado. ColÃ³calo en la raÃ­z del proyecto.")
        st.markdown("""
### Estructura Scrum del proyecto

| Sprint | Objetivo | Estado |
|--------|----------|--------|
| Sprint 1 | Setup inicial, FastAPI + React | âœ… Completado |
| Sprint 2 | Gemelo Digital 3D + Streamlit | ðŸ”„ En curso |
| Sprint 3 | Motor IA + AnÃ¡lisis Predictivo | â³ Pendiente |
| Sprint 4 | IntegraciÃ³n completa + Deploy | â³ Pendiente |

**Backlog priorizado:**
- [x] Estructura backend FastAPI
- [x] Frontend React con Vite
- [x] Consola Streamlit tÃ©cnica
- [ ] Modelo 3D avanzado (GLTF real)
- [ ] MÃ³dulo RL Agent
- [ ] Exportar reportes PDF
""")

    st.markdown("</div>", unsafe_allow_html=True)

# â”€â”€ Footer â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
st.markdown("---")
st.caption("âš¡ Consola tÃ©cnica VRI Digital Twin  â€¢  El frontend principal es React + Vite  â€¢  API: FastAPI")
