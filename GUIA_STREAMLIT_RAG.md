# 🎯 Guía para Probar RAG en Streamlit

## ✅ Estado Actual

- **Backend FastAPI**: ✅ RAG integrado (endpoint `/api/v1/chat`)
- **Streamlit**: ✅ Módulo "RAG Chat" añadido
- **Frontend React**: ✅ Chatbot con RAG integrado

---

## 🚀 Cómo Iniciar Todo

### **Opción 1: Solo Streamlit + FastAPI (Recomendado para probar RAG)**

#### Paso 1: Iniciar Backend FastAPI
```bash
# Terminal 1 - En el directorio backend
cd c:\Users\ather\Downloads\gemelitos\ap-1-gemelo-digital-riego-autonomo\backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Espera a ver:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

#### Paso 2: Iniciar Streamlit
```bash
# Terminal 2 - En el directorio backend
cd c:\Users\ather\Downloads\gemelitos\ap-1-gemelo-digital-riego-autonomo\backend
streamlit run streamlit_backend.py
```

**Espera a ver:**
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.X.X:8501
```

#### Paso 3: Abrir Streamlit
1. Abre tu navegador en: **http://localhost:8501**
2. En el sidebar, selecciona **"🤖 RAG Chat"**
3. Click en **"🔍 Verificar Estado RAG"** (debería decir "✅ RAG Sistema Operativo")
4. Escribe una pregunta o usa las sugeridas

---

### **Opción 2: Todo Completo (Streamlit + FastAPI + React Frontend)**

Si también quieres el frontend React:

```bash
# Terminal 1 - Backend FastAPI
cd c:\Users\ather\Downloads\gemelitos\ap-1-gemelo-digital-riego-autonomo\backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Streamlit
cd c:\Users\ather\Downloads\gemelitos\ap-1-gemelo-digital-riego-autonomo\backend
streamlit run streamlit_backend.py

# Terminal 3 - Frontend React
cd c:\Users\ather\Downloads\gemelitos\ap-1-gemelo-digital-riego-autonomo
npm run dev
```

**URLs:**
- FastAPI Docs: http://localhost:8000/docs
- Streamlit: http://localhost:8501
- React Frontend: http://localhost:3000 (o el puerto que indique Vite)

---

## 🔍 Qué Probar en Streamlit RAG Chat

### 1. Verificar Estado
- Click en **"🔍 Verificar Estado RAG"**
- Debe mostrar: `✅ RAG Sistema Operativo`
- Expandir "Ver Detalles" para ver la configuración

### 2. Preguntas Sugeridas (Click en los botones)
- 💬 "¿Cuántos eventos de riego se registraron en el dataset público?"
- 💬 "¿Qué tipos de suelo son mejores para riego por aspersión?"
- 💬 "¿Cuánta agua necesita el maíz durante la floración?"
- 💬 "¿Cuáles son las normativas de riego en zonas áridas?"
- 💬 "¿Qué cultivos se monitorearon en el dataset de Italia?"

### 3. Preguntas Personalizadas
Escribe en el campo de texto cualquier pregunta sobre:
- Cultivos (maíz, trigo)
- Suelos y sensores
- Sistemas VRI
- Regulaciones
- El dataset público

### 4. Verificar Fuentes
- Cada respuesta tiene un expandible **"📚 Ver X Fuentes"**
- Click para ver de qué archivos .md proviene la información
- Verifica que cite `09_real_world_dataset.md` para preguntas del dataset

---

## 📸 Cómo Se Ve

```
┌─────────────────────────────────────────────────────┐
│ VRI Digital Twin - Consola Tecnica                  │
│                                                      │
│ Modulos:                                             │
│ ○ 📊 Dashboard                                      │
│ ● 🤖 RAG Chat                    ← SELECCIONADO    │
│ ○ 🛰️ Gemelo Digital 3D                             │
│ ○ 🔧 Mantenimiento                                  │
│ ○ 📈 Analisis Predictivo                            │
│ ○ 🤖 Motor IA                                       │
│ ○ 📚 Documentacion Scrum                            │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ 🤖 RAG Chat - Asistente Agronómico                  │
├─────────────────────────────────────────────────────┤
│                                                      │
│ [🔍 Verificar Estado RAG]                           │
│ ✅ RAG Sistema Operativo                            │
│                                                      │
│ ─────────────────────────────────────────────────   │
│                                                      │
│ 💬 Conversación                                      │
│                                                      │
│ ┌─────────────────────────────────────────────┐    │
│ │ 👤 Tú:                                       │    │
│ │ ¿Cuántos eventos de riego hubo en el        │    │
│ │ dataset público?                             │    │
│ └─────────────────────────────────────────────┘    │
│                                                      │
│ ┌─────────────────────────────────────────────┐    │
│ │ 🤖 Asistente:                                │    │
│ │ Según el dataset público integrado, se       │    │
│ │ registraron un total de 789 eventos de       │    │
│ │ riego validados durante el período de        │    │
│ │ febrero a septiembre de 2025...              │    │
│ │                                              │    │
│ │ ▼ 📚 Ver 3 Fuentes                           │    │
│ └─────────────────────────────────────────────┘    │
│                                                      │
│ 📝 Nueva Consulta                                    │
│ [Tu pregunta aquí...]        [🇪🇸 ES ▼]            │
│ [🚀 Enviar]  [🗑️ Limpiar Chat]                     │
│                                                      │
│ 💡 Preguntas Sugeridas                               │
│ [💬 ¿Cuántos eventos...]  [💬 ¿Qué tipos...]       │
│ [💬 ¿Cuánta agua...]       [💬 ¿Cuáles son...]      │
└─────────────────────────────────────────────────────┘
```

---

## ⚠️ Troubleshooting

### Error: "No se pudo conectar"
```
❌ No se pudo conectar: HTTPConnectionPool...
```

**Solución:** El backend FastAPI no está corriendo
```bash
cd backend
uvicorn app.main:app --reload
```

### Error: "RAG no inicializado"
```
⚠️ RAG no inicializado
```

**Causa:** Primera vez que se inicia, el RAG tarda en cargar
**Solución:** Espera 1-2 minutos y vuelve a verificar. El modelo de embeddings (1.11 GB) se descarga la primera vez.

### Error: "ModuleNotFoundError: streamlit_modules"
```
Error al cargar módulo RAG Chat: No module named 'streamlit_modules'
```

**Solución:** Asegúrate de estar en el directorio correcto
```bash
cd c:\Users\ather\Downloads\gemelitos\ap-1-gemelo-digital-riego-autonomo\backend
streamlit run streamlit_backend.py
```

### Timeout en consultas
```
⏱️ Timeout: La consulta tardó demasiado
```

**Causa:** Primera consulta siempre es más lenta (inicializa el modelo)
**Solución:** Normal. Consultas siguientes serán rápidas (2-3 segundos)

---

## 🎨 Características del Módulo RAG Chat

### ✅ Funcionalidades
- **Historial de chat** persistente en la sesión
- **Botones de preguntas sugeridas** para testing rápido
- **Visualización de fuentes** expandible
- **Soporte bilingüe** (ES/EN selector)
- **Estado del servicio** con health check
- **Limpiar chat** para empezar de nuevo
- **Timestamps** en cada mensaje

### 📊 Información Mostrada
- Número de fuentes citadas
- Modelo LLM usado
- Archivo origen de cada fuente
- Extracto del contenido

### 🎯 Casos de Uso
1. **Consulta rápida**: Pregunta técnica sobre riego
2. **Verificación de dataset**: Comprobar que lee el dataset público
3. **Testing multilingüe**: Cambiar idioma y hacer pregunta
4. **Exploración de KB**: Ver qué información tiene disponible

---

## 📝 Resumen de Archivos Modificados

### Backend
- ✅ `backend/streamlit_backend.py` - Módulo RAG añadido a la lista
- ✅ `backend/streamlit_modules/rag_chat.py` - Módulo completo de RAG Chat
- ✅ `backend/streamlit_modules/__init__.py` - Package init

### Ya Existían (Fase 1)
- ✅ `backend/app/api/v1/endpoints/chat.py` - Endpoint RAG
- ✅ `backend/app/services/rag_service.py` - Servicio RAG
- ✅ `backend/data/knowledge_base/` - 9 archivos .md

---

## 🚀 Próximos Pasos

1. **Probar Streamlit RAG** - Verificar que funciona
2. **Probar Frontend React** - Verificar chatbot ahí también
3. **Documentar resultados** - Task 1.6 testing
4. **Commit y push** - Subir cambios de Streamlit
5. **Continuar Fase 2** - LangFlow workflows

---

## 💡 Tip Final

Si solo quieres probar RAG sin instalar dependencias de frontend:

```bash
# Una sola terminal, dos comandos
cd backend
uvicorn app.main:app --reload & streamlit run streamlit_backend.py
```

O abre dos terminales separadas para ver los logs de cada uno.

---

**¡Listo para probar!** 🎉 Abre http://localhost:8501 después de iniciar los servicios.
