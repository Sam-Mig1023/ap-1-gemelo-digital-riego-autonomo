# 📍 Dónde Ver el Calendario Fenológico en el Frontend

## 🎯 Ubicación Visual

El sistema de calendario fenológico aparece en **3 lugares** del frontend:

---

## 1️⃣ **Mapa GIS - Panel de Zona (AUTOMÁTICO)** ⭐

**Ubicación:** Pestaña "Mapa GIS" → Selecciona cualquier zona → Panel derecho

### ¿Qué se muestra?

✅ **Timeline del calendario** (línea de progreso)
```
Siembra: 2026-07-01  ━━━━●━━━━━━━━━━━━━━━━━  Cosecha: 2026-10-15
                     45%
                     ↓
                  Floración
```

✅ **Información del cultivo**
- 🌱 Nombre: Tomate
- 📊 Fase: Floración
- 📈 Kc: 1.15 (DINÁMICO)

✅ **Botón "Ver Análisis Fenológico AI 🤖"**
- Click para abrir modal con análisis completo

### Cómo acceder:
1. Abre: http://localhost:3000
2. Navega a: **"Mapa GIS"** (primera pestaña)
3. **Click en cualquier cuadrante** del mapa circular
4. **Panel derecho** mostrará:
   - Calendario automático (si hay datos)
   - Botón morado "Ver Análisis Fenológico AI 🤖"

---

## 2️⃣ **Modal AI con LangChain** 🤖

**Ubicación:** Click en botón "Ver Análisis Fenológico AI 🤖"

### ¿Qué se muestra?

```
╔═══════════════════════════════════════════════════════════╗
║              🌱 Análisis Fenológico AI                    ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  🍅 Tomate                            [🌸 Floración]     ║
║  Zona: zone-1-nw                                         ║
║                                                           ║
║  Progreso del ciclo: ▓▓▓▓▓▓░░░░░░░░░░ 42.5%            ║
║                                                           ║
║  📅 45 días     🎯 0 días     ⏰ 61 días                 ║
║     siembra        floración      cosecha                ║
║                                                           ║
║  💧 Coeficiente Kc: 1.15                                 ║
║     FAO-56 para etapa Floración                          ║
║                                                           ║
╠═══════════════════════════════════════════════════════════╣
║  🧠 Análisis del Agente AI  [LangChain ReAct]           ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  El cultivo de Tomate en zone-1-nw se encuentra en      ║
║  etapa de floración (45 días desde siembra). Esta es    ║
║  una etapa crítica donde el Kc alcanza su valor         ║
║  máximo de 1.15...                                       ║
║                                                           ║
║  [Razonamiento completo del agente]                     ║
║                                                           ║
╠═══════════════════════════════════════════════════════════╣
║  ✨ Recomendación de Riego AI  [Confianza: 88%]        ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  8.5 mm                                                  ║
║                                                           ║
║  Cálculo basado en FAO-56: ETc = Kc (1.15) × ET0 (5.5) ║
║                                                           ║
║  ⚠️ Factores de Riesgo:                                 ║
║    • Pronóstico de lluvia incierto                      ║
║                                                           ║
║  ✅ Tips de Optimización:                               ║
║    • Etapa Floración requiere monitoreo frecuente       ║
║    • Considerar aplicación fraccionada                  ║
║                                                           ║
║  [Actualizar Análisis AI]                               ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

### Características:
- 🎨 **Gradientes visuales** por etapa
- 🤖 **Razonamiento del agente** LangChain
- 💧 **Recomendación precisa** de riego
- ⚠️ **Factores de riesgo** identificados
- ✅ **Tips de optimización** agronómicos
- 🔄 **Botón de actualización** para nuevo análisis

---

## 3️⃣ **Consola del Navegador (Logs)** 🔍

**Ubicación:** Presiona F12 → Pestaña "Console"

### ¿Qué verás?

```javascript
[Phenology] Loading crop calendar data...
[Phenology] Updated zone-1-nw: Kc=1.15, Stage=Floración
[Phenology] Updated zone-2-ne: Kc=1.15, Stage=Floración
[Phenology] Updated zone-4: Kc=0.95, Stage=Floración
[Phenology] Updated zone-5: Kc=1.05, Stage=Formación
[Phenology] ✓ Crop calendar loaded successfully
```

Esto confirma que el sistema está:
- ✅ Cargando datos del backend
- ✅ Actualizando Kc dinámicamente
- ✅ Integrando con el Digital Twin Engine

---

## 📸 Guía Visual Paso a Paso

### Paso 1: Abrir el Mapa GIS
```
http://localhost:3000
↓
[Mapa GIS] ← Click aquí (primera pestaña)
```

### Paso 2: Seleccionar una Zona
```
     ╔════════════════╗
     ║    Zone NW     ║ ← Click aquí
     ║   Tomate 🍅    ║
     ║   H: 22%       ║
     ╚════════════════╝
```

### Paso 3: Ver el Panel Derecho
```
┌────────────────────────────────────┐
│  Zone 1 - Northwest                │
│  🌱 Tomate | Fase: Floración       │
│  Kc: 1.15                          │
│                                    │
│  📅 Calendario                     │
│  Siembra ━━●━━━━━━ Cosecha        │
│          45%                       │
│          Floración ↑               │
│                                    │
│  💧 Humedad del suelo              │
│  [████████░░] 22%                 │
│                                    │
│  ✨ Recomendación RL: 7.8 mm      │
│  [Aplicar Dosis]                   │
│                                    │
│  🤖 [Ver Análisis Fenológico AI]  │ ← Click aquí
└────────────────────────────────────┘
```

### Paso 4: Ver el Modal AI
```
  ┌─────────────────────────────────────┐
  │    MODAL FLOTANTE (grande)          │
  │                                     │
  │  🌱 Análisis Fenológico AI          │
  │  [X cerrar]                         │
  │                                     │
  │  [Todo el análisis completo]        │
  │                                     │
  └─────────────────────────────────────┘
```

---

## 🚀 Verificación Rápida

### ¿El sistema está funcionando?

Checklist:
- [ ] Backend corriendo en http://localhost:8000
- [ ] Frontend corriendo en http://localhost:3000
- [ ] Console del navegador (F12) muestra logs de `[Phenology]`
- [ ] Panel derecho del mapa muestra "🌱 Tomate | Fase: Floración"
- [ ] Aparece el botón morado "Ver Análisis Fenológico AI 🤖"
- [ ] Timeline del calendario visible con barra de progreso

### ¿No aparece nada?

**Posibles causas:**

1. **Backend no está corriendo**
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload
   ```

2. **CSV no tiene datos**
   - Verifica: `backend/data/crop_calendar.csv`
   - Debe tener al menos una fila con `zone-1-nw`

3. **Error en la API**
   - Abre: http://localhost:8000/api/v1/crop-calendar/calendar
   - Deberías ver JSON con datos fenológicos

4. **Error en frontend**
   - F12 → Console
   - Busca errores en rojo
   - Común: "Failed to fetch" = backend no está corriendo

---

## 🎨 Aspecto Visual

### Colores por Etapa Fenológica:

- 🟡 **Inicial** - Amarillo (Kc: 0.5-0.6)
- 🟢 **Vegetativo** - Verde (Kc: 0.7-0.9)
- 🌸 **Floración** - Rosa (Kc: 0.95-1.15)
- 🟠 **Formación** - Naranja (Kc: 0.9-1.20)
- 🔴 **Maduración** - Rojo (Kc: 0.7-0.85)

### Iconos:
- 🌱 Germinación/Inicial
- 🌿 Vegetativo
- 🌸 Floración
- 🍅 Formación de frutos
- 🔴 Maduración

---

## 💡 Tips Finales

### Para impresionar en una demostración:

1. **Selecciona diferentes zonas** → Cada una muestra cultivos diferentes
2. **Click en "Ver Análisis AI"** → Muestra el poder de LangChain
3. **Explica el Kc dinámico** → "Ahora se ajusta automáticamente según etapa"
4. **Muestra el razonamiento** → "El agente explica por qué recomienda X mm"
5. **Refresca el análisis** → Botón "Actualizar Análisis AI"

### Puntos clave a mencionar:
- ✅ **Kc dinámico** reemplaza valores fijos
- ✅ **Agente LangChain** con ReAct pattern
- ✅ **5 herramientas** especializadas
- ✅ **RAG integration** con conocimiento agronómico
- ✅ **Recomendaciones explicables** (XAI)

---

## 📞 Ayuda Rápida

**No veo el botón AI:**
→ La zona debe tener `cropName` (verificar que los datos se cargaron)

**El modal no se abre:**
→ Verificar consola de errores (F12), puede ser GROQ_API_KEY no configurada

**El análisis es lento:**
→ Normal, el agente ReAct hace múltiples llamadas al LLM (10-30 seg)

**No aparece el timeline:**
→ Verificar que `zone.plantingDate`, `floweringDate`, `harvestDate` existen

---

**¡Disfruta tu calendario fenológico con IA! 🚀🌱**
