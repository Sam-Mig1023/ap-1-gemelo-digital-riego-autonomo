import { 
  AgriculturalField, 
  ManagementZone, 
  SensorTelemetry, 
  WeatherRadarCell, 
  RLDecision, 
  UserProfile, 
  AuditLogEntry, 
  DigitalTwinSnapshot,
  ScheduledReport
} from '../types';

export const INITIAL_ZONES: ManagementZone[] = [
  {
    id: 'zone-1-nw',
    name: 'Zona 1 (Noroeste - Arenosa)',
    fieldId: 'field-ica-01',
    polygon: {
      type: 'Polygon',
      coordinates: [[
        [-75.7360, -14.0620],
        [-75.7310, -14.0620],
        [-75.7310, -14.0670],
        [-75.7360, -14.0670],
        [-75.7360, -14.0620]
      ]]
    },
    areaHectares: 24.5,
    soilTexture: 'sandy_loam',
    fieldCapacity: 0.22, // 22% vol
    wiltingPoint: 0.09,  // 9% vol
    saturatedK: 28.5,    // mm/hr fast infiltration
    suctionHead: 110.1,  // mm
    currentMoisture10cm: 14.8,
    currentMoisture30cm: 16.2,
    currentMoisture60cm: 18.0,
    currentCanopyTemp: 29.8,
    ambientTemp: 26.4,
    cwsi: 0.58, // Mild stress
    targetMoisture: 20.0,
    recommendedRateMm: 8.4,
    appliedRateMm: 0.0,
    hydraulicEfficiency: 0.89,
    status: 'mild_stress'
  },
  {
    id: 'zone-2-ne',
    name: 'Zona 2 (Noreste - Franco Limosa)',
    fieldId: 'field-ica-01',
    polygon: {
      type: 'Polygon',
      coordinates: [[
        [-75.7310, -14.0620],
        [-75.7260, -14.0620],
        [-75.7260, -14.0670],
        [-75.7310, -14.0670],
        [-75.7310, -14.0620]
      ]]
    },
    areaHectares: 28.0,
    soilTexture: 'silt_loam',
    fieldCapacity: 0.31,
    wiltingPoint: 0.13,
    saturatedK: 12.2,
    suctionHead: 166.8,
    currentMoisture10cm: 25.4,
    currentMoisture30cm: 26.8,
    currentMoisture60cm: 27.2,
    currentCanopyTemp: 24.2,
    ambientTemp: 26.4,
    cwsi: 0.18, // Optimal
    targetMoisture: 27.0,
    recommendedRateMm: 2.1,
    appliedRateMm: 3.5,
    hydraulicEfficiency: 0.92,
    status: 'optimal'
  },
  {
    id: 'zone-3-sw',
    name: 'Zona 3 (Suroeste - Franco Arcillosa)',
    fieldId: 'field-ica-01',
    polygon: {
      type: 'Polygon',
      coordinates: [[
        [-75.7360, -14.0670],
        [-75.7310, -14.0670],
        [-75.7310, -14.0720],
        [-75.7360, -14.0720],
        [-75.7360, -14.0670]
      ]]
    },
    areaHectares: 32.5,
    soilTexture: 'clay_loam',
    fieldCapacity: 0.36,
    wiltingPoint: 0.18,
    saturatedK: 6.8,
    suctionHead: 208.8,
    currentMoisture10cm: 31.0,
    currentMoisture30cm: 32.5,
    currentMoisture60cm: 34.0,
    currentCanopyTemp: 23.5,
    ambientTemp: 26.4,
    cwsi: 0.12,
    targetMoisture: 32.0,
    recommendedRateMm: 0.0,
    appliedRateMm: 0.0,
    hydraulicEfficiency: 0.86,
    status: 'optimal'
  },
  {
    id: 'zone-4-se',
    name: 'Zona 4 (Sureste - Franco Arenosa Elevada)',
    fieldId: 'field-ica-01',
    polygon: {
      type: 'Polygon',
      coordinates: [[
        [-75.7310, -14.0670],
        [-75.7260, -14.0670],
        [-75.7260, -14.0720],
        [-75.7310, -14.0720],
        [-75.7310, -14.0670]
      ]]
    },
    areaHectares: 25.0,
    soilTexture: 'sandy_loam',
    fieldCapacity: 0.23,
    wiltingPoint: 0.10,
    saturatedK: 24.0,
    suctionHead: 122.0,
    currentMoisture10cm: 12.1,
    currentMoisture30cm: 13.5,
    currentMoisture60cm: 15.2,
    currentCanopyTemp: 31.2,
    ambientTemp: 26.4,
    cwsi: 0.72, // Severe Stress
    targetMoisture: 21.0,
    recommendedRateMm: 11.5,
    appliedRateMm: 0.0,
    hydraulicEfficiency: 0.90,
    status: 'severe_stress'
  }
];

export const INITIAL_FIELD: AgriculturalField = {
  id: 'field-ica-01',
  tenantId: 'agro-corp-latam',
  name: 'Campo San Jerónimo - Pivot Central VRI #04',
  boundary: {
    type: 'Polygon',
    coordinates: [[
      [-75.7365, -14.0615],
      [-75.7255, -14.0615],
      [-75.7255, -14.0725],
      [-75.7365, -14.0725],
      [-75.7365, -14.0615]
    ]]
  },
  totalAreaHa: 110.0,
  cropName: 'Maíz de Alto Rendimiento (Zea mays L.)',
  cropVariety: 'Pioneer P30F53HR (Grano Húmedo)',
  plantingDate: '2026-06-15',
  cropStage: 'flowering',
  rootDepthMeters: 0.85,
  kcFactor: 1.15, // Peak flowering Kc
  irrigationSystemType: 'center_pivot_vri',
  numberOfSectors: 8,
  pumpFlowCapacityM3h: 360,
  currentStressIndex: 0.38,
  waterSavedM3Season: 42850,
  energySavedKwhSeason: 28900,
  zones: INITIAL_ZONES
};

export const INITIAL_SENSORS: SensorTelemetry[] = [
  {
    id: 'sn-01',
    sensorId: 'SEN-SOIL-NW01',
    zoneId: 'zone-1-nw',
    timestamp: new Date().toISOString(),
    sensorType: 'soil_moisture_multi',
    location: { lat: -14.0645, lng: -75.7335 },
    status: 'online',
    batteryLevel: 94,
    rssi: -68,
    readings: {
      volumetricWaterContent_10cm: 14.8,
      volumetricWaterContent_30cm: 16.2,
      volumetricWaterContent_60cm: 18.0,
      soilTempC: 22.4
    },
    qualityScore: 98
  },
  {
    id: 'sn-02',
    sensorId: 'SEN-IRT-NW02',
    zoneId: 'zone-1-nw',
    timestamp: new Date().toISOString(),
    sensorType: 'canopy_temperature_irt',
    location: { lat: -14.0640, lng: -75.7340 },
    status: 'online',
    batteryLevel: 89,
    rssi: -71,
    readings: {
      canopyTemperatureC: 29.8,
      ambientAirTempC: 26.4,
      relativeHumidityPct: 42
    },
    qualityScore: 96
  },
  {
    id: 'sn-03',
    sensorId: 'SEN-SOIL-NE01',
    zoneId: 'zone-2-ne',
    timestamp: new Date().toISOString(),
    sensorType: 'soil_moisture_multi',
    location: { lat: -14.0645, lng: -75.7285 },
    status: 'online',
    batteryLevel: 97,
    rssi: -62,
    readings: {
      volumetricWaterContent_10cm: 25.4,
      volumetricWaterContent_30cm: 26.8,
      volumetricWaterContent_60cm: 27.2,
      soilTempC: 21.0
    },
    qualityScore: 99
  },
  {
    id: 'sn-04',
    sensorId: 'SEN-SOIL-SW01',
    zoneId: 'zone-3-sw',
    timestamp: new Date().toISOString(),
    sensorType: 'soil_moisture_multi',
    location: { lat: -14.0695, lng: -75.7335 },
    status: 'online',
    batteryLevel: 82,
    rssi: -74,
    readings: {
      volumetricWaterContent_10cm: 31.0,
      volumetricWaterContent_30cm: 32.5,
      volumetricWaterContent_60cm: 34.0,
      soilTempC: 20.8
    },
    qualityScore: 95
  },
  {
    id: 'sn-05',
    sensorId: 'SEN-SOIL-SE01',
    zoneId: 'zone-4-se',
    timestamp: new Date().toISOString(),
    sensorType: 'soil_moisture_multi',
    location: { lat: -14.0695, lng: -75.7285 },
    status: 'online',
    batteryLevel: 91,
    rssi: -65,
    readings: {
      volumetricWaterContent_10cm: 12.1,
      volumetricWaterContent_30cm: 13.5,
      volumetricWaterContent_60cm: 15.2,
      soilTempC: 23.6
    },
    qualityScore: 97
  },
  {
    id: 'sn-06',
    sensorId: 'SEN-IRT-SE02',
    zoneId: 'zone-4-se',
    timestamp: new Date().toISOString(),
    sensorType: 'canopy_temperature_irt',
    location: { lat: -14.0690, lng: -75.7280 },
    status: 'online',
    batteryLevel: 88,
    rssi: -69,
    readings: {
      canopyTemperatureC: 31.2,
      ambientAirTempC: 26.4,
      relativeHumidityPct: 40
    },
    qualityScore: 94
  },
  {
    id: 'sn-07',
    sensorId: 'MET-AGRO-TOWER',
    zoneId: 'zone-1-nw',
    timestamp: new Date().toISOString(),
    sensorType: 'weather_station',
    location: { lat: -14.0670, lng: -75.7310 },
    status: 'online',
    batteryLevel: 100,
    rssi: -55,
    readings: {
      ambientAirTempC: 26.4,
      relativeHumidityPct: 43,
      solarRadiationWm2: 840,
      windSpeedMs: 3.2
    },
    qualityScore: 100
  }
];

export const INITIAL_RADAR_GRID: WeatherRadarCell[] = [
  {
    gridId: 'RAD-01-NW',
    lat: -14.0620,
    lng: -75.7360,
    dbzReflectivity: 18.5,
    rainRateMmHour: 0.2,
    confidenceScore: 0.88,
    forecast1hMm: 0.1,
    forecast3hMm: 0.4,
    forecast6hMm: 1.2,
    forecast24hMm: 3.5,
    radarTimestamp: new Date().toISOString()
  },
  {
    gridId: 'RAD-02-NE',
    lat: -14.0620,
    lng: -75.7260,
    dbzReflectivity: 22.0,
    rainRateMmHour: 0.6,
    confidenceScore: 0.85,
    forecast1hMm: 0.3,
    forecast3hMm: 0.8,
    forecast6hMm: 2.1,
    forecast24hMm: 4.8,
    radarTimestamp: new Date().toISOString()
  },
  {
    gridId: 'RAD-03-SW',
    lat: -14.0720,
    lng: -75.7360,
    dbzReflectivity: 14.0,
    rainRateMmHour: 0.0,
    confidenceScore: 0.92,
    forecast1hMm: 0.0,
    forecast3hMm: 0.2,
    forecast6hMm: 0.6,
    forecast24hMm: 2.0,
    radarTimestamp: new Date().toISOString()
  },
  {
    gridId: 'RAD-04-SE',
    lat: -14.0720,
    lng: -75.7260,
    dbzReflectivity: 19.5,
    rainRateMmHour: 0.3,
    confidenceScore: 0.89,
    forecast1hMm: 0.2,
    forecast3hMm: 0.5,
    forecast6hMm: 1.4,
    forecast24hMm: 3.2,
    radarTimestamp: new Date().toISOString()
  }
];

export const INITIAL_RL_DECISIONS: RLDecision[] = [
  {
    id: 'dec-20260831-01',
    fieldId: 'field-ica-01',
    zoneId: 'zone-4-se',
    zoneName: 'Zona 4 (Sureste - Franco Arenosa Elevada)',
    timestamp: new Date(Date.now() - 35 * 60 * 1000).toISOString(),
    policyId: 'PPO-VRI-DualReward-v4.2',
    recommendedVolumeM3: 2875,
    recommendedDepthMm: 11.5,
    executionWindowHours: { start: '22:00', end: '04:00' },
    confidenceScore: 0.94,
    status: 'approved',
    approvedBy: 'agronomo.senior@agricola.pe',
    approvalTimestamp: new Date(Date.now() - 25 * 60 * 1000).toISOString(),
    rewardExpected: 14.8,
    explanation: {
      zoneId: 'zone-4-se',
      dominantFeature: 'Estrés Térmico de Dosel (CWSI: 0.72)',
      shapValues: [
        { feature: 'Temp Dosel (+4.8°C vs Ambiente)', impact: +0.48, description: 'Cierre estomático agudo detectado por termografía' },
        { feature: 'Humedad 10-30cm (12.1% m3/m3)', impact: +0.36, description: 'Por debajo del 50% de agua disponible (PMP: 10%)' },
        { feature: 'Radar Precipitación 24h (3.2mm)', impact: -0.12, description: 'Lluvia leve no cubre déficit diario de ETc (6.8mm)' },
        { feature: 'Tarifa Eléctrica Valle', impact: +0.08, description: 'Horario nocturno optimiza costo de bombeo en 42%' }
      ],
      reasoningText: 'El modelo PPO identifica un déficit severo con alto riesgo de pérdida de biomasa en fase de floración. La tasa de 11.5mm restaurará la humedad al 85% de Capacidad de Campo sin generar percolación profunda.',
      safeModeTriggered: false
    },
    overriddenManually: false
  },
  {
    id: 'dec-20260831-02',
    fieldId: 'field-ica-01',
    zoneId: 'zone-1-nw',
    zoneName: 'Zona 1 (Noroeste - Arenosa)',
    timestamp: new Date(Date.now() - 35 * 60 * 1000).toISOString(),
    policyId: 'PPO-VRI-DualReward-v4.2',
    recommendedVolumeM3: 2058,
    recommendedDepthMm: 8.4,
    executionWindowHours: { start: '23:30', end: '05:30' },
    confidenceScore: 0.91,
    status: 'pending',
    rewardExpected: 11.2,
    explanation: {
      zoneId: 'zone-1-nw',
      dominantFeature: 'Alta Infiltración Arenosa + Estrés Térmico Moderado',
      shapValues: [
        { feature: 'Déficit de Humedad Radicular (16.2%)', impact: +0.42, description: 'Suelo arenoso pierde retención rápidamente' },
        { feature: 'CWSI Moderado (0.58)', impact: +0.31, description: 'Comienzo de estrés hídrico diurno' },
        { feature: 'Precipitación Radar Prevista (3.5mm)', impact: -0.15, description: 'Descontada del requerimiento neto bruto' }
      ],
      reasoningText: 'Riego fraccionado preventivo para mantener la conductividad hidráulica y evitar estrés hídrico durante la fecundación.',
      safeModeTriggered: false
    },
    overriddenManually: false
  },
  {
    id: 'dec-20260831-03',
    fieldId: 'field-ica-01',
    zoneId: 'zone-2-ne',
    zoneName: 'Zona 2 (Noreste - Franco Limosa)',
    timestamp: new Date(Date.now() - 90 * 60 * 1000).toISOString(),
    policyId: 'PPO-VRI-DualReward-v4.2',
    recommendedVolumeM3: 588,
    recommendedDepthMm: 2.1,
    executionWindowHours: { start: '18:00', end: '20:00' },
    confidenceScore: 0.96,
    status: 'feedback_verified',
    approvedBy: 'Sistema RL Autónomo',
    approvalTimestamp: new Date(Date.now() - 85 * 60 * 1000).toISOString(),
    executedTimestamp: new Date(Date.now() - 75 * 60 * 1000).toISOString(),
    rewardExpected: 8.5,
    rewardRealized: 8.8,
    explanation: {
      zoneId: 'zone-2-ne',
      dominantFeature: 'Estado Hídrico Óptimo - Micro-ajuste de reposición',
      shapValues: [
        { feature: 'Humedad en Rango Óptimo (25.4%)', impact: -0.35, description: 'Cercano a Capacidad de Campo (31%)' },
        { feature: 'Radar Lluvia Prevista (4.8mm)', impact: -0.25, description: 'Lluvia entrante complementará requerimiento' }
      ],
      reasoningText: 'Dosis mínima para compensar ETc diaria sin saturar horizontes arcillo-limosos.',
      safeModeTriggered: false
    },
    overriddenManually: false
  }
];

export const INITIAL_USERS: UserProfile[] = [
  {
    id: 'usr-001',
    email: 'admin.global@agrotech.ai',
    fullName: 'Dr. Alejandro Morales',
    role: 'superadmin',
    tenantName: 'AgroPrecision Global Holding',
    phone: '+51 987 654 321',
    assignedFieldIds: ['field-ica-01', 'field-majes-02'],
    mfaEnabled: true,
    preferredUnits: 'metric'
  },
  {
    id: 'usr-002',
    email: 'agronomo.senior@agricola.pe',
    fullName: 'Ing. Valeria Domínguez',
    role: 'agronomist',
    tenantName: 'AgroPrecision Global Holding',
    phone: '+51 976 543 210',
    assignedFieldIds: ['field-ica-01'],
    mfaEnabled: true,
    preferredUnits: 'metric'
  },
  {
    id: 'usr-003',
    email: 'productor.campo@sanpablo.com',
    fullName: 'Carlos Mendoza Ramos',
    role: 'farmer',
    tenantName: 'Fundo San Jerónimo SAC',
    phone: '+51 965 432 109',
    assignedFieldIds: ['field-ica-01'],
    mfaEnabled: false,
    preferredUnits: 'metric'
  },
  {
    id: 'usr-004',
    email: 'tecnico.iot@sensoresica.com',
    fullName: 'David Quispe Huamán',
    role: 'field_technician',
    tenantName: 'IoT Agro Services Peru',
    phone: '+51 954 321 098',
    assignedFieldIds: ['field-ica-01'],
    mfaEnabled: false,
    preferredUnits: 'metric'
  }
];

export const INITIAL_AUDIT_LOGS: AuditLogEntry[] = [
  {
    id: 'aud-001',
    timestamp: new Date(Date.now() - 25 * 60 * 1000).toISOString(),
    userId: 'usr-002',
    userEmail: 'agronomo.senior@agricola.pe',
    userRole: 'agronomist',
    action: 'APPROVE_IRRIGATION_DECISION',
    resource: 'RLDecision/dec-20260831-01 (Zona 4 - 11.5mm)',
    details: 'Aprobación confirmada tras verificar curva de estrés CWSI 0.72 y ventana eléctrica nocturna.',
    clientIp: '190.237.45.112',
    sha256Signature: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
  },
  {
    id: 'aud-002',
    timestamp: new Date(Date.now() - 75 * 60 * 1000).toISOString(),
    userId: 'system-rl',
    userEmail: 'rl-agent-autonomous@system.internal',
    userRole: 'rl_agent_system',
    action: 'EXECUTE_AUTONOMOUS_VRI',
    resource: 'IrrigationSector/S2 (Zona 2 - 2.1mm)',
    details: 'Ejecución automática por política PPO-VRI con confianza 0.96 en modo completamente autónomo.',
    clientIp: '10.0.4.18',
    sha256Signature: 'c5b8e92a1841a4a0c8b93708e3d8e52a979e2c38d3381f9a8d5f3a09d3b74548'
  },
  {
    id: 'aud-003',
    timestamp: new Date(Date.now() - 180 * 60 * 1000).toISOString(),
    userId: 'usr-001',
    userEmail: 'admin.global@agrotech.ai',
    userRole: 'superadmin',
    action: 'UPDATE_DIGITAL_TWIN_HYDRAULICS',
    resource: 'SoilProfile/field-ica-01/zone-1-nw',
    details: 'Calibración de conductividad saturada Ksat ajustada de 26.0 a 28.5 mm/h tras feedback de infiltración post-riego.',
    clientIp: '200.121.88.42',
    sha256Signature: '8f434346648f6b96df89dda901c5176b10e6d0ceec3e46e8c8b1a8d0efd8fa9e'
  }
];

export const INITIAL_SCHEDULED_REPORTS: ScheduledReport[] = [
  {
    id: 'sch-01',
    title: 'Informe Diario de Eficiencia Hídrica y Balance Digital Twin',
    format: 'pdf',
    frequency: 'daily',
    recipients: ['agronomo.senior@agricola.pe', 'productor.campo@sanpablo.com'],
    lastGenerated: '2026-08-31 06:00:00',
    status: 'active'
  },
  {
    id: 'sch-02',
    title: 'Libro Semanal de Telemetría y Decisiones RL (Multi-tab)',
    format: 'xlsx',
    frequency: 'weekly',
    recipients: ['admin.global@agrotech.ai'],
    lastGenerated: '2026-08-25 00:00:00',
    status: 'active'
  },
  {
    id: 'sch-03',
    title: 'Reporte Técnico Agronómico de Calibración de Suelos',
    format: 'docx',
    frequency: 'monthly',
    recipients: ['agronomo.senior@agricola.pe'],
    lastGenerated: '2026-08-01 08:00:00',
    status: 'active'
  }
];
