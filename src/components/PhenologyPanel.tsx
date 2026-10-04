/**
 * Phenology Panel Component
 * Displays AI-powered phenological analysis with LangChain reasoning
 */

import React, { useState, useEffect } from 'react';
import { 
  Sprout, 
  Calendar, 
  TrendingUp, 
  Sparkles, 
  Clock,
  Target,
  Droplets,
  AlertCircle,
  CheckCircle,
  Loader,
  Brain,
  X
} from 'lucide-react';
import { phenologyService, AIPhenologyAnalysis, IrrigationRecommendation } from '../services/phenologyService';
import { ManagementZone } from '../types';

interface PhenologyPanelProps {
  zone: ManagementZone;
  onClose?: () => void;
  compact?: boolean;
}

export const PhenologyPanel: React.FC<PhenologyPanelProps> = ({ zone, onClose, compact = false }) => {
  const [loading, setLoading] = useState(false);
  const [aiAnalysis, setAiAnalysis] = useState<AIPhenologyAnalysis | null>(null);
  const [recommendation, setRecommendation] = useState<IrrigationRecommendation | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadAIAnalysis();
  }, [zone.id]);

  const loadAIAnalysis = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Get AI phenology analysis
      const analysisRes = await phenologyService.getAIPhenologyAnalysis(zone.id);
      setAiAnalysis(analysisRes.data);

      // Get AI irrigation recommendation
      const recRes = await phenologyService.getAIIrrigationRecommendation(
        zone.id,
        zone.currentMoisture10cm,
        5.5, // ET0 - podría venir de datos reales
        0    // Rain forecast - podría venir de radar
      );
      setRecommendation(recRes.recommendation);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load AI analysis');
      console.error('Phenology panel error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStageColor = (stage: string) => {
    const colors: Record<string, string> = {
      initial: 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900/30',
      vegetative: 'text-green-600 bg-green-100 dark:bg-green-900/30',
      flowering: 'text-pink-600 bg-pink-100 dark:bg-pink-900/30',
      yield_formation: 'text-orange-600 bg-orange-100 dark:bg-orange-900/30',
      ripening: 'text-red-600 bg-red-100 dark:bg-red-900/30'
    };
    return colors[stage] || 'text-slate-600 bg-slate-100';
  };

  const getStageEmoji = (stage: string) => {
    const emojis: Record<string, string> = {
      initial: '🌱',
      vegetative: '🌿',
      flowering: '🌸',
      yield_formation: '🍅',
      ripening: '🔴'
    };
    return emojis[stage] || '🌾';
  };

  if (compact && !zone.cropStage) {
    return null; // No mostrar en modo compacto si no hay datos
  }

  return (
    <div className={`${compact ? 'p-3' : 'p-6'} bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-lg`}>
      
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Sprout className="w-5 h-5 text-emerald-500" />
          <h3 className="text-lg font-bold text-slate-900 dark:text-white">
            Análisis Fenológico AI
          </h3>
        </div>
        {onClose && (
          <button 
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* Loading State */}
      {loading && (
        <div className="flex flex-col items-center justify-center py-8">
          <Loader className="w-8 h-8 text-emerald-500 animate-spin mb-3" />
          <p className="text-sm text-slate-600 dark:text-slate-400">Consultando agente LangChain...</p>
        </div>
      )}

      {/* Error State */}
      {error && !loading && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <div className="flex items-center gap-2 text-red-700 dark:text-red-400">
            <AlertCircle className="w-5 h-5" />
            <p className="text-sm font-medium">{error}</p>
          </div>
        </div>
      )}

      {/* Main Content */}
      {!loading && !error && aiAnalysis && (
        <div className="space-y-4">
          
          {/* Phenology Overview */}
          <div className="bg-gradient-to-br from-emerald-50 to-teal-50 dark:from-emerald-950/40 dark:to-teal-950/40 p-4 rounded-lg border border-emerald-200 dark:border-emerald-800">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <span className="text-2xl">{getStageEmoji(aiAnalysis.phenology.current_stage)}</span>
                <div>
                  <h4 className="font-bold text-slate-900 dark:text-white">{aiAnalysis.phenology.crop_name}</h4>
                  <p className="text-xs text-slate-600 dark:text-slate-400">Zona: {zone.name}</p>
                </div>
              </div>
              <div className={`px-3 py-1 rounded-full text-xs font-semibold ${getStageColor(aiAnalysis.phenology.current_stage)}`}>
                {aiAnalysis.phenology.stage_name}
              </div>
            </div>

            {/* Progress Bar */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs text-slate-600 dark:text-slate-400">
                <span>Progreso del ciclo</span>
                <span className="font-bold">{aiAnalysis.phenology.progress_pct}%</span>
              </div>
              <div className="w-full bg-slate-200 dark:bg-slate-700 h-2 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-emerald-500 to-teal-500 rounded-full transition-all duration-500"
                  style={{ width: `${aiAnalysis.phenology.progress_pct}%` }}
                />
              </div>
            </div>

            {/* Key Metrics */}
            <div className="grid grid-cols-3 gap-3 mt-4">
              <div className="text-center">
                <div className="flex items-center justify-center gap-1 text-emerald-600 dark:text-emerald-400 mb-1">
                  <Calendar className="w-4 h-4" />
                </div>
                <p className="text-xs text-slate-600 dark:text-slate-400">Días desde siembra</p>
                <p className="text-lg font-bold text-slate-900 dark:text-white">{aiAnalysis.phenology.days_since_planting}</p>
              </div>
              <div className="text-center">
                <div className="flex items-center justify-center gap-1 text-pink-600 dark:text-pink-400 mb-1">
                  <Target className="w-4 h-4" />
                </div>
                <p className="text-xs text-slate-600 dark:text-slate-400">Días a floración</p>
                <p className="text-lg font-bold text-slate-900 dark:text-white">{aiAnalysis.phenology.days_to_flowering}</p>
              </div>
              <div className="text-center">
                <div className="flex items-center justify-center gap-1 text-amber-600 dark:text-amber-400 mb-1">
                  <Clock className="w-4 h-4" />
                </div>
                <p className="text-xs text-slate-600 dark:text-slate-400">Días a cosecha</p>
                <p className="text-lg font-bold text-slate-900 dark:text-white">{aiAnalysis.phenology.days_to_harvest}</p>
              </div>
            </div>

            {/* Kc Value */}
            <div className="mt-4 bg-white dark:bg-slate-900/60 rounded-lg p-3 border border-emerald-200 dark:border-emerald-800">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Droplets className="w-4 h-4 text-blue-500" />
                  <span className="text-sm font-medium text-slate-700 dark:text-slate-300">Coeficiente Kc</span>
                </div>
                <span className="text-2xl font-bold text-blue-600 dark:text-blue-400">{aiAnalysis.phenology.kc.toFixed(2)}</span>
              </div>
              <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
                FAO-56 para etapa {aiAnalysis.phenology.stage_name}
              </p>
            </div>
          </div>

          {/* AI Reasoning */}
          <div className="bg-purple-50 dark:bg-purple-950/30 p-4 rounded-lg border border-purple-200 dark:border-purple-800">
            <div className="flex items-center gap-2 mb-3">
              <Brain className="w-5 h-5 text-purple-600 dark:text-purple-400" />
              <h4 className="font-bold text-slate-900 dark:text-white">Análisis del Agente AI</h4>
              <span className="text-xs px-2 py-0.5 bg-purple-200 dark:bg-purple-900/50 text-purple-700 dark:text-purple-300 rounded-full">
                LangChain ReAct
              </span>
            </div>
            <div className="prose prose-sm dark:prose-invert max-w-none">
              <p className="text-sm text-slate-700 dark:text-slate-300 whitespace-pre-wrap">{aiAnalysis.ai_reasoning}</p>
            </div>
          </div>

          {/* Irrigation Recommendation */}
          {recommendation && (
            <div className="bg-blue-50 dark:bg-blue-950/30 p-4 rounded-lg border border-blue-200 dark:border-blue-800">
              <div className="flex items-center gap-2 mb-3">
                <Sparkles className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                <h4 className="font-bold text-slate-900 dark:text-white">Recomendación de Riego AI</h4>
                <span className="text-xs px-2 py-0.5 bg-blue-200 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300 rounded-full">
                  Confianza: {(recommendation.confidence * 100).toFixed(0)}%
                </span>
              </div>

              <div className="mb-3">
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-bold text-blue-600 dark:text-blue-400">{recommendation.recommended_mm.toFixed(1)}</span>
                  <span className="text-sm text-slate-600 dark:text-slate-400">mm</span>
                </div>
                <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">{recommendation.reasoning}</p>
              </div>

              {/* Risk Factors */}
              {recommendation.risk_factors.length > 0 && (
                <div className="mb-3">
                  <p className="text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Factores de Riesgo:</p>
                  <ul className="space-y-1">
                    {recommendation.risk_factors.map((risk, idx) => (
                      <li key={idx} className="flex items-start gap-2 text-xs text-orange-700 dark:text-orange-300">
                        <AlertCircle className="w-3 h-3 mt-0.5 flex-shrink-0" />
                        <span>{risk}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Optimization Tips */}
              {recommendation.optimization_tips.length > 0 && (
                <div>
                  <p className="text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Tips de Optimización:</p>
                  <ul className="space-y-1">
                    {recommendation.optimization_tips.map((tip, idx) => (
                      <li key={idx} className="flex items-start gap-2 text-xs text-emerald-700 dark:text-emerald-300">
                        <CheckCircle className="w-3 h-3 mt-0.5 flex-shrink-0" />
                        <span>{tip}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Refresh Button */}
          <button
            onClick={loadAIAnalysis}
            className="w-full px-4 py-2 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 text-white font-medium rounded-lg transition-all flex items-center justify-center gap-2"
          >
            <TrendingUp className="w-4 h-4" />
            Actualizar Análisis AI
          </button>
        </div>
      )}
    </div>
  );
};
