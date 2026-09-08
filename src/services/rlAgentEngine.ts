import { 
  ManagementZone, 
  RLDecision, 
  RLAgentObservationTensor, 
  XAIExplanation, 
  WeatherRadarCell, 
  SensorTelemetry 
} from '../types';
import { calculateCWSI, calculateEtc } from './digitalTwinEngine';

export interface RLRewardBreakdown {
  stressPenalty: number;
  waterConsumptionPenalty: number;
  overIrrigationPenalty: number;
  energyCostPenalty: number;
  totalReward: number;
}

/**
 * Builds the unified space-time state observation tensor for a management zone
 */
export function buildObservationTensor(
  zone: ManagementZone,
  radarCell?: WeatherRadarCell,
  weatherTelemetry?: SensorTelemetry
): RLAgentObservationTensor {
  const airTemp = weatherTelemetry?.readings?.ambientAirTempC ?? zone.ambientTemp;
  const rh = weatherTelemetry?.readings?.relativeHumidityPct ?? 45;
  const { cwsi, vpdKPa } = calculateCWSI(zone.currentCanopyTemp, airTemp, rh);
  
  const { etcMmDay } = calculateEtc(
    5.5,
    1.15,
    zone.currentMoisture10cm / 100,
    zone.fieldCapacity,
    zone.wiltingPoint
  );

  const forecastRain24h = radarCell?.forecast24hMm ?? 2.5;
  const radarEcho = radarCell?.dbzReflectivity ?? 15.0;

  // Depletion % = (FC - Current) / (FC - WP) * 100
  const taw = (zone.fieldCapacity - zone.wiltingPoint) * 100;
  const currentAvailable = zone.currentMoisture10cm - (zone.wiltingPoint * 100);
  const depletionPct = Math.max(0, Math.min(100, ((taw - currentAvailable) / taw) * 100));

  // Current hour tariff tier (off-peak 22h-06h: 1, mid 06h-18h: 2, peak 18h-22h: 3)
  const hour = new Date().getHours();
  let tariffTier = 2;
  if (hour >= 22 || hour < 6) tariffTier = 1;
  else if (hour >= 18 && hour < 22) tariffTier = 3;

  return {
    zoneId: zone.id,
    soilMoistureProfile: [zone.currentMoisture10cm, zone.currentMoisture30cm, zone.currentMoisture60cm],
    canopyTempKelvin: Number((zone.currentCanopyTemp + 273.15).toFixed(2)),
    ambientTempKelvin: Number((airTemp + 273.15).toFixed(2)),
    vaporPressureDeficitKPa: vpdKPa,
    cwsi: Number(cwsi.toFixed(3)),
    etcMmDay: etcMmDay,
    forecastRain24hMm: forecastRain24h,
    radarEchoIntensity: radarEcho,
    cropStageNormalized: 0.65, // Floración
    soilMoistureDepletionPct: Number(depletionPct.toFixed(1)),
    electricityTariffTier: tariffTier
  };
}

/**
 * Calculates composite RL Reward
 * R = - w_stress * Stress - w_water * AppliedVolume - w_drain * DeepLoss - w_energy * Cost
 */
export function computeRLReward(
  appliedMm: number,
  cwsiResult: number,
  overIrrigationMm: number,
  tariffTier: number
): RLRewardBreakdown {
  const w1_stress = 15.0;
  const w2_water = 0.45;
  const w3_over = 1.8;
  const w4_energy = 0.6;

  const stressPenalty = -w1_stress * Math.pow(cwsiResult, 1.8);
  const waterConsumptionPenalty = -w2_water * appliedMm;
  const overIrrigationPenalty = -w3_over * overIrrigationMm;
  const energyCostPenalty = -w4_energy * (appliedMm * tariffTier * 0.3);

  const totalReward = stressPenalty + waterConsumptionPenalty + overIrrigationPenalty + energyCostPenalty;

  return {
    stressPenalty: Number(stressPenalty.toFixed(2)),
    waterConsumptionPenalty: Number(waterConsumptionPenalty.toFixed(2)),
    overIrrigationPenalty: Number(overIrrigationPenalty.toFixed(2)),
    energyCostPenalty: Number(energyCostPenalty.toFixed(2)),
    totalReward: Number(totalReward.toFixed(2))
  };
}

/**
 * Evaluates Explainable AI (XAI) feature importance & Safe Mode bounds
 */
export function generateXAIExplanation(
  zone: ManagementZone,
  observation: RLAgentObservationTensor,
  recommendedMm: number,
  hasSensorAnomaly: boolean
): XAIExplanation {
  const shapValues = [
    {
      feature: `Estrés Térmico de Dosel (CWSI: ${observation.cwsi})`,
      impact: observation.cwsi > 0.45 ? +(observation.cwsi * 0.7) : -(0.3 * (1 - observation.cwsi)),
      description: observation.cwsi > 0.45 ? 'Elevado estrés hídrico detectado por termografía' : 'Sin estrés térmico notable'
    },
    {
      feature: `Agotamiento de Humedad (${observation.soilMoistureDepletionPct}%)`,
      impact: +(observation.soilMoistureDepletionPct * 0.008),
      description: `Zona ${zone.soilTexture.replace('_', ' ')} con déficit en horizonte radicular`
    },
    {
      feature: `Radar Lluvia 24h (${observation.forecastRain24hMm}mm)`,
      impact: -(observation.forecastRain24hMm * 0.05),
      description: 'Aporte pluviométrico previsto descontado del volumen neto'
    },
    {
      feature: `Demanda Evaporativa ETc (${observation.etcMmDay}mm/día)`,
      impact: +(observation.etcMmDay * 0.04),
      description: 'Reposición de la tasa transpiratoria en floración'
    }
  ];

  let safeModeTriggered = false;
  let safeModeReason: string | undefined = undefined;

  if (hasSensorAnomaly) {
    safeModeTriggered = true;
    safeModeReason = 'Anomalía de sensor detectada por Isolation Forest. Riego bloqueado a dosis de contingencia estándar.';
  } else if (observation.forecastRain24hMm > 25.0) {
    safeModeTriggered = true;
    safeModeReason = 'Alerta de tormenta severa por radar (>25mm). Riego suspendido preventivamente.';
  } else if (observation.cwsi > 0.85 && zone.currentMoisture10cm > zone.fieldCapacity * 100) {
    safeModeTriggered = true;
    safeModeReason = 'Conflicto termografía vs sensor capacitivo (Posible falla de sensor IRT o asfixia radicular).';
  }

  let reasoningText = `La política PPO calculó una tasa de ${recommendedMm}mm optimizando la ventana de infiltración Green-Ampt. `;
  if (recommendedMm > 6.0) {
    reasoningText += `Se priorizó abatir el estrés térmico en floración manteniendo el perfil por debajo del umbral de saturación.`;
  } else if (recommendedMm > 0) {
    reasoningText += `Dosis de mantenimiento para balancear la ETc diaria considerando la lluvia proyectada.`;
  } else {
    reasoningText += `Suelo con humedad adecuada; se preserva recurso hídrico y energía de bombeo.`;
  }

  return {
    zoneId: zone.id,
    dominantFeature: observation.cwsi > 0.45 ? 'Estrés Térmico del Dosel (CWSI)' : 'Balance de Humedad y Radar',
    shapValues: shapValues.map(s => ({ ...s, impact: Number(s.impact.toFixed(2)) })),
    reasoningText,
    safeModeTriggered,
    safeModeReason
  };
}

/**
 * PPO / SAC Policy Inference Engine (Simulated neural network forward pass)
 */
export function runRLPolicyInference(
  zone: ManagementZone,
  radarCell?: WeatherRadarCell,
  weatherTelemetry?: SensorTelemetry,
  hasSensorAnomaly: boolean = false
): RLDecision {
  const observation = buildObservationTensor(zone, radarCell, weatherTelemetry);
  
  // Policy network continuous action estimation (mm of irrigation)
  const taw = (zone.fieldCapacity - zone.wiltingPoint) * 100;
  const currentAvailable = zone.currentMoisture10cm - (zone.wiltingPoint * 100);
  const rawDeficitMm = Math.max(0, (zone.targetMoisture - zone.currentMoisture10cm) * 0.6 * 10);
  
  let baseActionMm = rawDeficitMm;
  
  // Adjust for CWSI canopy stress
  if (observation.cwsi > 0.5) {
    baseActionMm += (observation.cwsi - 0.4) * 6.0;
  }
  
  // Subtract forecast rain
  baseActionMm = Math.max(0, baseActionMm - (observation.forecastRain24hMm * 0.8));
  
  // Apply zone hydraulic efficiency
  baseActionMm = baseActionMm / zone.hydraulicEfficiency;
  
  let recommendedDepthMm = Number(Math.min(18.0, Math.max(0, baseActionMm)).toFixed(1));
  
  // If safe mode triggered, fallback
  if (hasSensorAnomaly) {
    recommendedDepthMm = 3.0; // Conservative baseline
  }

  const recommendedVolumeM3 = Number(((recommendedDepthMm / 1000) * (zone.areaHectares * 10000)).toFixed(0));
  const confidenceScore = Number((0.90 + Math.random() * 0.08 - (hasSensorAnomaly ? 0.35 : 0)).toFixed(2));
  
  const explanation = generateXAIExplanation(zone, observation, recommendedDepthMm, hasSensorAnomaly);
  const reward = computeRLReward(recommendedDepthMm, observation.cwsi, 0, observation.electricityTariffTier);

  return {
    id: `dec-${Date.now()}-${zone.id}`,
    fieldId: zone.fieldId,
    zoneId: zone.id,
    zoneName: zone.name,
    timestamp: new Date().toISOString(),
    policyId: 'PPO-VRI-DualReward-v4.2',
    recommendedVolumeM3,
    recommendedDepthMm,
    executionWindowHours: { start: '22:00', end: '04:00' },
    confidenceScore: Math.max(0.1, confidenceScore),
    status: 'pending',
    rewardExpected: reward.totalReward,
    explanation,
    overriddenManually: false
  };
}
