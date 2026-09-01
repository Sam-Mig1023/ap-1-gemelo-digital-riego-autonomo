import { ManagementZone, ClosedLoopFeedback } from '../types';

/**
 * Closed Loop Post-Irrigation Evaluator
 * Evaluates the actual physical sensor response 30-60 minutes after irrigation
 * and performs parameter recalibration for the Digital Twin.
 */
export function evaluatePostIrrigationFeedback(
  zone: ManagementZone,
  appliedMm: number,
  measuredMoisturePostPct: number
): {
  feedback: ClosedLoopFeedback;
  updatedZone: ManagementZone;
} {
  // Modeled expected increase: 
  // delta_theta = (appliedMm * efficiency) / (root_depth_mm * bulk_factor)
  const expectedIncreasePct = (appliedMm * zone.hydraulicEfficiency) / 6.0;
  const expectedMoisturePostPct = zone.currentMoisture10cm + expectedIncreasePct;
  
  const residualError = measuredMoisturePostPct - expectedMoisturePostPct;
  const infiltrationEfficiency = Number(Math.min(1.0, Math.max(0.4, (measuredMoisturePostPct - zone.currentMoisture10cm) / Math.max(1, expectedIncreasePct))).toFixed(2));

  // Parameter recalibration: if water penetrated faster than expected, Ksat was underestimated
  let ksatAdjustmentPct = 0;
  let newKsat = zone.saturatedK;

  if (Math.abs(residualError) > 1.5) {
    // If measured moisture in 10cm is lower than expected, water percolated faster -> increase Ksat
    if (residualError < 0) {
      ksatAdjustmentPct = +6.5;
      newKsat = Number((zone.saturatedK * 1.065).toFixed(1));
    } else {
      ksatAdjustmentPct = -5.0;
      newKsat = Number((zone.saturatedK * 0.95).toFixed(1));
    }
  }

  const feedback: ClosedLoopFeedback = {
    decisionId: `dec-fb-${Date.now()}`,
    zoneId: zone.id,
    timestampPostIrrigation: new Date().toISOString(),
    expectedMoisturePost: Number(expectedMoisturePostPct.toFixed(1)),
    measuredMoisturePost: Number(measuredMoisturePostPct.toFixed(1)),
    residualError: Number(residualError.toFixed(2)),
    infiltrationEfficiency,
    modelRecalibrated: Math.abs(ksatAdjustmentPct) > 0,
    ksatAdjustmentPct,
    rewardFeedback: Number((10 - Math.abs(residualError) * 2).toFixed(1))
  };

  const updatedZone: ManagementZone = {
    ...zone,
    saturatedK: newKsat,
    currentMoisture10cm: measuredMoisturePostPct,
    currentMoisture30cm: Number((zone.currentMoisture30cm + expectedIncreasePct * 0.7).toFixed(1)),
    currentMoisture60cm: Number((zone.currentMoisture60cm + expectedIncreasePct * 0.4).toFixed(1)),
    currentCanopyTemp: Number(Math.max(22.0, zone.currentCanopyTemp - 3.5).toFixed(1)),
    cwsi: Number(Math.max(0.08, zone.cwsi - 0.35).toFixed(2)),
    status: 'optimal'
  };

  return { feedback, updatedZone };
}
