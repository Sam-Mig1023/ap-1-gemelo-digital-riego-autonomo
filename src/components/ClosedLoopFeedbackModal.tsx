import React, { useState } from 'react';
import { 
  FileCheck2, 
  RotateCw, 
  ArrowRight, 
  CheckCircle, 
  TrendingUp, 
  AlertCircle,
  Sparkles
} from 'lucide-react';
import { ManagementZone, RLDecision, ClosedLoopFeedback } from '../types';
import { evaluatePostIrrigationFeedback } from '../services/closedLoopController';
import { useLanguage } from '../contexts/LanguageContext';

interface ClosedLoopFeedbackModalProps {
  decision: RLDecision;
  zone: ManagementZone;
  onClose: () => void;
  onCommitRecalibration: (feedback: ClosedLoopFeedback, updatedZone: ManagementZone) => void;
}

export const ClosedLoopFeedbackModal: React.FC<ClosedLoopFeedbackModalProps> = ({
  decision,
  zone,
  onClose,
  onCommitRecalibration
}) => {
  const { t } = useLanguage();
  const [measuredMoisturePost, setMeasuredMoisturePost] = useState<number>(
    Number((zone.currentMoisture10cm + (decision.recommendedDepthMm * zone.hydraulicEfficiency) / 6.0 + (Math.random() * 1.2 - 0.6)).toFixed(1))
  );

  const { feedback, updatedZone } = evaluatePostIrrigationFeedback(
    zone,
    decision.recommendedDepthMm,
    measuredMoisturePost
  );

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-500/80 dark:bg-slate-950/80 backdrop-blur-md p-4">
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl max-w-lg w-full p-5 sm:p-6 space-y-5 shadow-2xl">
        
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-3">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-blue-500/20 text-blue-400 border border-blue-500/40 flex items-center justify-center">
              <FileCheck2 className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-900 dark:text-white">{t('feedbackModal.title')}</h3>
              <p className="text-xs text-slate-600 dark:text-slate-400" dangerouslySetInnerHTML={{__html: t('feedbackModal.zoneDose', {zone: zone.name, dose: decision.recommendedDepthMm})}}></p>
            </div>
          </div>
          <button onClick={onClose} className="text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white text-sm">✕</button>
        </div>

        {/* Comparison Metrics */}
        <div className="grid grid-cols-2 gap-3 text-xs">
          
          <div className="bg-slate-50 dark:bg-slate-950/80 p-3 rounded-xl border border-slate-200 dark:border-slate-800 space-y-1">
            <span className="text-slate-600 dark:text-slate-400 block text-[11px]">{t('feedbackModal.metrics.simulated.label')}</span>
            <span className="text-xl font-bold font-mono text-blue-400">{feedback.expectedMoisturePost}%</span>
            <p className="text-[10px] text-slate-600 dark:text-slate-500">{t('feedbackModal.metrics.simulated.hint')}</p>
          </div>

          <div className="bg-slate-50 dark:bg-slate-950/80 p-3 rounded-xl border border-slate-200 dark:border-slate-800 space-y-1">
            <span className="text-slate-600 dark:text-slate-400 block text-[11px]">{t('feedbackModal.metrics.measured.label')}</span>
            <div className="flex items-center gap-2">
              <input
                type="number"
                step="0.1"
                value={measuredMoisturePost}
                onChange={(e) => setMeasuredMoisturePost(parseFloat(e.target.value) || zone.currentMoisture10cm)}
                className="w-20 bg-slate-100 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded px-2 py-0.5 text-slate-900 dark:text-white font-mono font-bold text-sm focus:outline-none focus:border-emerald-500"
              />
              <span className="text-emerald-400 font-bold text-sm">%</span>
            </div>
            <p className="text-[10px] text-slate-600 dark:text-slate-500">{t('feedbackModal.metrics.measured.hint')}</p>
          </div>

        </div>

        {/* Residual Error & Calibration Delta */}
        <div className="bg-slate-50 dark:bg-slate-950/90 p-4 rounded-xl border border-slate-200 dark:border-slate-800 space-y-2.5 text-xs">
          
          <div className="flex justify-between items-center">
            <span className="text-slate-700 dark:text-slate-300 font-semibold">{t('feedbackModal.calibration.residual')}</span>
            <span className={`font-mono font-bold ${Math.abs(feedback.residualError) > 1.5 ? 'text-amber-400' : 'text-emerald-400'}`}>
              {feedback.residualError > 0 ? `+${feedback.residualError}` : feedback.residualError}% m³/m³
            </span>
          </div>

          <div className="flex justify-between items-center">
            <span className="text-slate-700 dark:text-slate-300 font-semibold">{t('feedbackModal.calibration.efficiency')}</span>
            <span className="font-mono font-bold text-teal-300">
              {Math.round(feedback.infiltrationEfficiency * 100)}%
            </span>
          </div>

          <div className="flex justify-between items-center border-t border-slate-200/80 dark:border-slate-800/80 pt-2">
            <span className="text-slate-700 dark:text-slate-300 font-semibold">{t('feedbackModal.calibration.ksat')}</span>
            <span className="font-mono font-bold text-purple-300">
              {zone.saturatedK} → {updatedZone.saturatedK} mm/h ({feedback.ksatAdjustmentPct > 0 ? `+${feedback.ksatAdjustmentPct}` : feedback.ksatAdjustmentPct}%)
            </span>
          </div>

        </div>

        {/* Calibration Feedback Summary */}
        <div className="bg-blue-950/20 border border-blue-500/30 p-3 rounded-lg flex items-start gap-2.5 text-xs text-blue-300">
          <Sparkles className="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0" />
          <div>
            <strong className="block text-blue-200 font-semibold">{t('feedbackModal.summary.title')}</strong>
            <span>
              {t('feedbackModal.summary.body')}
            </span>
          </div>
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-2 pt-2 border-t border-slate-200 dark:border-slate-800">
          <button
            onClick={onClose}
            className="px-3.5 py-1.5 text-xs text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
          >
            {t('common.close')}
          </button>
          <button
            id="commit-recalibration-btn"
            onClick={() => {
              onCommitRecalibration(feedback, updatedZone);
              onClose();
            }}
            className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold flex items-center gap-1.5 shadow-lg shadow-emerald-950/40"
          >
            <CheckCircle className="w-3.5 h-3.5" />
            <span>{t('feedbackModal.actions.commit')}</span>
          </button>
        </div>

      </div>
    </div>
  );
};
