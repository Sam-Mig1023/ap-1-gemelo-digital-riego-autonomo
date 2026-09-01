import { ManagementZone, WhatIfScenarioInput, WhatIfScenarioResult } from '../types';

/**
 * Green-Ampt Infiltration Model
 * Infiltration Rate: f(t) = Ksat * (1 + (psi * DeltaTheta) / F(t))
 * where:
 *   Ksat: saturated hydraulic conductivity (mm/h)
 *   psi: matric suction at wetting front (mm)
 *   DeltaTheta: moisture deficit = porosity - initial moisture
 *   F(t): cumulative infiltration (mm)
 */
export function calculateGreenAmptInfiltration(
  waterAppliedMm: number,
  durationHours: number,
  ksat: number,
  suctionHeadMm: number,
  initialMoistureFrac: number,
  porosityFrac: number = 0.45
): {
  infiltratedMm: number;
  runoffMm: number;
  deepPercolationMm: number;
  finalMoistureFrac: number;
} {
  const deltaTheta = Math.max(0.02, porosityFrac - initialMoistureFrac);
  const applicationRate = waterAppliedMm / Math.max(0.2, durationHours);
  
  // Calculate average infiltration capacity
  const avgInfiltrationCapacity = ksat * (1 + (suctionHeadMm * deltaTheta) / Math.max(5, waterAppliedMm * 0.5));
  
  let infiltratedMm = 0;
  let runoffMm = 0;

  if (applicationRate <= avgInfiltrationCapacity) {
    infiltratedMm = waterAppliedMm;
    runoffMm = 0;
  } else {
    infiltratedMm = avgInfiltrationCapacity * durationHours;
    runoffMm = Math.max(0, waterAppliedMm - infiltratedMm);
  }

  // Deep percolation occurs if soil moisture exceeds Field Capacity (e.g., 0.32)
  const rootZoneStorageMm = 600 * (0.35 - initialMoistureFrac); // 600mm root depth
  let deepPercolationMm = 0;
  
  if (infiltratedMm > rootZoneStorageMm) {
    deepPercolationMm = (infiltratedMm - rootZoneStorageMm) * 0.65;
  }

  const effectiveAddition = (infiltratedMm - deepPercolationMm) / 600;
  const finalMoistureFrac = Math.min(porosityFrac, initialMoistureFrac + effectiveAddition);

  return {
    infiltratedMm: Number(infiltratedMm.toFixed(2)),
    runoffMm: Number(runoffMm.toFixed(2)),
    deepPercolationMm: Number(deepPercolationMm.toFixed(2)),
    finalMoistureFrac: Number(finalMoistureFrac.toFixed(3))
  };
}

/**
 * CWSI (Crop Water Stress Index) calculation from Infrared Thermometry (IRT)
 * CWSI = [(Tc - Ta) - (Tc - Ta)_lower] / [(Tc - Ta)_upper - (Tc - Ta)_lower]
 * where:
 *   Tc: Canopy Temperature (°C)
 *   Ta: Ambient Air Temperature (°C)
 *   VPD: Vapor Pressure Deficit (kPa)
 */
export function calculateCWSI(
  canopyTempC: number,
  airTempC: number,
  relativeHumidityPct: number
): {
  cwsi: number;
  vpdKPa: number;
  lowerBaselineDiff: number;
  upperBaselineDiff: number;
  stressCategory: 'none' | 'mild' | 'moderate' | 'severe';
} {
  // Saturated vapor pressure (Tetens formula)
  const es = 0.61078 * Math.exp((17.27 * airTempC) / (airTempC + 237.3));
  const ea = es * (relativeHumidityPct / 100);
  const vpdKPa = Math.max(0.1, es - ea);

  const deltaT = canopyTempC - airTempC;

  // Non-water-stressed baseline (NWSB): (Tc - Ta)_lower = a - b * VPD
  const a = 1.8;
  const b = 1.75;
  const lowerBaseline = a - b * vpdKPa;

  // Non-transpiring upper baseline: (Tc - Ta)_upper
  const upperBaseline = 5.2;

  let cwsi = (deltaT - lowerBaseline) / (upperBaseline - lowerBaseline);
  cwsi = Math.max(0, Math.min(1, cwsi));

  let stressCategory: 'none' | 'mild' | 'moderate' | 'severe' = 'none';
  if (cwsi > 0.65) stressCategory = 'severe';
  else if (cwsi > 0.45) stressCategory = 'moderate';
  else if (cwsi > 0.25) stressCategory = 'mild';

  return {
    cwsi: Number(cwsi.toFixed(3)),
    vpdKPa: Number(vpdKPa.toFixed(2)),
    lowerBaselineDiff: Number(lowerBaseline.toFixed(2)),
    upperBaselineDiff: Number(upperBaseline.toFixed(2)),
    stressCategory
  };
}

/**
 * FAO-56 Crop Evapotranspiration ETc = Kc * ET0
 * With soil water stress coefficient Ks = (TAW - Dr) / ((1 - p) * TAW)
 */
export function calculateEtc(
  et0MmDay: number,
  kc: number,
  currentMoistureFrac: number,
  fieldCapacityFrac: number,
  wiltingPointFrac: number,
  depletionFrac_p: number = 0.55
): {
  etcMmDay: number;
  ksWaterStressCoeff: number;
  rawEtcMmDay: number;
} {
  const taw = fieldCapacityFrac - wiltingPointFrac;
  const rawMoisture = currentMoistureFrac - wiltingPointFrac;
  const depletionDr = Math.max(0, taw - rawMoisture);
  
  let ks = 1.0;
  const readilyAvailableWater = depletionFrac_p * taw;
  
  if (depletionDr > readilyAvailableWater) {
    ks = (taw - depletionDr) / ((1 - depletionFrac_p) * taw);
    ks = Math.max(0, Math.min(1, ks));
  }

  const rawEtc = et0MmDay * kc;
  const actualEtc = rawEtc * ks;

  return {
    etcMmDay: Number(actualEtc.toFixed(2)),
    ksWaterStressCoeff: Number(ks.toFixed(2)),
    rawEtcMmDay: Number(rawEtc.toFixed(2))
  };
}

/**
 * Run What-If Simulation multi-day forward horizon
 */
export function runWhatIfScenario(
  zone: ManagementZone,
  input: WhatIfScenarioInput
): WhatIfScenarioResult[] {
  const results: WhatIfScenarioResult[] = [];
  let topMoisture = zone.currentMoisture10cm / 100;
  let deepMoisture = zone.currentMoisture30cm / 100;
  
  const baseDate = new Date();

  for (let d = 1; d <= input.horizonDays; d++) {
    const simDate = new Date(baseDate.getTime() + (d - 1) * 24 * 3600 * 1000).toISOString().split('T')[0];
    
    // Day 1 applies the simulated irrigation
    const dailyIrrigation = d === 1 ? input.irrigationActionMm : 0;
    const baseRainMm = [0, 1.2, 0, 3.5, 0.4, 0, 0][(d - 1) % 7];
    const dailyRainMm = baseRainMm * input.forecastRainFactor;
    
    const baseEt0 = 5.2 + (input.heatWaveScenarioDegC * 0.3);
    const kc = 1.15; // corn flowering
    
    const { etcMmDay, ksWaterStressCoeff } = calculateEtc(
      baseEt0,
      kc,
      (topMoisture + deepMoisture) / 2,
      zone.fieldCapacity,
      zone.wiltingPoint
    );

    // Apply Green-Ampt infiltration for water input
    const waterIn = dailyIrrigation + dailyRainMm;
    const infiltration = calculateGreenAmptInfiltration(
      waterIn,
      waterIn > 0 ? 3 : 1,
      zone.saturatedK,
      zone.suctionHead,
      topMoisture
    );

    // Update layers
    topMoisture = infiltration.finalMoistureFrac - (etcMmDay * 0.65) / 300;
    deepMoisture = deepMoisture + (infiltration.deepPercolationMm * 0.4) / 300 - (etcMmDay * 0.35) / 300;

    // Enforce bounds
    topMoisture = Math.max(zone.wiltingPoint * 0.8, Math.min(0.42, topMoisture));
    deepMoisture = Math.max(zone.wiltingPoint * 0.85, Math.min(0.40, deepMoisture));

    const avgMoisture = (topMoisture + deepMoisture) / 2;
    const cwsiEst = Math.max(0, Math.min(1, 1 - ksWaterStressCoeff + (input.heatWaveScenarioDegC * 0.04)));

    let cropStressLevel: 'none' | 'moderate' | 'severe' = 'none';
    if (cwsiEst > 0.6) cropStressLevel = 'severe';
    else if (cwsiEst > 0.35) cropStressLevel = 'moderate';

    const yieldImpact = (1 - ksWaterStressCoeff) * 3.8; // Yield response factor Ky = 1.25 for corn flowering

    results.push({
      dayIndex: d,
      date: simDate,
      moistureTopLayer: Number((topMoisture * 100).toFixed(1)),
      moistureDeepLayer: Number((deepMoisture * 100).toFixed(1)),
      cwsi: Number(cwsiEst.toFixed(2)),
      etcMm: etcMmDay,
      drainageLossMm: infiltration.deepPercolationMm,
      cropStressLevel,
      estimatedYieldImpactPct: Number(yieldImpact.toFixed(1))
    });
  }

  return results;
}
