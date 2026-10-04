# 📋 CONTEXTO DEL PROYECTO - VRI Digital Twin

> **Para: Claude AI Assistant**  
> **Proyecto**: Sistema de Riego Variable Autónomo con Gemelo Digital  
> **Tecnologías**: React 19 + TypeScript + FastAPI + Python  
> **Dominio**: AgTech / Agricultura de Precisión

---

## 🎯 RESUMEN EJECUTIVO

Sistema web inteligente que optimiza el riego agrícola usando:
- **Gemelo Digital** que simula la dinámica hídrica del suelo
- **Agente RL (PPO)** que toma decisiones de riego automáticas
- **Multi-sensor IoT** (humedad TDR, temperatura IRT, radar meteorológico)
- **Closed-Loop** con retroalimentación para mejora continua
- **Chatbot agronómico** con Groq API (LLaMA 3.3) + STT/TTS

**Estado actual**: Frontend completo funcional, backend demo (sin BD real conectada)

---

## 🏗️ ARQUITECTURA TÉCNICA

### **Frontend** (React 19 + TypeScript + Vite)
```
src/
├── App.tsx                          # Componente raíz, state management
├── components/                      # 11 componentes principales
│   ├── Header.tsx                   # Barra superior con selector de rol
│   ├── Sidebar.tsx                  # Navegación lateral
│   ├── FieldGISMap.tsx              # Mapa GIS con 4 zonas (SVG)
│   ├── RLDecisionConsole.tsx        # Decisiones del agente RL + SHAP
│   ├── TelemetryAnalytics.tsx      # Gráficos de sensores (Recharts)
│   ├── WhatIfSimulator.tsx         # Simulador de escenarios
│   ├── ReportExportStudio.tsx      # Generador PDF/Excel/Word
│   ├── RBACAuditConsole.tsx        # Auditoría con SHA-256
│   ├── ClosedLoopFeedbackModal.tsx # Feedback post-riego
│   ├── AgronomicChatbot.tsx        # Chatbot con Groq + voz
│   └── ArchitectureAndCodeViewer.tsx # Docs técnicas
├── services/                        # Lógica de negocio
│   ├── apiClient.ts                # Cliente HTTP tipado (no usado aún)
│   ├── rlAgentEngine.ts            # Simulador PPO RL
│   ├── digitalTwinEngine.ts        # Modelo Green-Ampt + balance hídrico
│   ├── closedLoopController.ts     # Loop cerrado de aprendizaje
│   ├── anomalyDetectionEngine.ts   # Isolation Forest para anomalías
│   ├── reportGenerators.ts         # jsPDF, xlsx, docx
│   └── groqService.ts              # Integración con Groq API
├── data/
│   └── mockData.ts                 # Datos de demo (50K+ puntos)
├── types/
│   └── index.ts                    # 20+ interfaces TypeScript
└── contexts/
    ├── ThemeContext.tsx            # Modo claro/oscuro
    └── LanguageContext.tsx         # i18n (ES/EN)
```

### **Backend** (FastAPI + Python 3.11)
```
backend/
├── app/
│   ├── main.py                     # App FastAPI con CORS
│   ├── core/
│   │   ├── config.py               # Variables de entorno
│   │   └── database.py             # DB pool (demo, sin BD real)
│   └── api/v1/endpoints/
│       ├── health.py               # Health checks
│       ├── fields.py               # Gestión de campos
│       ├── sensors.py              # Telemetría IoT
│       ├── rl_engine.py            # Motor RL
│       ├── irrigation.py           # Control VRI
│       └── reports.py              # Generación de reportes
├── requirements.txt                # FastAPI, uvicorn, pydantic
└── Dockerfile                      # Imagen Docker
```

---

## 📊 COMPONENTES PRINCIPALES

### 1. **Gemelo Digital (Digital Twin)**
- **Archivo**: `src/services/digitalTwinEngine.ts`
- **Función**: Simula el comportamiento hídrico del suelo
- **Modelo**:
  - **Infiltración**: Green-Ampt (percolación vertical)
  - **Evapotranspiración**: FAO Penman-Monteith (ETc = ETo × Kc)
  - **Balance hídrico**: θ(t+1) = θ(t) + Riego + Lluvia - ETc - Percolación
- **Entradas**: Riego aplicado, lluvia, temperatura, cultivo
- **Salidas**: Humedad predicha por horizonte (10cm, 30cm, 60cm)

### 2. **Agente RL (Reinforcement Learning)**
- **Archivo**: `src/services/rlAgentEngine.ts`
- **Algoritmo**: PPO (Proximal Policy Optimization) *simulado*
- **Estado (observaciones)**:
  - Humedad volumétrica por horizonte
  - Temperatura del dosel IRT
  - VPD (Déficit de Presión de Vapor)
  - Radar meteorológico (dBZ)
  - Etapa fenológica del cultivo
  - Textura del suelo
- **Acción**: Dosis de riego en mm (0-20 mm)
- **Recompensa dual**:
  - R_agronomic: Minimiza estrés hídrico + maximiza eficiencia
  - R_economic: Minimiza costos de agua + energía
  - R_total = 0.65 × R_agronomic + 0.35 × R_economic
- **Explicabilidad**: Valores SHAP (cuánto influyó cada sensor)

### 3. **Closed-Loop (Ciclo Cerrado)**
- **Archivo**: `src/services/closedLoopController.ts`
- **Flujo**:
  1. **Decisión RL**: Agente recomienda dosis
  2. **Aprobación humana**: Agrónomo valida (RBAC)
  3. **Ejecución**: Válvulas VRI aplican agua
  4. **Observación**: Sensores miden resultado real
  5. **Feedback**: Comparar predicción vs realidad
  6. **Recalibración**: Ajustar parámetros del gemelo digital (Ksat)
  7. **Aprendizaje**: Actualizar política PPO
- **Métrica**: Reward = -|humedad_predicha - humedad_real| - 0.3×desperdicio

### 4. **Chatbot Agronómico**
- **Archivo**: `src/components/AgronomicChatbot.tsx`
- **LLM**: Groq API con LLaMA 3.3 (70B parámetros)
- **Modelos disponibles**:
  - llama-3.3-70b-versatile (recomendado)
  - llama-3.1-8b-instant (rápido)
  - mixtral-8x7b-32768 (contexto largo)
- **Features**:
  - STT (Speech-to-Text) con Web Speech API
  - TTS (Text-to-Speech) con SpeechSynthesis
  - Markdown rendering con syntax highlight
  - Modo bilingüe (ES/EN)
  - Context: Inyecta datos del campo, zonas, sensores
- **Limitación actual**: No tiene RAG (responde solo con conocimiento del LLM base)

### 5. **Multi-Sensor IoT**
- **Sensores simulados** (en mockData.ts):
  - **TDR** (Time Domain Reflectometry): Humedad volumétrica % a 10/30/60 cm
  - **IRT** (Infrared Thermometer): Temperatura del dosel °C
  - **Ambiente**: Temperatura, humedad relativa, viento
  - **Radar meteorológico**: Reflectividad dBZ (predicción lluvia)
- **Frecuencia**: 1 lectura cada 15 minutos (144 puntos/día/sensor)
- **Detección de anomalías**: Isolation Forest (±2.5σ)

### 6. **Visualización GIS**
- **Mapa SVG** con 4 zonas de manejo:
  - NW (Franco arenoso, 12.3 ha)
  - NE (Franco arcilloso, 10.8 ha)
  - SW (Franco limoso, 11.5 ha)
  - SE (Franco, 13.1 ha)
- **Capas visuales**:
  - Estrés hídrico (gradiente verde → amarillo → rojo)
  - Humedad volumétrica %
  - Dosis recomendada por RL
  - Radar meteorológico
  - Textura de suelo
- **Pivot central animado** (rotación CSS)

---

## 🎨 STACK TECNOLÓGICO COMPLETO

| Categoría | Tecnología | Versión | Uso |
|-----------|-----------|---------|-----|
| **Frontend** | React | 19.0.1 | Framework UI |
| | TypeScript | 5.8.2 | Tipado estático |
| | Vite | 6.2.3 | Bundler + dev server |
| | Tailwind CSS | 4.1.14 | Estilos utility-first |
| | Recharts | 3.10.1 | Gráficos de telemetría |
| | React Markdown | 10.1.0 | Render markdown del chatbot |
| | jsPDF | 4.2.1 | Generación de PDFs |
| | xlsx | 0.18.5 | Generación de Excel |
| | docx | 9.7.1 | Generación de Word |
| | Lucide React | 0.546.0 | Iconos SVG |
| **Backend** | FastAPI | 0.115 | Framework API REST |
| | Python | 3.11 | Lenguaje backend |
| | Uvicorn | 0.30 | ASGI server |
| | Pydantic | 2.8.2 | Validación de datos |
| **Previstos** | PostgreSQL | 15+ | Base de datos |
| | TimescaleDB | - | Time-series extension |
| | PostGIS | - | Geospatial extension |
| | Redis | 7+ | Cache + message broker |
| | Celery | - | Task queue |
| **DevOps** | Docker | - | Containerización |
| | Docker Compose | - | Orquestación local |

---

## 🔄 FLUJO DE UNA DECISIÓN DE RIEGO

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. LECTURA DE SENSORES                                         │
│    • TDR mide humedad a 10/30/60 cm                           │
│    • IRT mide temperatura del dosel                            │
│    • Radar detecta lluvia inminente                            │
└──────────────────────┬──────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────────┐
│ 2. DETECCIÓN DE ANOMALÍAS                                      │
│    • Isolation Forest filtra lecturas erróneas                 │
│    • Marca sensores defectuosos                                │
└──────────────────────┬──────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────────┐
│ 3. GEMELO DIGITAL                                              │
│    • Simula balance hídrico con Green-Ampt                     │
│    • Predice humedad futura                                    │
│    • Calcula déficit hídrico                                   │
└──────────────────────┬──────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────────┐
│ 4. AGENTE RL (PPO)                                             │
│    • Recibe estado (sensores + gemelo digital)                 │
│    • Política neuronal genera acción (dosis mm)                │
│    • Calcula confianza (0-1)                                   │
│    • Genera explicación SHAP                                   │
└──────────────────────┬──────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────────┐
│ 5. APROBACIÓN HUMANA (RBAC)                                    │
│    • Agrónomo ve decisión en UI                                │
│    • Puede: Aprobar / Rechazar / Anular                        │
│    • Registro en auditoría con SHA-256                         │
└──────────────────────┬──────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────────┐
│ 6. EJECUCIÓN VRI                                               │
│    • Señales PWM a válvulas del pivot                          │
│    • Aplicación diferenciada por zona                          │
│    • Ventana horaria optimizada (22:00-04:00)                 │
└──────────────────────┬──────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────────┐
│ 7. OBSERVACIÓN DE RESULTADO                                    │
│    • Sensores miden nueva humedad                              │
│    • Se compara predicción vs realidad                         │
│    • Se calcula error                                          │
└──────────────────────┬──────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────────┐
│ 8. FEEDBACK & RECALIBRACIÓN                                    │
│    • Modal de closed-loop se abre                              │
│    • Usuario registra outcome observado                        │
│    • Sistema recalibra Ksat del gemelo digital                 │
│    • Se calcula reward para RL                                 │
└──────────────────────┬──────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────────┐
│ 9. APRENDIZAJE                                                 │
│    • Experiencia (s, a, r, s') guardada                        │
│    • Política PPO se actualiza (batch retraining)              │
│    • Próxima decisión es más precisa                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚦 ESTADO ACTUAL DEL PROYECTO

### ✅ **Implementado y Funcionando**
- [x] Frontend React completo con 7 vistas
- [x] Mapa GIS interactivo con 4 zonas
- [x] Simulador de agente RL (PPO mockeado)
- [x] Gemelo digital (Green-Ampt + balance hídrico)
- [x] Chatbot con Groq API (LLaMA 3.3)
- [x] STT/TTS (Speech-to-Text / Text-to-Speech)
- [x] Sistema de reportes (PDF/Excel/Word)
- [x] Auditoría con SHA-256
- [x] RBAC (5 roles: Superadmin, Agrónomo, Productor, Técnico, RL Agent)
- [x] Modo claro/oscuro adaptativo
- [x] i18n bilingüe (Español/Inglés)
- [x] Closed-loop feedback modal
- [x] Detección de anomalías (Isolation Forest)
- [x] What-If Simulator
- [x] 50,000+ datos sintéticos de sensores

### 🟡 **Parcialmente Implementado**
- [ ] Backend FastAPI (estructura lista, endpoints demo sin BD real)
- [ ] API REST (swagger docs generado, pero no conectado al frontend)
- [ ] apiClient.ts (código listo pero no usado, frontend usa mockData)

### ❌ **No Implementado**
- [ ] Base de datos PostgreSQL + TimescaleDB
- [ ] Modelos RL reales (PyTorch/TensorFlow)
- [ ] Entrenamiento continuo del agente PPO
- [ ] Conexión a hardware VRI (válvulas, PLC, Modbus)
- [ ] Integración con sensores IoT reales
- [ ] WebSockets para telemetría en tiempo real
- [ ] Autenticación JWT
- [ ] Redis cache
- [ ] Celery task queue
- [ ] **RAG (Retrieval Augmented Generation) en chatbot** ❌
- [ ] **LangChain** ❌
- [ ] **LangFlow** ❌
- [ ] **Dataset público documentado** ❌
- [ ] **Sistema de notificaciones inteligentes** ❌

---

## 🎯 PROBLEMA ACTUAL: REQUISITOS DEL INGENIERO

**Contexto**: El ingeniero Ticona revisará el proyecto y pidió:

1. ✅ **Dataset público** → Actualmente solo datos mock en `mockData.ts`
2. ❌ **LangChain implementado** → Chatbot usa solo API directa de Groq
3. ❌ **LangFlow workflows** → No existe
4. ❓ **Sugerencias de qué implementar con LangFlow**

---

## 💡 RECOMENDACIONES DE CLAUDE

### **PRIORIDAD ALTA (Crítico para la evaluación)**

#### 1. **Dataset Público Documentado** 📊
**Por qué es crítico**: Demuestra reproducibilidad científica y transparencia.

**Qué hacer**:
- Exportar los 50K+ datos de `mockData.ts` a CSV estructurado
- Crear `DATASET_README.md` con metadatos (licencia, schema, citación)
- Publicar en Hugging Face Datasets con licencia CC BY 4.0
- Crear endpoint `/api/v1/dataset/export-dataset` para descarga

**Tiempo estimado**: 4-6 horas

**Archivos a crear**:
```
backend/data/
├── sensor_readings.csv              # 50K+ lecturas
├── irrigation_decisions.csv         # Decisiones RL con SHAP
├── weather_radar.csv                # Datos de radar
└── DATASET_README.md                # Documentación

backend/app/api/v1/endpoints/dataset.py  # Endpoint de descarga
```

**Beneficio**: Diferenciación fuerte vs otros proyectos que no comparten datos.

---

#### 2. **LangChain RAG (Retrieval Augmented Generation)** 🔗
**Por qué es crítico**: El chatbot actual solo tiene conocimiento base del LLM. Con RAG, responderá con fuentes verificables de documentos agronómicos.

**Qué hacer**:
1. **Crear base de conocimiento** en `backend/data/knowledge_base/`:
   ```
   knowledge_base/
   ├── cultivos/
   │   ├── papa_requerimientos_hidricos.md
   │   ├── papa_etapas_fenologicas.md
   │   └── papa_enfermedades.md
   ├── suelos/
   │   ├── textura_suelos.md
   │   ├── conductividad_hidraulica.md
   │   └── capacidad_campo.md
   ├── riego/
   │   ├── metodos_riego.md
   │   ├── vri_tecnologia.md
   │   └── eficiencia_riego.md
   └── normativas/
       └── ley_recursos_hidricos_peru.md
   ```

2. **Instalar dependencias**:
   ```bash
   pip install langchain langchain-groq langchain-community \
               chromadb faiss-cpu sentence-transformers
   ```

3. **Implementar servicio RAG** (`backend/app/services/rag_service.py`):
   - Cargar documentos con `DirectoryLoader`
   - Dividir en chunks con `RecursiveCharacterTextSplitter`
   - Embeddings con `HuggingFaceEmbeddings` (paraphrase-multilingual-MiniLM-L12-v2)
   - Vectorstore con FAISS
   - Chain RAG con `RetrievalQA`

4. **Endpoint RAG** (`backend/app/api/v1/endpoints/chatbot.py`):
   ```python
   @router.post("/chat")
   async def chat_with_rag(query: ChatQuery, x_groq_api_key: str):
       rag_service = get_rag_service(x_groq_api_key)
       result = rag_service.query(query.question)
       return {
           "answer": result["answer"],
           "sources": result["sources"]  # ← Clave: cita fuentes
       }
   ```

5. **Actualizar frontend** (`AgronomicChatbot.tsx`):
   - Cambiar de llamada directa a Groq → llamada a `/chat` con RAG
   - Mostrar fuentes citadas debajo de cada respuesta

**Tiempo estimado**: 1-2 días

**Beneficio**:
- Respuestas verificables con fuentes
- Conocimiento específico del dominio agrícola
- No inventa información (groundedness)
- Demuestra dominio de LangChain (requisito del ingeniero)

---

#### 3. **LangFlow Workflows Visuales** 🎨
**Por qué es crítico**: Muestra capacidad de diseñar pipelines de IA sin código hardcodeado.

**Qué hacer**:
1. **Instalar LangFlow**:
   ```bash
   pip install langflow
   langflow run --host 0.0.0.0 --port 7860
   ```

2. **Diseñar 3 flujos en la UI** (http://localhost:7860):

   **Flujo 1: Chatbot RAG Agronómico**
   ```
   [User Question] → [FAISS Retriever] → [Groq LLM] → [Answer + Sources]
   ```

   **Flujo 2: Sistema de Alertas Inteligentes**
   ```
   [Sensor Data] → [Anomaly Detector] → [LLM Classifier (Urgency)] 
       ↓                                           ↓
   [Digital Twin]                      [Message Generator (personalized)]
       ↓                                           ↓
   [RL Decision]  ───────────────────→  [Multi-channel Dispatcher]
                                           ├─ Email (critical)
                                           ├─ SMS (critical)
                                           ├─ Push (moderate)
                                           └─ Dashboard (info)
   ```

   **Flujo 3: Análisis de Decisión RL con Explicabilidad**
   ```
   [Zone State] → [RL Agent (PPO)] → [SHAP Explainer]
                       ↓                      ↓
                  [Decision]    ←─    [LLM Validator]
                       ↓
            [Human Approval Interface]
   ```

3. **Exportar flujos**:
   - Click "Export" → "Python Code"
   - Guardar en `backend/app/services/langflow_pipelines/`

4. **Integrar en backend**:
   ```python
   # backend/app/api/v1/endpoints/alerts.py
   from langflow.load import run_flow_from_json
   
   @router.post("/process-alert")
   async def process_alert(event: AlertEvent):
       flow_config = load("flows/alert_system.json")
       result = run_flow_from_json(flow_config, input_value=event.dict())
       return result
   ```

**Tiempo estimado**: 1 día

**Beneficio**:
- Muestra dominio de herramientas no-code/low-code
- Arquitectura visual clara para presentación
- Facilita mantenimiento por no programadores (agrónomos)

---

#### 4. **Sistema de Notificaciones Inteligentes con LLM** 📬
**Por qué es importante**: Demuestra aplicación práctica de IA más allá del chatbot.

**Qué hacer**:
1. **Clasificador de urgencia con LLM**:
   ```python
   # backend/app/services/notification_service.py
   def classify_urgency(event: dict) -> Literal["critical", "moderate", "info"]:
       prompt = f"""
       Analiza este evento de sensor y clasifica la urgencia:
       - Humedad: {event['moisture']}% (umbral: {event['threshold']}%)
       - Cultivo: {event['crop']} en etapa {event['growth_stage']}
       
       Responde solo: CRITICAL, MODERATE o INFO
       """
       response = groq_llm.invoke(prompt)
       return parse_urgency(response)
   ```

2. **Generador de mensajes personalizados**:
   ```python
   def generate_message(event: dict, role: str) -> str:
       prompt = f"""
       Genera un mensaje de alerta para un {role} sobre:
       {event}
       
       - Técnico si rol='agronomist'
       - Simple si rol='farmer'
       - Máximo 3 líneas
       """
       return groq_llm.invoke(prompt).content
   ```

3. **Dispatcher multi-canal**:
   ```python
   if urgency == "critical":
       send_email(message)
       send_sms(message)
   elif urgency == "moderate":
       send_push_notification(message)
   else:
       log_to_dashboard(message)
   ```

**Tiempo estimado**: 1 día

**Beneficio**:
- Aplicación práctica de LLM para clasificación
- Demuestra arquitectura event-driven
- Muestra consideración de UX (mensajes personalizados por rol)

---

### **PRIORIDAD MEDIA (Mejoras importantes)**

#### 5. **Conectar Frontend con Backend Real**
Actualmente el frontend usa `mockData.ts`. Conectar a FastAPI:
- Descomentar imports de `apiClient.ts` en `App.tsx`
- Reemplazar `useState(INITIAL_ZONES)` por `useEffect(() => fetch zones)`
- Probar integración end-to-end

**Tiempo**: 4-6 horas

---

#### 6. **Base de Datos PostgreSQL + TimescaleDB**
- Docker compose con PostgreSQL 15 + TimescaleDB extension
- Modelos SQLAlchemy en `backend/app/models/`
- Migraciones con Alembic
- Tablas: `fields`, `zones`, `sensors`, `telemetry`, `decisions`, `audit_logs`

**Tiempo**: 1-2 días

---

#### 7. **Autenticación JWT**
- Endpoint `/auth/login` con bcrypt
- Middleware JWT en FastAPI
- Token storage en localStorage (frontend)
- Protected routes por rol

**Tiempo**: 1 día

---

### **PRIORIDAD BAJA (Nice-to-have)**

#### 8. **WebSockets para Telemetría Real-Time**
- FastAPI WebSocket endpoint
- React useEffect con WebSocket connection
- Live updates de sensores sin polling

**Tiempo**: 1 día

---

#### 9. **Modelo RL Real (PyTorch/TensorFlow)**
- Sustituir simulación en `rlAgentEngine.ts`
- Entrenar PPO con Stable-Baselines3
- Guardar pesos en .pt file
- Endpoint `/rl-engine/infer` llama modelo real

**Tiempo**: 3-5 días (requiere dataset de entrenamiento)

---

## 📋 PLAN DE ACCIÓN RECOMENDADO (3-4 días)

### **Día 1: Dataset + Base de Conocimiento**
- [ ] AM: Exportar mockData a CSVs estructurados (sensor_readings.csv, etc.)
- [ ] AM: Crear DATASET_README.md con metadatos
- [ ] AM: Subir a Hugging Face Datasets
- [ ] PM: Crear 15-20 archivos .md en `knowledge_base/` (papa, suelo, riego)
- [ ] PM: Endpoint `/dataset/export-dataset`

### **Día 2: LangChain RAG**
- [ ] AM: Instalar dependencias LangChain
- [ ] AM: Implementar `rag_service.py` (loader, embeddings, FAISS, RetrievalQA)
- [ ] PM: Endpoint `/chat` con RAG
- [ ] PM: Actualizar `AgronomicChatbot.tsx` para mostrar fuentes
- [ ] Testing: Hacer 10 preguntas y verificar fuentes citadas

### **Día 3: LangFlow**
- [ ] AM: Instalar y levantar LangFlow UI
- [ ] AM: Diseñar Flujo 1 (Chatbot RAG)
- [ ] PM: Diseñar Flujo 2 (Alertas Inteligentes)
- [ ] PM: Diseñar Flujo 3 (Análisis RL)
- [ ] Exportar a Python y capturar screenshots

### **Día 4: Notificaciones + Testing Final**
- [ ] AM: Implementar `notification_service.py` (clasificador + generator)
- [ ] AM: Endpoint `/process-alert`
- [ ] PM: Testing end-to-end de todos los componentes
- [ ] PM: Actualizar README.md con sección de LangChain/LangFlow
- [ ] PM: Preparar demo para el ingeniero

---

## 🎬 SCRIPT DE DEMO PARA EL INGENIERO (5 minutos)

**[0:00-0:30] Introducción**
"Nuestro proyecto es un gemelo digital para riego de precisión con closed-loop learning. Usa RL para optimizar dosis, gemelo digital para simular hidráulica, y ahora agregamos LangChain + LangFlow."

**[0:30-1:30] Dataset Público**
"Publicamos un dataset de 50,000+ lecturas de sensores en Hugging Face con licencia CC BY 4.0."
*(Mostrar Hugging Face page + endpoint `/dataset/metadata`)*

**[1:30-3:00] Chatbot RAG**
"Implementamos RAG con base de conocimiento agronómica. No inventa, cita fuentes."
*(Hacer pregunta: "¿Cuál es el Kc de papa en fase media?")*
*(Mostrar respuesta: "1.15 según papa_requerimientos_hidricos.md")*

**[3:00-4:00] LangFlow Workflows**
"Diseñamos 3 workflows visuales: Chatbot RAG, Alertas Inteligentes, y Análisis RL con explicabilidad."
*(Mostrar screenshots de LangFlow UI con los 3 flujos)*

**[4:00-4:45] Notificaciones Inteligentes**
"Sistema de alertas que clasifica urgencia con LLM y personaliza mensajes por rol."
*(POST /process-alert, mostrar JSON response con urgency: "critical" y mensajes personalizados)*

**[4:45-5:00] Cierre**
"En resumen: dataset abierto, LangChain RAG con fuentes verificables, LangFlow workflows exportables, y notificaciones inteligentes multi-canal. Todo integrado en un sistema full-stack."

---

## 📚 RECURSOS Y REFERENCIAS

### Documentación
- **LangChain Python**: https://python.langchain.com/docs/
- **LangFlow**: https://github.com/logspace-ai/langflow
- **Groq API**: https://console.groq.com/docs
- **FastAPI**: https://fastapi.tiangolo.com/
- **React**: https://react.dev/
- **Hugging Face Datasets**: https://huggingface.co/docs/datasets

### Papers Relevantes
- **PPO**: "Proximal Policy Optimization Algorithms" (Schulman et al., 2017)
- **Green-Ampt**: "Studies on Soil Physics" (Green & Ampt, 1911)
- **SHAP**: "A Unified Approach to Interpreting Model Predictions" (Lundberg & Lee, 2017)
- **RAG**: "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" (Lewis et al., 2020)

---

## 🆘 PREGUNTAS FRECUENTES PARA CLAUDE

**P: ¿Cómo ejecuto el proyecto?**
```bash
# Frontend
npm install
npm run dev  # → http://localhost:3000

# Backend
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python -m uvicorn app.main:app --reload  # → http://localhost:8000
```

**P: ¿Dónde están los datos?**
R: `src/data/mockData.ts` → 50K+ puntos sintéticos de sensores, decisiones RL, etc.

**P: ¿El chatbot funciona?**
R: Sí, pero necesitas API key de Groq (gratis en console.groq.com/keys). La guardas en localStorage desde el botón de configuración del chatbot.

**P: ¿Por qué no usa la base de datos?**
R: Está en modo "demo". El backend tiene la estructura pero `database.py` solo hace logs. Para conectar BD real, necesitas PostgreSQL + actualizar `DATABASE_URL` en `.env`.

**P: ¿El agente RL es real?**
R: No, es una simulación matemática en `rlAgentEngine.ts`. Para modelo real necesitas entrenar PPO con TensorFlow/PyTorch.

**P: ¿Qué falta para impresionar al ingeniero?**
R: Lo crítico:
1. Dataset público en Hugging Face ✅
2. LangChain RAG con fuentes ✅
3. LangFlow workflows (screenshots) ✅
4. Notificaciones inteligentes ✅

---

## ✅ CHECKLIST DE VERIFICACIÓN

Antes de presentar al ingeniero:

- [ ] Dataset CSV descargable desde `/dataset/export-dataset`
- [ ] DATASET_README.md con licencia y citación
- [ ] Dataset publicado en Hugging Face (o al menos preparado)
- [ ] 15+ archivos .md en `knowledge_base/`
- [ ] RAG funcionando: pregunta → respuesta + fuentes citadas
- [ ] 3 flujos LangFlow diseñados y exportados
- [ ] Screenshots de LangFlow guardados para presentación
- [ ] Endpoint `/process-alert` devuelve urgencia + mensajes
- [ ] README.md actualizado con sección de LangChain/LangFlow
- [ ] Backend corriendo sin errores
- [ ] Frontend corriendo sin errores
- [ ] Chatbot con Groq API Key configurada

---

**FIN DEL DOCUMENTO DE CONTEXTO**

Este documento proporciona a Claude toda la información necesaria para:
1. Entender la arquitectura del proyecto
2. Conocer el estado actual
3. Saber qué falta implementar
4. Tener recomendaciones específicas y priorizadas
5. Poder ayudar en implementación de cualquier componente

**Última actualización**: 2024-09-24
