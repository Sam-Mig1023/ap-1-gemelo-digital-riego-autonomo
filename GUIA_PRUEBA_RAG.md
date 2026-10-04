# 🚀 Guía Rápida - Probar RAG Sistema (Fase 1)

## ✅ Estado Actual
- **SUBIDO AL REPO**: Commit `408274e` - "feat: Implementación completa de RAG con LangChain + Groq (Fase 1)"
- **SIN CONFLICTOS**: Integrado con últimos cambios de tu compañera
- **LISTO PARA PROBAR**: Todas las dependencias instaladas

---

## 🧪 Opción 1: Prueba Rápida (5 minutos)

### Paso 1: Verificar Imports
```bash
cd c:\Users\ather\Downloads\gemelitos\ap-1-gemelo-digital-riego-autonomo
python -c "from backend.app.services.rag_service import get_rag_service; print('✅ RAG OK')"
```

### Paso 2: Ejecutar Test Manual
```bash
python backend/tests/test_rag_service.py
```

**Qué esperar:**
- ✅ Health check pasa
- ✅ Inicialización exitosa
- ✅ 5 preguntas respondidas con fuentes
- ⏱️ Tiempo de respuesta < 5 segundos

---

## 🌐 Opción 2: Probar con FastAPI (10 minutos)

### Paso 1: Iniciar servidor backend
```bash
cd c:\Users\ather\Downloads\gemelitos\ap-1-gemelo-digital-riego-autonomo\backend
uvicorn app.main:app --reload
```

### Paso 2: Abrir interfaz Swagger
- Navega a: http://localhost:8000/docs

### Paso 3: Probar endpoints
1. **GET** `/api/v1/chat/health` → Ver estado del servicio RAG
2. **POST** `/api/v1/chat` → Enviar una pregunta:
   ```json
   {
     "question": "¿Cuánta agua necesita el maíz durante la floración?",
     "language": "es"
   }
   ```

**Respuesta esperada:**
```json
{
  "answer": "El maíz durante la floración requiere...",
  "sources": [
    {
      "content": "Extracto del documento...",
      "metadata": {
        "source": "backend/data/knowledge_base/01_crops_corn_maiz.md"
      }
    }
  ],
  "model": "llama-3.3-70b-versatile",
  "num_sources": 2
}
```

---

## 🎨 Opción 3: Probar Frontend Completo (15 minutos)

### Paso 1: Backend corriendo
```bash
cd backend
uvicorn app.main:app --reload
```

### Paso 2: Frontend en otra terminal
```bash
cd c:\Users\ather\Downloads\gemelitos\ap-1-gemelo-digital-riego-autonomo
npm run dev
```

### Paso 3: Abrir aplicación
- Navega a: http://localhost:5173
- Ve al **Chatbot Agronómico**
- Haz preguntas en español o inglés
- Verifica que aparezcan las **fuentes** debajo de cada respuesta

---

## 🧪 5 Preguntas de Prueba

1. **Cultivos (Maíz):**  
   `"¿Cuánta agua necesita el maíz durante la floración?"`

2. **Suelos:**  
   `"¿Qué tipos de suelo son mejores para riego por aspersión?"`

3. **Regulaciones:**  
   `"¿Cuáles son las normativas de riego en zonas áridas?"`

4. **Mejores Prácticas:**  
   `"¿Cuál es el mejor momento del día para regar cultivos?"`

5. **Dataset Público:**  
   `"Según el dataset público, ¿cuántos eventos de riego hubo en la zona 1?"`

---

## ✅ Criterios de Éxito

### Debe Funcionar:
- ✅ Todas las preguntas retornan respuestas relevantes
- ✅ Cada respuesta incluye al menos 1 fuente citada
- ✅ Fuentes referencian archivos correctos de la knowledge base
- ✅ Tiempo de respuesta < 5 segundos
- ✅ Funciona en español e inglés

### Puede Tener:
- ⚠️ Primera consulta más lenta (carga de modelos)
- ⚠️ Warnings sobre LF/CRLF (normal en Windows)

---

## 📁 Archivos Importantes

### Backend
- `backend/app/services/rag_service.py` - Servicio RAG principal
- `backend/app/api/v1/endpoints/chat.py` - Endpoint de chat
- `backend/data/knowledge_base/` - 9 archivos .md de conocimiento
- `backend/data/datasets/` - 4 archivos CSV del dataset público
- `backend/tests/test_rag_service.py` - Tests unitarios

### Frontend
- `src/components/AgronomicChatbot.tsx` - Chatbot con RAG integrado
- `src/services/apiClient.ts` - Cliente API con método chat()
- `src/services/groqService.ts` - Interfaz con tipos actualizados

### Configuración
- `backend/.env` - Tu API key (NO en repo)
- `backend/.env.example` - Template sin secrets
- `backend/requirements.txt` - Dependencias instaladas

---

## 🐛 Troubleshooting

### Error: "GROQ_API_KEY not set"
```bash
# Verifica que exista el archivo .env
ls backend/.env

# Si no existe, cópialo de .env.example y añade tu key
copy backend\.env.example backend\.env
# Luego edita backend/.env y pon tu API key real
```

### Error: "No module named 'langchain'"
```bash
# Reinstala dependencias
pip install -r backend/requirements.txt
```

### Error: "Knowledge base not found"
```bash
# Verifica que existan los archivos
ls backend/data/knowledge_base/
# Deberías ver 9 archivos .md
```

### Respuestas muy lentas (> 10s)
- Normal en la primera consulta (carga de modelos)
- Verifica tu conexión a internet
- Consultas siguientes deben ser < 5s

---

## 📊 Progreso Actual

### ✅ Completado (Tasks 1.1 - 1.5)
- [x] Knowledge base con 9 archivos + dataset público
- [x] Dependencias LangChain instaladas
- [x] RAG service implementado
- [x] Endpoint /api/v1/chat creado
- [x] Frontend integrado con RAG

### ⏳ Pendiente (Task 1.6)
- [ ] **Ejecutar pruebas manuales** ← AQUÍ ESTÁS
- [ ] Documentar resultados en `backend/docs/rag_test_results.md`
- [ ] Verificar criterios de éxito

### 🎯 Siguiente Fase
**Fase 2: LangFlow Visual Workflows**
- Instalación de LangFlow
- Diseño de 3 flujos visuales
- Documentación con screenshots

---

## 📝 Notas Importantes

1. **Tu API Key está segura**: El archivo `.env` está en `.gitignore` y nunca se subirá
2. **Dataset incluido**: 4 zonas de CSV ya están en el repo para pruebas
3. **Bilingüe**: Todo funciona en español e inglés automáticamente
4. **Sin conflictos**: Ya integrado con cambios de tu compañera (commit `433b104`)

---

## 🆘 ¿Necesitas Ayuda?

Si algo no funciona:
1. Revisa la sección de Troubleshooting arriba
2. Consulta `backend/docs/rag_test_results.md` para detalles técnicos
3. Verifica que todas las dependencias estén instaladas: `pip list | grep langchain`

---

**¡Listo para probar!** 🚀 Elige una de las 3 opciones arriba y comienza.
