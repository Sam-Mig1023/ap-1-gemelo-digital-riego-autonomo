# 🌱 Calendario Fenológico Automático con LangChain AI

## 📋 Resumen

Sistema inteligente de seguimiento fenológico que calcula automáticamente la etapa de desarrollo de cada cultivo y ajusta dinámicamente el coeficiente Kc para optimizar el riego.

**Tecnologías Clave:**
- ✅ LangChain Agents (ReAct pattern)
- ✅ RAG Integration (conocimiento agronómico)
- ✅ Custom Tools (5 herramientas especializadas)
- ✅ LLM Chains (recomendaciones de riego)
- ✅ Groq LLM (Llama-3.3-70b-versatile)

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                        │
├─────────────────────────────────────────────────────────────┤
│  • PhenologyPanel.tsx      - UI Component                   │
│  • phenologyService.ts     - API Client                     │
│  • digitalTwinEngine.ts    - Dynamic Kc Integration         │
│  • App.tsx                 - Auto-load phenology data       │
└─────────────────────────────────────────────────────────────┘
                              ↓ HTTP REST API
┌─────────────────────────────────────────────────────────────┐
│                  Backend FastAPI (Python)                   │
├─────────────────────────────────────────────────────────────┤
│  ENDPOINTS:                                                  │
│  • GET  /api/v1/crop-calendar/calendar                      │
│  • GET  /api/v1/crop-calendar/calendar/{zone_id}            │
│  • GET  /api/v1/crop-calendar/kc/{zone_id}                  │
│  • GET  /api/v1/crop-calendar/ai/phenology/{zone_id} 🤖    │
│  • POST /api/v1/crop-calendar/ai/irrigation-recommendation  │
│  • GET  /api/v1/crop-calendar/ai/tools                      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│           LangChain Services (AI Layer)                     │
├─────────────────────────────────────────────────────────────┤
│  phenology_agent_service.py                                 │
│                                                              │
│  🤖 ReAct Agent with Tools:                                 │
│     1. CalculatePhenology      - Stage computation          │
│     2. CalculateGDD            - Thermal time               │
│     3. QueryCropKnowledge      - RAG search                 │
│     4. GetKcRecommendation     - Kc database                │
│     5. CalculateWaterRequirement - ETc calculation          │
│                                                              │
│  💬 LLM Chain:                                              │
│     - Irrigation recommendation with reasoning              │
│     - Risk assessment                                       │
│     - Optimization tips                                     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Data Sources                             │
├─────────────────────────────────────────────────────────────┤
│  • crop_calendar.csv        - Planting dates                │
│  • KC_DATABASE (in-memory)  - FAO-56 coefficients           │
│  • rag_service.py           - Agronomic knowledge base      │
│  • FAISS vectorstore        - Semantic search               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Características Implementadas

### 1. **Cálculo Automático de Etapa Fenológica**

**Archivo:** `backend/app/api/v1/endpoints/crop_calendar.py`

```python
def calculate_stage_from_dates(planting_date, flowering_date, harvest_date, today):
    """
    Calcula la etapa actual basándose en:
    - Días desde siembra
    - Progreso hacia floración
    - Progreso hacia cosecha
    
    Retorna: (stage_id, stage_name, days_since_planting)
    """
```

**Etapas:**
- `initial` (0-20%): Emergencia y establecimiento
- `vegetative` (20-40%): Desarrollo vegetativo
- `flowering` (40-65%): Floración y cuajado
- `yield_formation` (65-85%): Formación de frutos
- `ripening` (85-100%): Maduración

### 2. **Coeficientes Kc Dinámicos (FAO-56)**

**Base de datos por cultivo y etapa:**

```python
KC_DATABASE = {
    "Tomate": {
        "initial": {"kc": 0.60, "duration_days": 20},
        "vegetative": {"kc": 0.90, "duration_days": 25},
        "flowering": {"kc": 1.15, "duration_days": 30},
        "yield_formation": {"kc": 1.20, "duration_days": 25},
        "ripening": {"kc": 0.80, "duration_days": 20}
    },
    "Calabacin": {...},
    "Arandano": {...}
}
```

### 3. **Agente LangChain con ReAct Pattern** 🤖

**Archivo:** `backend/app/services/phenology_agent_service.py`

El agente sigue el patrón **ReAct** (Reasoning + Acting):

```
Thought: ¿Qué información necesito?
Action: CalculatePhenology
Action Input: zone-1-nw
Observation: Zone: zone-1-nw, Stage: Floración, Kc: 1.15
Thought: Ahora consulto conocimiento agronómico
Action: QueryCropKnowledge  
Action Input: "requerimientos hídricos tomate en floración"
Observation: [Respuesta del RAG]
Thought: Ya puedo dar recomendación
Final Answer: [Análisis completo]
```

**5 Herramientas disponibles:**

1. **CalculatePhenology**: Calcula etapa actual, Kc y progreso
2. **CalculateGDD**: Suma térmica (Growing Degree Days)
3. **QueryCropKnowledge**: Búsqueda RAG en base de conocimiento
4. **GetKcRecommendation**: Info detallada de Kc por etapa
5. **CalculateWaterRequirement**: ETc = Kc × ET0

### 4. **Recomendaciones de Riego con LLM Chain**

```python
def get_irrigation_recommendation(zone_id, current_moisture, et0, rain_forecast):
    """
    Genera recomendación inteligente considerando:
    - Etapa fenológica y Kc actual
    - Humedad del suelo
    - Demanda atmosférica (ET0)
    - Pronóstico de lluvia
    
    Retorna:
    - Lámina recomendada (mm)
    - Razonamiento técnico
    - Nivel de confianza (0-1)
    - Factores de riesgo
    - Tips de optimización
    """
```

### 5. **Integración con Digital Twin Engine**

**Archivo:** `src/services/digitalTwinEngine.ts`

```typescript
// ANTES: Kc estático
const kc = 1.15;

// AHORA: Kc dinámico desde calendario fenológico
const kc = zone.kc !== undefined ? zone.kc : 1.15;
```

El Kc se actualiza automáticamente cada 24 horas desde el backend.

### 6. **Visualización en React**

**Componente:** `src/components/PhenologyPanel.tsx`

Features:
- ✅ Información de etapa fenológica actual
- ✅ Barra de progreso del ciclo
- ✅ Métricas clave (días desde siembra, a floración, a cosecha)
- ✅ Coeficiente Kc actualizado
- ✅ Análisis del agente AI con razonamiento
- ✅ Recomendación de riego con nivel de confianza
- ✅ Factores de riesgo identificados
- ✅ Tips de optimización

---

## 📊 Datos de Entrada

**CSV:** `backend/data/crop_calendar.csv`

```csv
zona,cultivo,fecha_siembra,fecha_floracion_esperada,fecha_cosecha
zone-1-nw,Tomate,2026-07-01,2026-08-15,2026-10-15
zone-2-ne,Tomate,2026-07-01,2026-08-15,2026-10-15
zone-4,Calabacin,2026-07-15,2026-08-20,2026-09-30
zone-5,Arandano,2026-01-01,2026-09-01,2026-11-30
```

---

## 🔌 API Endpoints

### **Endpoints Básicos**

#### `GET /api/v1/crop-calendar/calendar`
Obtiene etapas fenológicas de todas las zonas.

**Respuesta:**
```json
[
  {
    "zone_id": "zone-1-nw",
    "crop_name": "Tomate",
    "current_stage": "flowering",
    "stage_name": "Floración",
    "days_since_planting": 45,
    "days_to_flowering": 0,
    "days_to_harvest": 61,
    "kc": 1.15,
    "progress_pct": 42.5,
    "planting_date": "2026-07-01",
    "flowering_date": "2026-08-15",
    "harvest_date": "2026-10-15"
  }
]
```

#### `GET /api/v1/crop-calendar/kc/{zone_id}`
Obtiene solo el Kc actual de una zona.

**Respuesta:**
```json
{
  "zone_id": "zone-1-nw",
  "kc": 1.15,
  "stage": "flowering",
  "stage_name": "Floración",
  "crop": "Tomate"
}
```

### **Endpoints AI-Powered** 🤖

#### `GET /api/v1/crop-calendar/ai/phenology/{zone_id}`
Análisis completo con agente LangChain.

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "phenology": { /* datos fenológicos */ },
    "ai_reasoning": "El cultivo de Tomate en zone-1-nw se encuentra en etapa de floración (45 días desde siembra). Esta es una etapa crítica donde el Kc alcanza su valor máximo de 1.15...",
    "timestamp": "2026-09-24T10:30:00Z"
  },
  "agent_type": "LangChain ReAct Agent",
  "model": "llama-3.3-70b-versatile"
}
```

#### `POST /api/v1/crop-calendar/ai/irrigation-recommendation/{zone_id}`
Recomendación de riego con IA.

**Parámetros:**
- `current_moisture`: Humedad actual del suelo (%)
- `et0`: ET0 de referencia (mm/día)
- `rain_forecast`: Pronóstico de lluvia (mm)

**Respuesta:**
```json
{
  "success": true,
  "recommendation": {
    "zone_id": "zone-1-nw",
    "recommended_mm": 8.5,
    "reasoning": "Etapa de floración con Kc=1.15 y humedad al 22%. ETc calculado: 6.3 mm/día. Aplicar riego complementario.",
    "confidence": 0.88,
    "risk_factors": [
      "Pronóstico de lluvia incierto"
    ],
    "optimization_tips": [
      "Etapa Floración requiere monitoreo frecuente",
      "Considerar aplicación fraccionada en suelos arenosos"
    ]
  },
  "method": "LangChain LLM Chain + FAO-56"
}
```

#### `GET /api/v1/crop-calendar/ai/tools`
Lista las herramientas disponibles del agente.

---

## 💻 Uso en Frontend

### **1. Cargar datos fenológicos automáticamente**

```typescript
// En App.tsx
import { phenologyService } from './services/phenologyService';

useEffect(() => {
  const loadPhenologyData = async () => {
    const phenologyMap = await phenologyService.getMapVisualizationData();
    
    // Actualizar zonas con Kc dinámico
    setZones(prevZones => 
      prevZones.map(zone => {
        const phenology = phenologyMap.get(zone.id);
        if (phenology) {
          return {
            ...zone,
            kc: phenology.kc,
            cropName: phenology.crop_name,
            cropStage: phenology.current_stage,
            plantingDate: phenology.planting_date,
            floweringDate: phenology.flowering_date,
            harvestDate: phenology.harvest_date
          };
        }
        return zone;
      })
    );
  };
  
  loadPhenologyData();
  const interval = setInterval(loadPhenologyData, 24 * 60 * 60 * 1000);
  return () => clearInterval(interval);
}, []);
```

### **2. Usar el panel de fenología**

```tsx
import { PhenologyPanel } from './components/PhenologyPanel';

<PhenologyPanel 
  zone={selectedZone} 
  onClose={() => setShowPhenology(false)}
/>
```

### **3. Obtener Kc dinámico**

```typescript
import { getDynamicKc } from './services/phenologyService';

const kc = await getDynamicKc('zone-1-nw');
// kc = 1.15 (actualizado según etapa actual)
```

---

## 🧪 Testing

### **1. Probar endpoints básicos**

```bash
# Backend running
cd backend
python -m uvicorn app.main:app --reload

# Test calendar endpoint
curl http://localhost:8000/api/v1/crop-calendar/calendar

# Test Kc endpoint
curl http://localhost:8000/api/v1/crop-calendar/kc/zone-1-nw
```

### **2. Probar agente AI**

```bash
# AI phenology analysis
curl http://localhost:8000/api/v1/crop-calendar/ai/phenology/zone-1-nw

# AI irrigation recommendation
curl "http://localhost:8000/api/v1/crop-calendar/ai/irrigation-recommendation/zone-1-nw?current_moisture=22&et0=5.5&rain_forecast=0"

# List agent tools
curl http://localhost:8000/api/v1/crop-calendar/ai/tools
```

### **3. Verificar en frontend**

```bash
# Frontend running
npm run dev

# Abrir navegador
http://localhost:3000

# Ver consola del navegador
# Deberías ver:
# [Phenology] Loading crop calendar data...
# [Phenology] Updated zone-1-nw: Kc=1.15, Stage=Floración
# [Phenology] ✓ Crop calendar loaded successfully
```

---

## 📈 Beneficios

### **Precisión Agronómica**
- ✅ Kc ajustado automáticamente según etapa real
- ✅ Cálculos ETc más precisos
- ✅ Menos desperdicio de agua

### **Inteligencia Artificial**
- ✅ Razonamiento contextual con LangChain
- ✅ Recomendaciones basadas en múltiples factores
- ✅ Explicabilidad (XAI) del agente

### **Escalabilidad**
- ✅ Fácil agregar nuevos cultivos al KC_DATABASE
- ✅ Extensible con más herramientas (Tools)
- ✅ Integración RAG con conocimiento agronómico

### **UX Mejorado**
- ✅ Visualización clara de etapa fenológica
- ✅ Timeline del ciclo de cultivo
- ✅ Recomendaciones accionables

---

## 🔮 Próximas Mejoras

1. **Growing Degree Days (GDD) Real**
   - Integrar datos de temperatura reales
   - Cálculo preciso de suma térmica

2. **Ajuste de Kc por Estrés**
   - Considerar CWSI para ajustar Kc
   - Factor de estrés hídrico (Ks)

3. **Predicción de Etapas**
   - ML para predecir fechas de floración
   - Ajuste por condiciones climáticas

4. **Más Cultivos**
   - Expandir KC_DATABASE
   - Soporte para cultivos mixtos

5. **Alertas Proactivas**
   - Notificaciones de cambio de etapa
   - Alertas de necesidades críticas

---

## 📝 Dependencias

**Backend:**
```
langchain>=0.1.0
langchain-groq>=0.1.0
langchain-community>=0.0.20
faiss-cpu>=1.7.4
sentence-transformers>=2.2.2
```

**Frontend:**
```
react>=19.0.0
typescript>=5.0.0
lucide-react>=0.300.0
```

---

## 👨‍💻 Autores

Sistema implementado con LangChain para demostración de capacidades avanzadas de IA en agricultura de precisión.

**Stack:**
- Backend: FastAPI + LangChain + Groq
- Frontend: React + TypeScript
- AI: Llama-3.3-70b-versatile via Groq

---

## 📄 License

MIT - Parte del proyecto Gemelo Digital de Riego Autónomo
