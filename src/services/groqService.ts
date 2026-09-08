import { 
  AgriculturalField, 
  ManagementZone, 
  RLDecision, 
  SensorTelemetry, 
  WeatherRadarCell 
} from '../types';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
}

const GROQ_API_ENDPOINT = 'https://api.groq.com/openai/v1/chat/completions';
const LOCAL_STORAGE_KEY = 'groq_api_key';
const LOCAL_STORAGE_MODEL_KEY = 'groq_selected_model';
const DEFAULT_GROQ_API_KEY = 'groq_api_key';

export const DEFAULT_MODEL = 'openai/gpt-oss-120b';

export const AVAILABLE_GROQ_MODELS = [
  { 
    id: 'openai/gpt-oss-120b', 
    name: 'GPT-OSS 120B (Recomendado)', 
    speed: 'Muy Rápido', 
    description: 'Modelo insignia de 120B con máxima precisión agronómica y razonamiento biofísico' 
  },
  { 
    id: 'qwen/qwen3.8-27b', 
    name: 'Qwen 3.8 27B', 
    speed: 'Ultra Rápido', 
    description: 'Alta velocidad y excelente comprensión de balances de humedad' 
  },
  { 
    id: 'openai/gpt-oss-20b', 
    name: 'GPT-OSS 20B Instant', 
    speed: 'Instantáneo', 
    description: 'Latencia mínima para consultas rápidas en campo' 
  },
  { 
    id: 'groq/compound', 
    name: 'Groq Compound', 
    speed: 'Rápido', 
    description: 'Sistema compuesto con herramientas integradas de Groq' 
  }
];

export function getStoredGroqApiKey(): string {
  const localKey = localStorage.getItem(LOCAL_STORAGE_KEY);

  if (localKey && localKey.trim().length > 0) {
    return localKey.trim();
  }

  const envKey = (import.meta as any).env?.VITE_GROQ_API_KEY;

  if (envKey && typeof envKey === 'string' && envKey.trim().length > 0) {
    return envKey.trim();
  }

  return '';
}

export function setStoredGroqApiKey(key: string): void {
  localStorage.setItem(LOCAL_STORAGE_KEY, key.trim());
}

export function clearStoredGroqApiKey(): void {
  localStorage.removeItem(LOCAL_STORAGE_KEY);
}

export function getStoredGroqModel(): string {
  const stored = localStorage.getItem(LOCAL_STORAGE_MODEL_KEY);
  const validIds = AVAILABLE_GROQ_MODELS.map(m => m.id);
  // Si el usuario tenía guardado un modelo que ya no existe (como llama-3.3-70b-versatile o mixtral), migrar a DEFAULT_MODEL
  if (stored && validIds.includes(stored)) {
    return stored;
  }
  localStorage.setItem(LOCAL_STORAGE_MODEL_KEY, DEFAULT_MODEL);
  return DEFAULT_MODEL;
}

export function setStoredGroqModel(model: string): void {
  localStorage.setItem(LOCAL_STORAGE_MODEL_KEY, model);
}

/**
 * Genera el System Prompt contextualizado con los datos vivos del Gemelo Digital
 */
export function buildAgronomicSystemPrompt(
  field: AgriculturalField,
  zones: ManagementZone[],
  decisions: RLDecision[],
  sensors: SensorTelemetry[],
  radarCells: WeatherRadarCell[]
): string {
  const avgCwsi = (zones.reduce((acc, z) => acc + z.cwsi, 0) / zones.length).toFixed(2);
  const totalWaterSaved = field.waterSavedM3Season.toLocaleString();
  const totalEnergySaved = field.energySavedKwhSeason.toLocaleString();
  
  const zonesSummary = zones.map(z => {
    return `- ${z.name}: Textura ${z.soilTexture}, Humedad 10cm: ${z.currentMoisture10cm}%, 30cm: ${z.currentMoisture30cm}%, Temp Dosel: ${z.currentCanopyTemp}°C, CWSI: ${z.cwsi} (${z.status}), Ksat: ${z.saturatedK} mm/h, Dosis recomendada RL: ${z.recommendedRateMm} mm.`;
  }).join('\n');

  const decisionsSummary = decisions.map(d => {
    return `- Decisión ${d.id} para ${d.zoneName}: Dosis ${d.recommendedDepthMm} mm (${d.recommendedVolumeM3} m³), Estado: ${d.status}, Confianza: ${(d.confidenceScore * 100).toFixed(0)}%, Factor dominante: ${d.explanation.dominantFeature}. Fundamento: "${d.explanation.reasoningText}"`;
  }).join('\n');

  const radarSummary = radarCells.map(r => {
    return `- Celda ${r.gridId}: Lluvia prevista 24h: ${r.forecast24hMm} mm (Reflectividad ${r.dbzReflectivity} dBZ).`;
  }).join('\n');

  return `Eres el "Asistente Agronómico de Inteligencia Artificial" del Gemelo Digital de Ciclo Cerrado para Riego Autónomo de Tasa Variable (VRI).
Tu objetivo es orientar a agrónomos, productores e ingenieros de campo sobre el estado biofísico del cultivo, el balance hídrico y las decisiones tomadas por el agente de Aprendizaje por Refuerzo (PPO-RL).

DATOS EN TIEMPO REAL DEL CAMPO:
• Campo: "${field.name}" (${field.totalAreaHa} Hectáreas)
• Cultivo: ${field.cropName} (${field.cropVariety})
• Etapa Fenológica: ${field.cropStage} (Kc: ${field.kcFactor}, Profundidad radicular: ${field.rootDepthMeters} m)
• Sistema de Riego: Pivot Central VRI (8 sectores, capacidad de bomba: ${field.pumpFlowCapacityM3h} m³/h)
• Ahorro Acumulado en Temporada: ${totalWaterSaved} m³ de agua (-28.4%) y ${totalEnergySaved} kWh de energía de bombeo.
• Estrés Térmico Promedio del Campo (CWSI): ${avgCwsi}

ESTADO DE LAS ZONAS DE MANEJO:
${zonesSummary}

DECISIONES DE RIEGO ACTIVAS DEL AGENTE RL (PPO):
${decisionsSummary}

PRONÓSTICO METEOROLÓGICO Y RADAR DOPPLER:
${radarSummary}

MODELOS FÍSICOS UTILIZADOS EN EL GEMELO DIGITAL:
1. Infiltración de Green-Ampt: f(t) = Ksat * [1 + (psi * DeltaTheta) / F(t)]
2. Estrés hídrico por termografía infrarroja (CWSI) basado en déficit de presión de vapor (VPD).
3. Balance de dos estratos FAO-56 (evaporación superficial 0-30cm y transpiración basal 30-60cm).
4. Ciclo Cerrado (Closed-Loop): Recalibración post-riego a 45-60 min comparando humedad simulada vs sensor TDR real para reajustar la conductividad saturada Ksat.

PAUTAS DE RESPUESTA:
- Responde SIEMPRE en español claro, profesional, agronómico y conciso.
- Justifica las respuestas con los datos reales del campo proporcionados arriba.
- Si te preguntan por qué se recomienda cierta dosis en una zona (por ejemplo Zona 4), explica el estrés térmico del dosel (CWSI), el tipo de suelo y el descuento de la lluvia prevista por radar.
- Cuando la respuesta sea leída en voz alta, procura oraciones fluidas, naturales y sin exceso de caracteres especiales o tablas complejas. Puedes usar viñetas y negritas cortas para facilitar la lectura visual.`;
}

/**
 * Envía una consulta a la API de Groq
 */
export async function queryGroqChat(
  messages: Array<{ role: 'user' | 'assistant' | 'system'; content: string }>,
  systemPrompt: string,
  apiKey: string,
  model: string = DEFAULT_MODEL
): Promise<string> {
  if (!apiKey || apiKey.trim().length === 0) {
    throw new Error('API_KEY_MISSING');
  }

  // Validar si el modelo está en la lista de modelos soportados, si no mapear a DEFAULT_MODEL
  const validIds = AVAILABLE_GROQ_MODELS.map(m => m.id);
  let targetModel = validIds.includes(model) ? model : DEFAULT_MODEL;

  const executeCall = async (modelToUse: string) => {
    const payload = {
      model: modelToUse,
      messages: [
        { role: 'system', content: systemPrompt },
        ...messages.slice(-8) // Enviar los últimos turnos para contexto conversacional
      ],
      temperature: 0.4,
      max_tokens: 800,
      top_p: 0.95
    };

    return fetch(GROQ_API_ENDPOINT, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey.trim()}`
      },
      body: JSON.stringify(payload)
    });
  };

  let response = await executeCall(targetModel);

  // Si el modelo específico retorna 404/400 (por ejemplo si fue deprecado en Groq o no se tiene acceso)
  // intentamos automáticamente fallback al modelo recomendado
  if (!response.ok && targetModel !== DEFAULT_MODEL) {
    const errClone = await response.clone().text();
    if (
      response.status === 404 ||
      response.status === 400 ||
      errClone.includes('does not exist') ||
      errClone.includes('decommissioned')
    ) {
      console.warn(`[GroqService] El modelo '${targetModel}' no está disponible. Realizando fallback automático a '${DEFAULT_MODEL}'...`);
      targetModel = DEFAULT_MODEL;
      setStoredGroqModel(DEFAULT_MODEL);
      response = await executeCall(DEFAULT_MODEL);
    }
  }

  if (!response.ok) {
    let errorDetail = `Error HTTP ${response.status}`;
    try {
      const errJson = await response.json();
      if (errJson?.error?.message) {
        errorDetail = errJson.error.message;
      }
    } catch {
      // Ignorar fallback
    }

    if (response.status === 401) {
      throw new Error('Clave API de Groq inválida o no autorizada. Por favor verifica tu clave.');
    }
    if (response.status === 429) {
      throw new Error('Límite de tasa o tokens excedido en Groq API. Intenta nuevamente en unos segundos.');
    }
    throw new Error(`Error en Groq API: ${errorDetail}`);
  }

  const data = await response.json();
  const botReply = data?.choices?.[0]?.message?.content;
  if (!botReply) {
    throw new Error('Respuesta vacía recibida desde Groq API.');
  }

  return botReply;
}

