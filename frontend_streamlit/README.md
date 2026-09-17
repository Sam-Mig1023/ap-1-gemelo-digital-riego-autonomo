# 🌾 VRI Digital Twin — Frontend Streamlit

Frontend desarrollado en **Python + Streamlit** que consume la **API REST FastAPI** del backend.

## Stack

| Capa | Tecnología |
|---|---|
| Frontend | Python + Streamlit |
| Comunicación | API REST (requests HTTP) |
| Visualización | Plotly |
| Datos | pandas + numpy |

## Estructura

```
frontend_streamlit/
├── app.py              # Punto de entrada principal (sidebar + router)
├── api_client.py       # Cliente HTTP que consume la API FastAPI
├── requirements.txt    # Dependencias Python
├── .env.example        # Variables de entorno
└── pages/
    ├── dashboard.py        # KPIs y estado general
    ├── gemelo_digital.py   # Mapa del campo y zonas de manejo
    ├── agente_rl.py        # Inferencia PPO y gestión de decisiones
    ├── telemetria.py       # Sensores y series de tiempo
    ├── control_riego.py    # Ejecución y control del riego
    └── reportes.py         # Generación y descarga de reportes
```

## Instalación

```bash
cd frontend_streamlit

# Crear entorno virtual
python -m venv venv
# Windows:
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar URL del backend
copy .env.example .env
# Editar .env si el backend corre en otro puerto
```

## Ejecución

Primero inicia el backend FastAPI (desde `../backend/`):
```bash
cd ../backend
python -m uvicorn app.main:app --reload --port 8000
```

Luego inicia Streamlit:
```bash
streamlit run app.py
```

Abre: **http://localhost:8501**

## Módulos

| Módulo | Descripción | Endpoint API usado |
|---|---|---|
| 🏠 Dashboard | KPIs, estado del campo, tendencias | `/health`, `/api/v1/fields/`, `/api/v1/irrigation/status` |
| 🗺️ Gemelo Digital | Mapa 2D del campo por zona y capa | `/api/v1/fields/field-001/zones` |
| 🤖 Agente RL | Inferencia PPO, SHAP, aprobar/anular | `/api/v1/rl-engine/infer-vri-rates` |
| 📡 Telemetría | Series de tiempo, mapa de calor, ingesta | `/api/v1/sensors/`, `/api/v1/sensors/telemetry/ingest` |
| 💧 Control de Riego | Ejecución, manual, emergencia, schedule | `/api/v1/irrigation/*` |
| 📄 Reportes | Generar, historial, descarga CSV | `/api/v1/reports/*` |
