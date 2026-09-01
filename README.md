<div align="center">

# 🌾 VRI Digital Twin - Closed-Loop Autonomous Irrigation System

**Gemelo Digital para Riego Variable con Aprendizaje por Refuerzo**

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green)
![React](https://img.shields.io/badge/React-19+-61dafb)
![TypeScript](https://img.shields.io/badge/TypeScript-5.8+-3178c6)

</div>

---

## 📋 Descripción del Proyecto

Sistema inteligente de riego variable (VRI) que combina:
- 🤖 **Agente RL (PPO)**: Aprendizaje por refuerzo para optimizar riego
- 📊 **Gemelo Digital**: Simulación de dinámica hídrica del suelo
- 🌡️ **Multi-sensor**: Humedad, temperatura dosel, radar meteorológico
- 🎯 **Closed-Loop**: Retroalimentación automática y ajustes en tiempo real
- 📱 **Dashboard Web**: Interfaz React con visualización GIS interactiva

---

## ⚙️ Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:

### 1. **Node.js** (para frontend)
- Descarga: https://nodejs.org/
- Versión requerida: **16.0.0 o superior**
- Verificar instalación:
  ```bash
  node --version
  npm --version
  ```

### 2. **Python** (para backend)
- Descarga: https://www.python.org/downloads/
- Versión requerida: **3.10 o superior** (se recomienda 3.11+)
- **⚠️ Importante en Windows**: Marca la opción "Add Python to PATH" durante la instalación
- Verificar instalación:
  ```bash
  python --version
  ```

### 3. **Git** (opcional pero recomendado)
- Descarga: https://git-scm.com/
- Para clonar/actualizar el repositorio

---

## 🚀 Guía de Instalación Paso a Paso

### PASO 1️⃣: Clonar o Descargar el Proyecto

**Opción A: Usando Git (Recomendado)**
```bash
git clone <repository-url>
cd ap-1-gemelo-digital-riego-autonomo
```

**Opción B: Descargar ZIP**
- Descargar el proyecto como ZIP
- Extraer en la carpeta deseada
- Abrir terminal en esa carpeta

---

### PASO 2️⃣: Instalar Frontend (React/Vite)

**En la carpeta raíz del proyecto:**

1. Instalar dependencias de npm:
   ```bash
   npm install
   ```
   ⏳ Esto tardará 1-2 minutos. Espera a que termine.

2. Verificar que se instaló correctamente:
   ```bash
   npm --version
   npx vite --version
   ```

3. Crear archivo `.env.local` en la raíz:
   ```bash
   # En Windows (PowerShell):
   echo 'VITE_API_URL=http://localhost:8000
   VITE_APP_ENV=development
   VITE_DEBUG=true' > .env.local
   
   # En Mac/Linux:
   cat > .env.local << EOF
   VITE_API_URL=http://localhost:8000
   VITE_APP_ENV=development
   VITE_DEBUG=true
   EOF
   ```

   ✅ Verificar que se creó el archivo `.env.local`

---

### PASO 3️⃣: Instalar Backend (FastAPI)

**En la carpeta `backend/` del proyecto:**

1. Navegar a la carpeta backend:
   ```bash
   cd backend
   ```

2. Crear entorno virtual de Python:
   
   **Windows (PowerShell):**
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
   
   **Windows (CMD):**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
   
   **Mac/Linux:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

   ✅ Verificar que el entorno está activado (verás `(venv)` al inicio de la línea)

3. Instalar dependencias de Python:
   ```bash
   pip install --upgrade pip
   pip install fastapi uvicorn[standard] pydantic python-dotenv
   ```
   
   ⏳ Esto tardará 2-3 minutos. Espera a que termine.

4. Verificar instalación:
   ```bash
   pip list | findstr fastapi
   # o en Mac/Linux:
   pip list | grep fastapi
   ```

---

## ▶️ Ejecución del Proyecto

### Opción A: Iniciar Frontend y Backend por Separado (Recomendado para Desarrollo)

**Terminal 1 - Frontend (React):**
```bash
# Desde la raíz del proyecto (NO en backend/)
npm run dev
```

Deberías ver:
```
  VITE v6.4.3  ready in 2198 ms
  ➜  Local:   http://localhost:3000/
  ➜  Network: http://192.168.x.x:3000/
```

✅ **Frontend corriendo en:** `http://localhost:3000/`

---

**Terminal 2 - Backend (FastAPI):**
```bash
# Desde la carpeta backend/
cd backend
# Si el entorno virtual no está activado:
# Windows: .\venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Deberías ver:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started server process
INFO:     ✅ API Ready!
```

✅ **Backend corriendo en:** `http://localhost:8000/`

---

### 📂 Abrir Navegador

Abre tu navegador web y accede a:

| Componente | URL | Descripción |
|-----------|-----|-------------|
| **Frontend** | http://localhost:3000 | Aplicación React principal |
| **API Docs** | http://localhost:8000/docs | Documentación interactiva de endpoints |
| **Health Check** | http://localhost:8000/health | Verificar que backend está vivo |

---

### Opción B: Iniciar con Docker Compose

Si tienes Docker instalado:

```bash
# Desde la raíz del proyecto
docker-compose up -d
```

Esto iniciará:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- PostgreSQL: puerto 5432
- Redis: puerto 6379

Para detener:
```bash
docker-compose down
```

---

## ✅ Verificación de que Todo Funciona

### 1. **Verificar Frontend:**
- Abre http://localhost:3000
- Deberías ver el dashboard con:
  - Título: "CLOSED-LOOP DIGITAL TWIN VRI"
  - Mapa GIS interactivo con 4 zonas
  - Métricas de estrés hídrico

### 2. **Verificar Backend:**
- Abre http://localhost:8000/health
- Deberías ver JSON:
  ```json
  {
    "status": "healthy",
    "service": "VRI Digital Twin API",
    "version": "1.0.0"
  }
  ```

### 3. **Verificar API Docs:**
- Abre http://localhost:8000/docs
- Deberías ver Swagger UI con todos los endpoints listados

---

## 🏗️ Estructura del Proyecto

```
ap-1-gemelo-digital-riego-autonomo/
│
├── src/                          # Frontend React/TypeScript
│   ├── components/               # Componentes React
│   │   ├── FieldGISMap.tsx       # Mapa GIS interactivo
│   │   ├── RLDecisionConsole.tsx # Decisiones del agente RL
│   │   ├── TelemetryAnalytics.tsx
│   │   ├── WhatIfSimulator.tsx
│   │   └── ...
│   ├── services/
│   │   ├── apiClient.ts          # Cliente HTTP tipado
│   │   ├── rlAgentEngine.ts
│   │   └── ...
│   ├── data/
│   │   └── mockData.ts           # Datos de demostración
│   ├── types/
│   │   └── index.ts              # Tipos TypeScript
│   ├── App.tsx
│   └── main.tsx
│
├── backend/                      # Backend Python/FastAPI
│   ├── app/
│   │   ├── main.py              # Aplicación principal
│   │   ├── core/
│   │   │   ├── config.py        # Configuración
│   │   │   └── database.py      # DB (demo)
│   │   └── api/v1/
│   │       └── endpoints/
│   │           ├── health.py
│   │           ├── fields.py
│   │           ├── sensors.py
│   │           ├── rl_engine.py
│   │           ├── irrigation.py
│   │           └── reports.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── public/                      # Assets estáticos
├── package.json
├── tsconfig.json
├── vite.config.ts
├── docker-compose.yml
├── .env.local                   # Variables frontend (crear)
└── README.md                    # Este archivo
```

---

## 🔧 Troubleshooting - Solución de Problemas

### Error: "npm: command not found"
**Solución:** Node.js no está instalado o no está en PATH
- Descarga Node.js desde https://nodejs.org/
- En Windows, marca "Add to PATH" durante la instalación
- Reinicia la terminal/PowerShell después de instalar

### Error: "python: command not found"
**Solución:** Python no está instalado o no está en PATH
- Descarga Python desde https://www.python.org/downloads/
- En Windows, marca "Add Python to PATH" durante la instalación
- Reinicia la terminal/PowerShell después de instalar

### Error: "ModuleNotFoundError: No module named 'fastapi'"
**Solución:** Falta activar el entorno virtual o instalar dependencias
```bash
# Asegúrate de estar en la carpeta backend/
cd backend

# Activar entorno (Windows):
.\venv\Scripts\activate

# Instalar paquetes:
pip install fastapi uvicorn[standard]
```

### Error: "Port 3000 already in use"
**Solución:** Otro proceso usa el puerto 3000
```bash
# Ver qué proceso usa el puerto 3000 (Windows PowerShell):
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# O usar otro puerto:
npm run dev -- --port 3001
```

### Error: "Port 8000 already in use"
**Solución:** Similar al anterior
```bash
# Windows PowerShell:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# O usar otro puerto:
python -m uvicorn app.main:app --port 8001
```

### El frontend no puede conectarse al backend
**Solución:** Verificar que `VITE_API_URL` es correcto en `.env.local`
```
VITE_API_URL=http://localhost:8000
```

Si aún no funciona, abre la consola del navegador (F12) y revisa los errores CORS.

---

## 📡 API Endpoints Disponibles

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/v1/fields` | GET | Listar campos agrícolas |
| `/api/v1/fields/{field_id}/zones` | GET | Zonas de manejo |
| `/api/v1/sensors` | GET | Sensores disponibles |
| `/api/v1/rl-engine/infer-vri-rates` | POST | Inferencia RL |
| `/api/v1/irrigation/execute-decision` | POST | Ejecutar riego |
| `/api/v1/reports/generate` | POST | Generar reportes |

Para documentación completa: http://localhost:8000/docs

---

## 🔄 Cambios Principales Realizados

### Eliminado:
- ❌ Dependencia `@google/genai` (Gemini API)
- ❌ Variable de entorno `GEMINI_API_KEY`

### Implementado:
- ✅ Backend FastAPI funcional
- ✅ 6 módulos de API endpoints
- ✅ Cliente HTTP tipado (TypeScript)
- ✅ Documentación Swagger/OpenAPI
- ✅ CORS habilitado
- ✅ Modo desarrollo con hot-reload

---

## 📚 Documentación Adicional

- [backend/README.md](backend/README.md) - Documentación detallada del backend
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Guía de configuración avanzada
- [FastAPI Docs](https://fastapi.tiangolo.com/) - Documentación oficial
- [React Docs](https://react.dev/) - Documentación oficial

---

## 🎯 Próximos Pasos (Opcional)

1. **Conectar a Base de Datos:**
   - Implementar modelos SQLAlchemy
   - Conectar PostgreSQL + TimescaleDB

2. **Agregar Autenticación:**
   - JWT authentication
   - RBAC (Role-Based Access Control)

3. **Mejorar RL Engine:**
   - Integrar modelo PPO real
   - Agregar training continuo

4. **Deploy en Producción:**
   - Configurar Docker Compose completo
   - Nginx reverse proxy
   - SSL/TLS certificates

---

## 📞 Soporte

Si encuentras problemas:
1. Revisa la sección "Troubleshooting"
2. Verifica que los requisitos previos están instalados
3. Asegúrate de tener los puertos 3000 y 8000 disponibles
4. Revisa los logs en la terminal

---

<div align="center">

**¡Listo para desarrollar! 🚀**

Hecho con ❤️ para agricultura de precisión

</div>
