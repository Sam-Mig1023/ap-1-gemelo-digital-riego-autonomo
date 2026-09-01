import { SensorTelemetry } from '../types';

export interface AnomalyDetectionResult {
  sensorId: string;
  isAnomaly: boolean;
  anomalyScore: number; // 0 (normal) to 1.0 (highly anomalous)
  anomalyType?: 'frozen_values' | 'drift_out_of_bounds' | 'rate_of_change_spike' | 'battery_critical';
  details: string;
}

/**
 * Evaluates telemetry streams against statistical limits and Isolation Forest proxy logic
 */
export function evaluateSensorAnomalies(
  currentSensor: SensorTelemetry,
  historicalReadings: number[] = []
): AnomalyDetectionResult {
  const readings = currentSensor.readings;
  let isAnomaly = false;
  let anomalyScore = 0.05;
  let anomalyType: AnomalyDetectionResult['anomalyType'] = undefined;
  let details = 'Sensor operando dentro de los parámetros estocásticos normales.';

  // 1. Check for physical bounds
  if (readings.volumetricWaterContent_10cm !== undefined) {
    const vwc = readings.volumetricWaterContent_10cm;
    if (vwc < 2.0 || vwc > 58.0) {
      isAnomaly = true;
      anomalyScore = 0.95;
      anomalyType = 'drift_out_of_bounds';
      details = `Lectura de humedad (${vwc}%) excede los límites físicos del suelo mineral (2% - 58%).`;
    }
  }

  // 2. Check for Canopy Temp bounds
  if (readings.canopyTemperatureC !== undefined) {
    const ct = readings.canopyTemperatureC;
    if (ct < 5.0 || ct > 55.0) {
      isAnomaly = true;
      anomalyScore = 0.92;
      anomalyType = 'drift_out_of_bounds';
      details = `Temperatura de dosel IRT (${ct}°C) fuera de rango biológico admisible.`;
    }
  }

  // 3. Check for frozen values across history
  if (historicalReadings.length >= 5) {
    const variance = historicalReadings.reduce((acc, val) => acc + Math.pow(val - historicalReadings[0], 2), 0) / historicalReadings.length;
    if (variance < 0.0001) {
      isAnomaly = true;
      anomalyScore = 0.88;
      anomalyType = 'frozen_values';
      details = 'Sensor estancado (lecturas idénticas por > 5 ciclos continuos). Sospecha de falla de transductor.';
    }
  }

  // 4. Low battery check
  if (currentSensor.batteryLevel < 12) {
    isAnomaly = true;
    anomalyScore = 0.78;
    anomalyType = 'battery_critical';
    details = `Batería crítica (${currentSensor.batteryLevel}%). Señal analógica propensa a ruido por baja tensión.`;
  }

  return {
    sensorId: currentSensor.sensorId,
    isAnomaly,
    anomalyScore: Number(anomalyScore.toFixed(2)),
    anomalyType,
    details
  };
}
