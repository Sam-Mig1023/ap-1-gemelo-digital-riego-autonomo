# 📁 Estructura del Proyecto - VRI Digital Twin

**Generado**: 1790250988.3972347  
**Excluye**: `node_modules`, `venv`, `.git`, `__pycache__`, `dist`, `build`, `.kiro`, `.vscode`, `.idea`

---

## Árbol de Directorios

```
├── .env.example
├── .gitignore
├── CONTEXTO_PROYECTO_CLAUDE.md
├── Dockerfile
├── ESTADO_REQUISITOS.md
├── GUIA_PRUEBA_RAG.md
├── PROJECT_GUIDE.txt
├── PROJECT_STRUCTURE.md
├── PROJECT_STRUCTURE.txt
├── README.md
├── RESUMEN_REQUISITOS_PENDIENTES.md
├── SETUP_GUIDE.md
├── bun.lock
├── docker-compose.yml
├── generate_structure.py
├── index.html
├── metadata.json
├── package-lock.json
├── package.json
├── tailwind.config.js
├── tsconfig.json
├── vite.config.ts
├── backend/
│   ├── .env
│   ├── .env.example
│   ├── .gitignore
│   ├── Dockerfile
│   ├── README.md
│   ├── requirements.txt
│   ├── streamlit_backend.py
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── endpoints/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── chat.py
│   │   │   │   │   ├── fields.py
│   │   │   │   │   ├── health.py
│   │   │   │   │   ├── irrigation.py
│   │   │   │   │   ├── reports.py
│   │   │   │   │   ├── rl_engine.py
│   │   │   │   │   ├── sensors.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   ├── services/
│   │   │   ├── rag_service.py
│   ├── data/
│   │   ├── .gitignore
│   │   ├── README.md
│   │   ├── datasets/
│   │   │   ├── dataset_zone_1_preprocessed.csv
│   │   │   ├── dataset_zone_2_preprocessed.csv
│   │   │   ├── dataset_zone_4_preprocessed.csv
│   │   │   ├── dataset_zone_5_preprocessed.csv
│   │   ├── knowledge_base/
│   │   │   ├── 01_crops_corn_maiz.md
│   │   │   ├── 02_crops_wheat_trigo.md
│   │   │   ├── 03_soils_types_tipos.md
│   │   │   ├── 04_soils_sensors_sensores.md
│   │   │   ├── 05_irrigation_vri_basics.md
│   │   │   ├── 06_irrigation_hardware_equipamiento.md
│   │   │   ├── 07_regulations_water_rights.md
│   │   │   ├── 08_regulations_environmental_impact.md
│   │   │   ├── 09_real_world_dataset.md
│   ├── docs/
│   │   ├── rag_test_results.md
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_rag_service.py
├── src/
│   ├── App.tsx
│   ├── index.css
│   ├── main.tsx
│   ├── components/
│   │   ├── AgronomicChatbot.tsx
│   │   ├── ArchitectureAndCodeViewer.tsx
│   │   ├── ClosedLoopFeedbackModal.tsx
│   │   ├── FieldGISMap.tsx
│   │   ├── Header.tsx
│   │   ├── RBACAuditConsole.tsx
│   │   ├── RLDecisionConsole.tsx
│   │   ├── ReportExportStudio.tsx
│   │   ├── Sidebar.tsx
│   │   ├── TelemetryAnalytics.tsx
│   │   ├── WhatIfSimulator.tsx
│   ├── contexts/
│   │   ├── LanguageContext.tsx
│   │   ├── ThemeContext.tsx
│   ├── data/
│   │   ├── mockData.ts
│   ├── locales/
│   │   ├── en.ts
│   │   ├── es.ts
│   │   ├── index.ts
│   ├── services/
│   │   ├── anomalyDetectionEngine.ts
│   │   ├── apiClient.ts
│   │   ├── closedLoopController.ts
│   │   ├── codebaseData.ts
│   │   ├── digitalTwinEngine.ts
│   │   ├── groqService.ts
│   │   ├── reportGenerators.ts
│   │   ├── rlAgentEngine.ts
│   ├── types/
│   │   ├── index.ts
```

---

## Descripción de Carpetas Principales

### 📂 `src/` - Frontend React + TypeScript
- `components/` - 11 componentes React principales (GIS, Chatbot, RL Console, etc.)
- `services/` - Lógica de negocio (RL engine, Digital Twin, API client)
- `data/` - Datos mock (50K+ puntos de sensores)
- `types/` - Definiciones TypeScript
- `contexts/` - Context providers (Theme, Language)

### 📂 `backend/` - Backend FastAPI + Python
- `app/main.py` - Aplicación principal FastAPI
- `app/core/` - Configuración y base de datos
- `app/api/v1/endpoints/` - 6 módulos de endpoints REST
- `data/knowledge_base/` - Base de conocimiento agronómico (8 archivos .md)
- `requirements.txt` - Dependencias Python

### 📂 `public/` - Assets estáticos
- Favicon, imágenes, archivos públicos

### 📄 Archivos de Configuración
- `package.json` - Dependencias Node.js
- `tsconfig.json` - Configuración TypeScript
- `vite.config.ts` - Configuración Vite
- `docker-compose.yml` - Orquestación Docker
- `.env.example` - Variables de entorno de ejemplo

### 📄 Documentación
- `README.md` - Guía principal del proyecto
- `SETUP_GUIDE.md` - Guía de configuración detallada
- `CONTEXTO_PROYECTO_CLAUDE.md` - Contexto técnico completo
- `ESTADO_REQUISITOS.md` - Estado de cumplimiento de requisitos
