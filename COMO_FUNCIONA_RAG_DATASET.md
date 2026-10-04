# 📊 Cómo el RAG Consume el Dataset - Explicación Visual

## 🔄 Flujo Completo del RAG

```
┌─────────────────────────────────────────────────────────────┐
│ 1. INICIALIZACIÓN (Primera vez - puede tomar 5-10 min)     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ Knowledge Base (9 archivos .md)                             │
├─────────────────────────────────────────────────────────────┤
│ [OK] 01_crops_corn_maiz.md                                  │
│ [OK] 02_crops_wheat_trigo.md                                │
│ [OK] 03_soils_types_tipos.md                                │
│ [OK] 04_soils_sensors_sensores.md                           │
│ [OK] 05_irrigation_vri_basics.md                            │
│ [OK] 06_irrigation_hardware_equipamiento.md                 │
│ [OK] 07_regulations_water_rights.md                         │
│ [OK] 08_regulations_environmental_impact.md                 │
│ ★★★ 09_real_world_dataset.md ★★★ ← AQUÍ ESTÁ EL DATASET   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ Text Splitting (chunks de 1000 caracteres)                  │
│ - Cada documento se divide en pedazos pequeños             │
│ - Overlap de 200 caracteres para mantener contexto         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ Embeddings Generation (1.11 GB de modelo)                   │
│ - Modelo: paraphrase-multilingual-mpnet-base-v2            │
│ - Convierte texto → vectores numéricos                      │
│ - Descarga automática la primera vez                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ FAISS Vector Store                                           │
│ - Base de datos de vectores en memoria                      │
│ - Permite búsqueda semántica ultra-rápida                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Cuando Haces una Pregunta

```
Usuario pregunta:
"¿Cuántos eventos de riego hubo en el dataset público?"
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ Pregunta → Embedding (vector)                                │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ FAISS busca los 4 chunks más relevantes                     │
│ (Búsqueda semántica por similitud de vectores)             │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ Resultados (Top 4 chunks)                                    │
├─────────────────────────────────────────────────────────────┤
│ 1. [09_real_world_dataset.md]                               │
│    "Total validated events: 789..."                          │
│                                                              │
│ 2. [09_real_world_dataset.md]                               │
│    "Irrigation Events (reconstructed)..."                    │
│                                                              │
│ 3. [09_real_world_dataset.md]                               │
│    "Standard irrigations: 432, Fertigations: 357..."        │
│                                                              │
│ 4. [05_irrigation_vri_basics.md]                            │
│    "VRI systems track irrigation events..."                 │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ Groq LLM (llama-3.3-70b-versatile)                         │
│                                                              │
│ Prompt: "Basándote SOLO en estos documentos, responde:     │
│          ¿Cuántos eventos de riego hubo...?"               │
│                                                              │
│ Contexto: [Los 4 chunks encontrados]                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ RESPUESTA GENERADA                                           │
├─────────────────────────────────────────────────────────────┤
│ "Según el dataset público integrado, se registraron un      │
│  total de 789 eventos de riego validados durante el         │
│  período de febrero a septiembre de 2025. De estos:         │
│  - 432 fueron irrigaciones estándar                          │
│  - 357 fueron fertigaciones"                                 │
│                                                              │
│ FUENTES:                                                     │
│ - 09_real_world_dataset.md (líneas 45-67)                   │
│ - 09_real_world_dataset.md (líneas 102-115)                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Qué Información del Dataset Está Disponible

El archivo `09_real_world_dataset.md` contiene:

### ✅ Estadísticas Clave
- **789 eventos de riego** totales validados
- **432 irrigaciones** estándar
- **357 fertigaciones**
- Período: Febrero - Septiembre 2025
- Localización: Arnesano, Apulia, Italia

### ✅ Información por Sector

| Sector | Cultivo | Filas de Datos | Archivo CSV |
|--------|---------|----------------|-------------|
| 1 | Tomate | 9,531 | dataset_zone_1_preprocessed.csv |
| 2 | Tomate | 11,929 | dataset_zone_2_preprocessed.csv |
| 4 | Zucchini | 12,676 | dataset_zone_4_preprocessed.csv |
| 5 | Arándanos | 11,814 | dataset_zone_5_preprocessed.csv |

### ✅ Variables Disponibles
- Humedad del suelo (0-100%)
- pH del suelo
- Conductividad eléctrica
- Datos meteorológicos (ERA5)
- Duración de riego
- Volumen de agua aplicado

### ✅ Umbrales por Cultivo
- Puntos de marchitez
- Capacidad de campo
- Puntos de saturación
- Triggers de inicio/fin de riego

---

## 🔍 Ejemplos de Preguntas que el RAG Puede Responder

### ✅ Sobre Eventos de Riego
- "¿Cuántos eventos de riego se registraron en total?"
- "¿Cuántas fertigaciones hubo versus irrigaciones normales?"
- "¿Cuál fue la duración promedio de los eventos de riego?"

### ✅ Sobre los Sectores
- "¿Cuántas filas de datos hay para cada zona?"
- "¿Qué cultivos se monitorearon en el dataset?"
- "¿En qué período se recolectaron los datos?"

### ✅ Sobre Variables
- "¿Qué variables meteorológicas incluye el dataset?"
- "¿Qué sensores de suelo se utilizaron?"
- "¿Cómo se mide el volumen de agua aplicado?"

### ✅ Sobre Umbrales
- "¿Cuál es el umbral de riego para tomates en campo abierto?"
- "¿Qué nivel de humedad indica estrés hídrico?"
- "¿Cuándo se activa el riego automático?"

---

## 🚀 Cómo Verificar que Funciona

### Opción 1: Script de Prueba (Ejecutando ahora)
```bash
python test_dataset_rag.py
```

**Lo que verás:**
1. Carga de 9 archivos .md ✓
2. Descarga del modelo de embeddings (1.11 GB) ← PRIMERA VEZ SOLAMENTE
3. Inicialización de FAISS
4. Consulta al RAG
5. Respuesta con "789 eventos"
6. Fuentes que incluyen `09_real_world_dataset.md`

### Opción 2: FastAPI Docs
```bash
cd backend
uvicorn app.main:app --reload
# Abre: http://localhost:8000/docs
```

Prueba en `POST /api/v1/chat`:
```json
{
  "question": "Según el dataset, ¿cuántos eventos de riego hubo?",
  "language": "es"
}
```

### Opción 3: Frontend Completo
```bash
# Terminal 1
cd backend
uvicorn app.main:app --reload

# Terminal 2
npm run dev
```

Abre el chatbot y pregunta sobre el dataset.

---

## ⏱️ Tiempos Esperados

### Primera Ejecución (Inicialización)
- **Descarga del modelo**: 5-10 minutos (1.11 GB)
- **Carga de documentos**: 2-3 segundos
- **Creación de FAISS index**: 10-15 segundos
- **Primera consulta**: 3-5 segundos

### Ejecuciones Siguientes
- **Carga de documentos**: 2-3 segundos (no descarga modelo)
- **Creación de FAISS index**: 10-15 segundos
- **Consultas**: 2-3 segundos cada una

---

## 🎯 Confirmación Visual

Cuando funcione correctamente, verás algo como:

```
===========================================================
RESPUESTA DEL RAG:
===========================================================
Según el dataset público integrado en el sistema VRI Digital 
Twin, se registraron un total de 789 eventos de riego 
validados. Estos eventos fueron reconstructed from valve 
telemetry data y abarcan el período desde el 17 de febrero 
hasta el 31 de agosto de 2025.

De estos 789 eventos:
- 432 fueron irrigaciones estándar
- 357 fueron fertigaciones

============================================================
FUENTES CITADAS (3 fuentes):
============================================================

--- Fuente 1 ---
Archivo: backend\data\knowledge_base\09_real_world_dataset.md
Contenido: **Irrigation Events (reconstructed from valve 
telemetry):**
- Total validated events: 789
- Standard irrigations: 432
- Fertigations: 357...
[OK] CONFIRMADO! El RAG esta leyendo el archivo del dataset

============================================================
VERIFICACION:
============================================================
[OK] La respuesta menciona el numero correcto de eventos (789)
[OK] Encontradas 2 fuentes del dataset

============================================================
CONCLUSION: El RAG esta consumiendo el dataset [OK]
============================================================
```

---

## 📝 Notas Importantes

1. **El modelo se descarga UNA SOLA VEZ**: Después queda en cache
2. **Los CSV NO se leen directamente**: El RAG lee el .md que DOCUMENTA el dataset
3. **Las fuentes siempre se citan**: Puedes verificar de dónde viene cada respuesta
4. **Funciona offline**: Después de descargar el modelo, solo necesitas internet para Groq LLM
5. **Es bilingüe**: Funciona igual en español e inglés

---

**Estado Actual:** El script está descargando el modelo de embeddings (36% completado). 
Esto es normal la primera vez y tomará 5-10 minutos dependiendo de tu conexión.

Una vez completado, el RAG responderá en 2-3 segundos todas las futuras consultas! 🚀
