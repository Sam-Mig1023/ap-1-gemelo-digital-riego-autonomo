// Domain Types for Closed-Loop Digital Twin for Autonomous Variable-Rate Irrigation (VRI)

export type SoilTextureType = 'sandy_loam' | 'silt_loam' | 'clay_loam' | 'loam' | 'sandy_clay';

export type CropStage = 'initial' | 'vegetative' | 'flowering' | 'yield_formation' | 'ripening';

export type SystemOperationMode = 'manual' | 'assisted' | 'autonomous';

export type DecisionStatus = 'pending' | 'approved' | 'executed' | 'failed' | 'reverted' | 'feedback_verified';

export type UserRole = 'superadmin' | 'agronomist' | 'farmer' | 'field_technician' | 'rl_agent_system';

export type SensorType = 'soil_moisture_multi' | 'canopy_temperature_irt' | 'weather_station' | 'flow_meter';

export interface GeoPolygon {
  type: 'Polygon';
  coordinates: number[][][]; // [ [ [lng, lat], ... ] ]
}

export interface ManagementZone {
  id: string;
  name: string;
  fieldId: string;
  polygon: GeoPolygon;
  areaHectares: number;
  soilTexture: SoilTextureType;
  fieldCapacity: number; // m3/m3 (e.g. 0.32)
  wiltingPoint: number;  // m3/m3 (e.g. 0.14)
  saturatedK: number;     // mm/h hydraulic conductivity (Green-Ampt)
  suctionHead: number;    // mm matric suction head
  currentMoisture10cm: number; // % or m3/m3
  currentMoisture30cm: number;
  currentMoisture60cm: number;
  currentCanopyTemp: number;   // °C
  ambientTemp: number;         // °C
  cwsi: number;                // Crop Water Stress Index [0..1]
  targetMoisture: number;      // %
  recommendedRateMm: number;   // Recommended mm
  appliedRateMm: number;       // Last applied mm
  hydraulicEfficiency: number; // e.g. 0.88 (88%)
  status: 'optimal' | 'mild_stress' | 'severe_stress' | 'over_irrigated';
}

export interface AgriculturalField {
  id: string;
  tenantId: string;
  name: string;
  boundary: GeoPolygon;
  totalAreaHa: number;
  cropName: string;
  cropVariety: string;
  plantingDate: string;
  cropStage: CropStage;
  rootDepthMeters: number;
  kcFactor: number; // Crop coefficient FAO-56
  irrigationSystemType: 'center_pivot_vri' | 'linear_move_vri' | 'drip_dosing_zones';
  numberOfSectors: number;
  pumpFlowCapacityM3h: number;
  currentStressIndex: number;
  waterSavedM3Season: number;
  energySavedKwhSeason: number;
  zones: ManagementZone[];
}

export interface SensorTelemetry {
  id: string;
  sensorId: string;
  zoneId: string;
  timestamp: string;
  sensorType: SensorType;
  location: { lat: number; lng: number };
  status: 'online' | 'offline' | 'warning' | 'anomaly';
  batteryLevel: number;
  rssi: number;
  readings: {
    volumetricWaterContent_10cm?: number; // m3/m3
    volumetricWaterContent_30cm?: number; // m3/m3
    volumetricWaterContent_60cm?: number; // m3/m3
    canopyTemperatureC?: number;          // °C from IRT
    ambientAirTempC?: number;
    relativeHumidityPct?: number;
    solarRadiationWm2?: number;
    windSpeedMs?: number;
    soilTempC?: number;
    flowRateLps?: number;
  };
  anomalyFlag?: boolean;
  anomalyScore?: number; // from Isolation Forest [0..1]
  qualityScore: number;  // [0..100]
}

export interface WeatherRadarCell {
  gridId: string;
  lat: number;
  lng: number;
  dbzReflectivity: number; // 0 - 65 dBZ
  rainRateMmHour: number;
  confidenceScore: number;
  forecast1hMm: number;
  forecast3hMm: number;
  forecast6hMm: number;
  forecast24hMm: number;
  radarTimestamp: string;
}

export interface RLAgentObservationTensor {
  zoneId: string;
  soilMoistureProfile: [number, number, number]; // [10cm, 30cm, 60cm]
  canopyTempKelvin: number;
  ambientTempKelvin: number;
  vaporPressureDeficitKPa: number;
  cwsi: number;
  etcMmDay: number;
  forecastRain24hMm: number;
  radarEchoIntensity: number;
  cropStageNormalized: number;
  soilMoistureDepletionPct: number;
  electricityTariffTier: number; // 1: off-peak, 2: mid, 3: peak
}

export interface XAIExplanation {
  zoneId: string;
  dominantFeature: string;
  shapValues: {
    feature: string;
    impact: number; // positive = increased irrigation, negative = decreased
    description: string;
  }[];
  reasoningText: string;
  safeModeTriggered: boolean;
  safeModeReason?: string;
}

export interface RLDecision {
  id: string;
  fieldId: string;
  zoneId: string;
  zoneName: string;
  timestamp: string;
  policyId: string;
  recommendedVolumeM3: number;
  recommendedDepthMm: number;
  executionWindowHours: { start: string; end: string };
  confidenceScore: number; // [0..1]
  status: DecisionStatus;
  approvedBy?: string;
  approvalTimestamp?: string;
  executedTimestamp?: string;
  rewardExpected: number;
  rewardRealized?: number;
  explanation: XAIExplanation;
  overriddenManually: boolean;
  overrideReason?: string;
}

export interface ClosedLoopFeedback {
  decisionId: string;
  zoneId: string;
  timestampPostIrrigation: string; // 45 min after
  expectedMoisturePost: number;
  measuredMoisturePost: number;
  residualError: number;
  infiltrationEfficiency: number;
  modelRecalibrated: boolean;
  ksatAdjustmentPct: number;
  rewardFeedback: number;
}

export interface DigitalTwinSnapshot {
  timestamp: string;
  fieldId: string;
  realAverageMoisture: number;
  simulatedAverageMoisture: number;
  realCanopyTemp: number;
  simulatedCanopyTemp: number;
  currentEt0: number;
  currentEtc: number;
  projectedStressRisk: number;
  accumulatedReward: number;
}

export interface UserProfile {
  id: string;
  email: string;
  fullName: string;
  role: UserRole;
  tenantName: string;
  phone: string;
  assignedFieldIds: string[];
  mfaEnabled: boolean;
  preferredUnits: 'metric' | 'imperial';
}

export interface AuditLogEntry {
  id: string;
  timestamp: string;
  userId: string;
  userEmail: string;
  userRole: UserRole;
  action: string;
  resource: string;
  details: string;
  clientIp: string;
  sha256Signature: string;
}

export interface WhatIfScenarioInput {
  targetZoneId: string;
  irrigationActionMm: number;
  forecastRainFactor: number; // 0.0 to 2.0
  heatWaveScenarioDegC: number; // +0 to +8 C
  horizonDays: number;
}

export interface WhatIfScenarioResult {
  dayIndex: number;
  date: string;
  moistureTopLayer: number;
  moistureDeepLayer: number;
  cwsi: number;
  etcMm: number;
  drainageLossMm: number;
  cropStressLevel: 'none' | 'moderate' | 'severe';
  estimatedYieldImpactPct: number;
}

export interface ScheduledReport {
  id: string;
  title: string;
  format: 'pdf' | 'docx' | 'xlsx' | 'csv';
  frequency: 'daily' | 'weekly' | 'monthly' | 'on_demand';
  recipients: string[];
  lastGenerated: string;
  status: 'active' | 'paused';
}

export interface OfflineQueueItem {
  id: string;
  actionType: 'approve_irrigation' | 'manual_override' | 'sensor_calibration' | 'field_config';
  payload: any;
  queuedAt: string;
  synced: boolean;
}
