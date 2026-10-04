# 🚀 Guía Rápida: Calendario Fenológico AI

## 📝 Resumen en 30 segundos

Acabas de agregar un **agente LangChain** que calcula automáticamente:
- 🌱 Etapa fenológica actual de cada cultivo
- 📊 Coeficiente Kc dinámico (reemplaza valores fijos)
- 💧 Recomendaciones de riego inteligentes
- 🤖 Razonamiento explicable con ReAct pattern

---

## ⚡ Inicio Rápido (3 pasos)

### 1️⃣ Instalar dependencias adicionales

```bash
cd backend
pip install langchain langchain-groq langchain-community
```

### 2️⃣ Configurar GROQ_API_KEY (opcional para AI features)

En `backend/.env`:
```env
GROQ_API_KEY=gsk_tu_api_key_aquí
```

> **Nota:** Puedes obtener una API key gratis en https://console.groq.com

### 3️⃣ Probar el sistema

```bash
# Probar agente AI
cd backend
python test_phenology_agent.py

# Iniciar backend
python -m uvicorn app.main:app --reload

# En otra terminal: iniciar frontend
cd ..
npm run dev
```

---

## 🎯 Endpoints Principales

### Básicos (sin AI)
```bash
# Ver calendario completo
curl http://localhost:8000/api/v1/crop-calendar/calendar

# Ver Kc de una zona
curl http://localhost:8000/api/v1/crop-calendar/kc/zone-1-nw
```

### AI-Powered 🤖
```bash
# Análisis con agente LangChain
curl http://localhost:8000/api/v1/crop-calendar/ai/phenology/zone-1-nw

# Recomendación de riego
curl "http://localhost:8000/api/v1/crop-calendar/ai/irrigation-recommendation/zone-1-nw?current_moisture=22&et0=5.5"

# Ver herramientas del agente
curl http://localhost:8000/api/v1/crop-calendar/ai/tools
```

---

## 📊 Ver en el Frontend

1. Inicia el frontend: `npm run dev`
2. Abre: http://localhost:3000
3. **Consola del navegador** mostrará:
   ```
   [Phenology] Loading crop calendar data...
   [Phenology] Updated zone-1-nw: Kc=1.15, Stage=Floración
   [Phenology] ✓ Crop calendar loaded successfully
   ```

4. El **mapa GIS** ahora muestra:
   - 🌱 Nombre del cultivo
   - 📈 Etapa fenológica
   - 📊 Kc actualizado dinámicamente
   - 📅 Timeline del calendario

---

## 🔧 Personalizar Cultivos

Edita `backend/data/crop_calendar.csv`:

```csv
zona,cultivo,fecha_siembra,fecha_floracion_esperada,fecha_cosecha
zone-1-nw,Tomate,2026-07-01,2026-08-15,2026-10-15
zone-2-ne,Maiz,2026-06-15,2026-08-30,2026-11-15
```

Agrega Kc en `backend/app/services/phenology_agent_service.py`:

```python
KC_DATABASE = {
    "Maiz": {
        "initial": {"kc": 0.40, "duration_days": 25},
        "vegetative": {"kc": 0.80, "duration_days": 30},
        "flowering": {"kc": 1.20, "duration_days": 35},
        "yield_formation": {"kc": 1.15, "duration_days": 30},
        "ripening": {"kc": 0.60, "duration_days": 20}
    }
}
```

---

## 🧪 Testing Rápido

```bash
# Test completo del agente
cd backend
python test_phenology_agent.py

# Deberías ver:
# ✓ Basic calculation works!
# ✓ All tools loaded!
# ✓ AI analysis works!
# ✓ Irrigation recommendation works!
```

---

## 🎨 Componentes React Disponibles

### PhenologyPanel
Muestra análisis completo de fenología con AI:

```tsx
import { PhenologyPanel } from './components/PhenologyPanel';

<PhenologyPanel zone={selectedZone} />
```

### Servicio de API
```typescript
import { phenologyService } from './services/phenologyService';

// Obtener Kc dinámico
const kc = await phenologyService.getDynamicKcForZone('zone-1-nw');

// Análisis AI completo
const analysis = await phenologyService.getAIPhenologyAnalysis('zone-1-nw');

// Recomendación de riego
const rec = await phenologyService.getAIIrrigationRecommendation(
  'zone-1-nw', 22, 5.5, 0
);
```

---

## 🐛 Troubleshooting

### Error: "GROQ_API_KEY not set"
**Solución:** Agrega tu API key en `backend/.env`:
```env
GROQ_API_KEY=gsk_...
```

### Error: "Module 'langchain' not found"
**Solución:** Instala dependencias:
```bash
cd backend
pip install langchain langchain-groq langchain-community
```

### Los datos no se actualizan en frontend
**Solución:** 
1. Verifica que el backend esté corriendo: http://localhost:8000/docs
2. Revisa la consola del navegador para errores
3. Refresca la página (F5)

### El agente AI es lento
**Solución:** 
- Normal, puede tomar 10-30 segundos
- El agente ReAct hace múltiples llamadas al LLM
- Usa endpoints básicos (`/calendar`, `/kc`) para respuestas rápidas

---

## 📚 Documentación Completa

- **[CALENDARIO_FENOLOGICO_AI.md](./CALENDARIO_FENOLOGICO_AI.md)** - Documentación técnica completa
- **[README.md](./README.md)** - Guía general del proyecto
- **API Docs:** http://localhost:8000/docs (cuando el backend corre)

---

## 🎯 Lo Más Importante

1. **Kc ahora es dinámico** ✅
   - Se actualiza automáticamente según etapa fenológica
   - Reemplaza valores fijos en `digitalTwinEngine.ts`

2. **Agente LangChain con 5 herramientas** 🤖
   - ReAct pattern para razonamiento
   - Integración RAG con base de conocimiento
   - Recomendaciones explicables

3. **Visualización en React** 📊
   - Componente `PhenologyPanel` listo para usar
   - Integración automática en `App.tsx`
   - Actualización cada 24 horas

---

## ❓ ¿Necesitas ayuda?

- Ver logs del backend: Terminal donde corre `uvicorn`
- Ver logs del frontend: Consola del navegador (F12)
- Probar endpoints: http://localhost:8000/docs

**¡El sistema está listo para impresionar! 🚀**
