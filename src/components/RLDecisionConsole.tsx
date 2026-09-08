import React, { useState } from 'react';
import { 
  Cpu, 
  CheckCircle2, 
  AlertOctagon, 
  Sliders, 
  HelpCircle, 
  Zap, 
  Clock, 
  Layers, 
  ShieldAlert, 
  Play, 
  RefreshCw,
  Edit3,
  BarChart3,
  ThumbsUp,
  FileCheck2
} from 'lucide-react';
import { 
  ManagementZone, 
  RLDecision, 
  WeatherRadarCell, 
  SensorTelemetry, 
  UserRole 
} from '../types';
import { buildObservationTensor, computeRLReward } from '../services/rlAgentEngine';
import { useLanguage } from '../contexts/LanguageContext';

interface RLDecisionConsoleProps {
  zones: ManagementZone[];
  decisions: RLDecision[];
  radarCells: WeatherRadarCell[];
  sensors: SensorTelemetry[];
  activeRole: UserRole;
  systemMode: string;
  onApproveDecision: (decisionId: string) => void;
  onManualOverride: (decisionId: string, customDepthMm: number, reason: string) => void;
  onRecomputeAllRL: () => void;
  onTriggerFeedbackModal: (decision: RLDecision) => void;
}

export const RLDecisionConsole: React.FC<RLDecisionConsoleProps> = ({
  zones,
  decisions,
  radarCells,
  sensors,
  activeRole,
  systemMode,
  onApproveDecision,
  onManualOverride,
  onRecomputeAllRL,
  onTriggerFeedbackModal
}) => {
  const { t } = useLanguage();
  const [selectedDecisionId, setSelectedDecisionId] = useState<string>(decisions[0]?.id || '');
  const [overrideModalOpen, setOverrideModalOpen] = useState<boolean>(false);
  const [overrideDepthMm, setOverrideDepthMm] = useState<number>(5.0);
  const [overrideReason, setOverrideReason] = useState<string>('Ajuste agronómico preventivo por viento desecante');

  const selectedDecision = decisions.find(d => d.id === selectedDecisionId) || decisions[0];
  const relatedZone = zones.find(z => z.id === selectedDecision?.zoneId) || zones[0];
  const observation = buildObservationTensor(relatedZone, radarCells[0], sensors[0]);
  const rewardBreakdown = computeRLReward(selectedDecision?.recommendedDepthMm || 0, observation.cwsi, 0, observation.electricityTariffTier);

  const canApprove = activeRole === 'superadmin' || activeRole === 'agronomist' || activeRole === 'farmer';

  const handleOpenOverride = (decision: RLDecision) => {
    setSelectedDecisionId(decision.id);
    setOverrideDepthMm(decision.recommendedDepthMm);
    setOverrideModalOpen(true);
  };

  const handleConfirmOverride = () => {
    if (selectedDecision) {
      onManualOverride(selectedDecision.id, overrideDepthMm, overrideReason);
      setOverrideModalOpen(false);
    }
  };

  return (
    <div className="space-y-6">
      
      {/* Top Banner: RL Engine Status & Policy Meta */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-4 sm:p-5 rounded-2xl flex flex-wrap items-center justify-between gap-4 shadow-xl">
        <div className="flex items-center gap-3.5">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-700 flex items-center justify-center shadow-lg shadow-emerald-950/50 border border-emerald-400/40">
            <Cpu className="w-6 h-6 text-white animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <h2 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white tracking-tight">
                {t('rlConsole.title')}
              </h2>
              <span className="px-2 py-0.5 text-xs font-semibold rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                {t('rlConsole.modelActive')}
              </span>
            </div>
            <p className="text-xs text-slate-600 dark:text-slate-400 mt-0.5">
              {t('rlConsole.subtitle')}
            </p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2.5">
          <button
            id="recalculate-rl-btn"
            onClick={onRecomputeAllRL}
            className="px-3.5 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 text-xs font-medium border border-slate-300 dark:border-slate-700 flex items-center gap-1.5 transition-all"
          >
            <RefreshCw className="w-3.5 h-3.5 text-emerald-400" />
            <span>{t('rlConsole.reinfer')}</span>
          </button>
        </div>
      </div>

      {/* Main Grid: Observation Tensor + XAI Explainability + Decisions List */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Column: 3D Observation Tensor Live Feed (4 Cols) */}
        <div className="lg:col-span-4 space-y-4">
          
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-4 rounded-xl space-y-3.5 shadow-lg">
            <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-2.5">
              <span className="text-xs font-bold text-slate-800 dark:text-slate-200 uppercase tracking-wider flex items-center gap-1.5">
                <Layers className="w-3.5 h-3.5 text-emerald-400" />
                {t('rlConsole.observationTensor')}
              </span>
              <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-500/30">
                Shape: [4, 12]
              </span>
            </div>

            <div className="space-y-2 text-xs font-mono">
              
              <div className="bg-slate-50 dark:bg-slate-950/80 p-2.5 rounded-lg border border-slate-200/80 dark:border-slate-800/80 flex items-center justify-between">
                <span className="text-slate-600 dark:text-slate-400">{t('rlConsole.moistureProfile')}</span>
                <span className="text-emerald-400 font-bold">
                  [{observation.soilMoistureProfile.join('%, ')}%]
                </span>
              </div>

              <div className="bg-slate-50 dark:bg-slate-950/80 p-2.5 rounded-lg border border-slate-200/80 dark:border-slate-800/80 flex items-center justify-between">
                <span className="text-slate-600 dark:text-slate-400">{t('rlConsole.canopyTemp')}</span>
                <span className="text-amber-300 font-bold">{observation.canopyTempKelvin} K ({relatedZone.currentCanopyTemp}°C)</span>
              </div>

              <div className="bg-slate-50 dark:bg-slate-950/80 p-2.5 rounded-lg border border-slate-200/80 dark:border-slate-800/80 flex items-center justify-between">
                <span className="text-slate-600 dark:text-slate-400">{t('rlConsole.vpd')}</span>
                <span className="text-slate-900 dark:text-white font-bold">{observation.vaporPressureDeficitKPa} kPa</span>
              </div>

              <div className="bg-slate-50 dark:bg-slate-950/80 p-2.5 rounded-lg border border-slate-200/80 dark:border-slate-800/80 flex items-center justify-between">
                <span className="text-slate-600 dark:text-slate-400">{t('rlConsole.cwsiIndex')}</span>
                <span className={`font-bold ${observation.cwsi > 0.45 ? 'text-rose-400' : 'text-emerald-400'}`}>
                  {observation.cwsi}
                </span>
              </div>

              <div className="bg-slate-50 dark:bg-slate-950/80 p-2.5 rounded-lg border border-slate-200/80 dark:border-slate-800/80 flex items-center justify-between">
                <span className="text-slate-600 dark:text-slate-400">{t('rlConsole.etcDemand')}</span>
                <span className="text-blue-300 font-bold">{observation.etcMmDay} mm/día</span>
              </div>

              <div className="bg-slate-50 dark:bg-slate-950/80 p-2.5 rounded-lg border border-slate-200/80 dark:border-slate-800/80 flex items-center justify-between">
                <span className="text-slate-600 dark:text-slate-400">{t('rlConsole.radarRain')}</span>
                <span className="text-purple-300 font-bold">{observation.forecastRain24hMm} mm ({observation.radarEchoIntensity} dBZ)</span>
              </div>

              <div className="bg-slate-50 dark:bg-slate-950/80 p-2.5 rounded-lg border border-slate-200/80 dark:border-slate-800/80 flex items-center justify-between">
                <span className="text-slate-600 dark:text-slate-400">{t('rlConsole.tariff')}</span>
                <span className="text-yellow-300 font-bold">
                  {observation.electricityTariffTier === 1 ? t('rlConsole.tariffLow') : t('rlConsole.tariffMid')}
                </span>
              </div>

            </div>
          </div>

          {/* Multi-Objective Reward Decomposition */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-4 rounded-xl space-y-3 shadow-lg">
            <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-2">
              <span className="text-xs font-bold text-slate-800 dark:text-slate-200 uppercase tracking-wider flex items-center gap-1.5">
                <BarChart3 className="w-3.5 h-3.5 text-blue-400" />
                {t('rlConsole.rewardDecomposition')}
              </span>
              <span className="text-xs font-mono font-bold text-emerald-400">
                {rewardBreakdown.totalReward} pts
              </span>
            </div>

            <div className="space-y-2 text-xs">
              <div className="flex justify-between items-center text-slate-600 dark:text-slate-400">
                <span>{t('rlConsole.stressPenalty')}</span>
                <span className="font-mono text-rose-400">{rewardBreakdown.stressPenalty} pts</span>
              </div>
              <div className="flex justify-between items-center text-slate-600 dark:text-slate-400">
                <span>{t('rlConsole.waterPenalty')}</span>
                <span className="font-mono text-amber-400">{rewardBreakdown.waterConsumptionPenalty} pts</span>
              </div>
              <div className="flex justify-between items-center text-slate-600 dark:text-slate-400">
                <span>{t('rlConsole.overIrrigationPenalty')}</span>
                <span className="font-mono text-blue-400">{rewardBreakdown.overIrrigationPenalty} pts</span>
              </div>
              <div className="flex justify-between items-center text-slate-600 dark:text-slate-400">
                <span>{t('rlConsole.energyPenalty')}</span>
                <span className="font-mono text-purple-400">{rewardBreakdown.energyCostPenalty} pts</span>
              </div>
            </div>
          </div>

        </div>

        {/* Right Column: Decision Queue & Explainable AI (8 Cols) */}
        <div className="lg:col-span-8 space-y-4">
          
          {/* Decision Selector Cards */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-4 rounded-xl space-y-3 shadow-lg">
            <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-2">
              <span className="text-xs font-bold text-slate-800 dark:text-slate-200 uppercase tracking-wider flex items-center gap-1.5">
                <Zap className="w-3.5 h-3.5 text-emerald-400" />
                {t('rlConsole.decisionQueue')}
              </span>
              <span className="text-xs text-slate-600 dark:text-slate-400">
                {t('rlConsole.systemMode')} <strong className="text-slate-900 dark:text-white">{systemMode === 'assisted' ? t('rlConsole.modeAssisted') : systemMode === 'manual' ? t('rlConsole.modeManual') : systemMode === 'autonomous' ? t('rlConsole.modeAutonomous') : systemMode}</strong>
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {decisions.map((dec) => {
                const isSelected = dec.id === selectedDecision?.id;
                return (
                  <div
                    key={dec.id}
                    onClick={() => setSelectedDecisionId(dec.id)}
                    className={`p-3.5 rounded-xl border cursor-pointer transition-all ${
                      isSelected
                        ? 'bg-slate-200/90 dark:bg-slate-800/90 border-emerald-500/60 shadow-lg shadow-emerald-950/30'
                        : 'bg-slate-50 dark:bg-slate-950/60 border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-slate-900 dark:text-white">{dec.zoneName.split('(')[0]}</span>
                      <span className={`text-[10px] font-semibold px-2 py-0.5 rounded border ${
                        dec.status === 'approved'
                          ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                          : dec.status === 'pending'
                          ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                          : dec.status === 'feedback_verified'
                          ? 'bg-blue-500/20 text-blue-300 border-blue-500/40'
                          : 'bg-slate-500/20 text-slate-300 border-slate-500/40'
                      }`}>
                        {dec.status === 'approved' ? t('rlConsole.statusApproved') : dec.status === 'pending' ? t('rlConsole.statusPending') : dec.status === 'feedback_verified' ? t('rlConsole.statusVerified') : dec.status.toUpperCase()}
                      </span>
                    </div>

                    <div className="mt-2 flex items-baseline justify-between">
                      <div>
                        <span className="text-2xl font-bold font-mono text-emerald-400">
                          {dec.recommendedDepthMm} <span className="text-xs text-slate-600 dark:text-slate-400 font-sans">mm</span>
                        </span>
                        <p className="text-[11px] text-slate-600 dark:text-slate-400">{dec.recommendedVolumeM3.toLocaleString()} m³</p>
                      </div>
                      <div className="text-right">
                        <span className="text-xs font-mono font-semibold text-slate-700 dark:text-slate-300">
                          {t('rlConsole.confidence')} {Math.round(dec.confidenceScore * 100)}%
                        </span>
                        <p className="text-[10px] text-slate-500">{t('rlConsole.window')} {dec.executionWindowHours.start} - {dec.executionWindowHours.end}</p>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Selected Decision Detail: XAI Feature Attributions & Actions */}
          {selectedDecision && (
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-4 sm:p-5 rounded-xl space-y-4 shadow-lg">
              
              <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 dark:border-slate-800 pb-3">
                <div>
                  <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                    <span>{t('rlConsole.explainability', { zone: selectedDecision.zoneName })}</span>
                  </h3>
                  <p className="text-xs text-emerald-400/90 mt-0.5">
                    {t('rlConsole.dominantFeature', { feature: selectedDecision.explanation.dominantFeature })}
                  </p>
                </div>

                {/* Status and Action Buttons */}
                <div className="flex items-center gap-2">
                  {selectedDecision.status === 'pending' && (
                    <>
                      <button
                        id="approve-decision-btn"
                        onClick={() => onApproveDecision(selectedDecision.id)}
                        disabled={!canApprove}
                        className={`px-3 py-1.5 rounded-lg text-xs font-medium flex items-center gap-1.5 transition-all ${
                          canApprove
                            ? 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-md shadow-emerald-950/40'
                            : 'bg-slate-100 dark:bg-slate-800 text-slate-500 cursor-not-allowed'
                        }`}
                      >
                        <ThumbsUp className="w-3.5 h-3.5" />
                        <span>{t('rlConsole.approveIrrigation')}</span>
                      </button>

                      <button
                        id="override-decision-btn"
                        onClick={() => handleOpenOverride(selectedDecision)}
                        className="px-3 py-1.5 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 text-xs font-medium border border-slate-300 dark:border-slate-700 flex items-center gap-1.5 transition-all"
                      >
                        <Edit3 className="w-3.5 h-3.5 text-amber-400" />
                        <span>{t('rlConsole.manualOverride')}</span>
                      </button>
                    </>
                  )}

                  {selectedDecision.status === 'approved' && (
                    <button
                      id="trigger-feedback-btn"
                      onClick={() => onTriggerFeedbackModal(selectedDecision)}
                      className="px-3.5 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-medium flex items-center gap-1.5 transition-all shadow-md shadow-blue-950/40"
                    >
                      <FileCheck2 className="w-3.5 h-3.5" />
                      <span>{t('rlConsole.verifyFeedback')}</span>
                    </button>
                  )}
                </div>
              </div>

              {/* SHAP Feature Impact Bars */}
              <div className="space-y-3">
                <span className="text-xs font-semibold text-slate-600 dark:text-slate-400 block">
                  {t('rlConsole.shapContribution')}
                </span>

                <div className="space-y-2.5">
                  {selectedDecision.explanation.shapValues.map((shap, i) => {
                    const isPositive = shap.impact >= 0;
                    return (
                      <div key={i} className="space-y-1 bg-slate-50 dark:bg-slate-950/60 p-2.5 rounded-lg border border-slate-200/80 dark:border-slate-800/80">
                        <div className="flex justify-between items-center text-xs">
                          <span className="text-slate-800 dark:text-slate-200 font-medium">{shap.feature}</span>
                          <span className={`font-mono font-bold ${isPositive ? 'text-emerald-400' : 'text-blue-400'}`}>
                            {isPositive ? `+${shap.impact}` : shap.impact}
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-600 dark:text-slate-400">{shap.description}</p>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Natural Language Reasoning from RL */}
              <div className="bg-emerald-950/20 border border-emerald-500/30 p-3 rounded-lg text-xs text-slate-700 dark:text-slate-300">
                <p className="font-semibold text-emerald-300 mb-1">{t('rlConsole.biophysicalReasoning')}</p>
                <p>{selectedDecision.explanation.reasoningText}</p>
              </div>

              {/* Safe Mode Alert Banner if Triggered */}
              {selectedDecision.explanation.safeModeTriggered && (
                <div className="bg-rose-950/30 border border-rose-500/40 p-3 rounded-lg flex items-start gap-2.5 text-xs text-rose-300">
                  <ShieldAlert className="w-4 h-4 text-rose-400 mt-0.5 flex-shrink-0" />
                  <div>
                    <strong className="block text-rose-200 font-semibold">{t('rlConsole.safeModeOn')}</strong>
                    <span>{selectedDecision.explanation.safeModeReason}</span>
                  </div>
                </div>
              )}

            </div>
          )}

        </div>

      </div>

      {/* Manual Override Modal */}
      {overrideModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-50/80 dark:bg-slate-950/80 backdrop-blur-sm p-4">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl max-w-md w-full p-5 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-3">
              <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <Edit3 className="w-4 h-4 text-amber-400" />
                <span>{t('rlConsole.overrideTitle')}</span>
              </h3>
              <button
                onClick={() => setOverrideModalOpen(false)}
                className="text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white text-xs"
              >
                ✕
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-600 dark:text-slate-400 mb-1">{t('rlConsole.prescribedDose')}</label>
                <span className="font-mono text-sm font-bold text-emerald-400">{selectedDecision?.recommendedDepthMm} mm</span>
              </div>

              <div>
                <label className="block text-slate-700 dark:text-slate-300 font-semibold mb-1">{t('rlConsole.newDose')}</label>
                <input
                  type="number"
                  min="0"
                  max="30"
                  step="0.5"
                  value={overrideDepthMm}
                  onChange={(e) => setOverrideDepthMm(parseFloat(e.target.value) || 0)}
                  className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg px-3 py-2 text-slate-900 dark:text-white font-mono focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-slate-700 dark:text-slate-300 font-semibold mb-1">{t('rlConsole.justification')}</label>
                <textarea
                  rows={3}
                  value={overrideReason}
                  onChange={(e) => setOverrideReason(e.target.value)}
                  className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg p-2.5 text-slate-900 dark:text-white focus:outline-none focus:border-emerald-500"
                  placeholder={t('rlConsole.justificationPlaceholder')}
                />
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-2 border-t border-slate-200 dark:border-slate-800">
              <button
                onClick={() => setOverrideModalOpen(false)}
                className="px-3 py-1.5 text-xs text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
              >
                {t('common.cancel')}
              </button>
              <button
                id="confirm-override-submit-btn"
                onClick={handleConfirmOverride}
                className="px-4 py-1.5 rounded-lg bg-amber-600 hover:bg-amber-500 text-white text-xs font-semibold shadow-md shadow-amber-950/40"
              >
                {t('rlConsole.confirmAndLog')}
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};
