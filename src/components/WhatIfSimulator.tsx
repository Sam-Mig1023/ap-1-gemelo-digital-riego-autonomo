import React, { useState } from 'react';
import { 
  Sliders, 
  Play, 
  TrendingDown, 
  TrendingUp, 
  Droplet, 
  Sun, 
  CloudRain, 
  AlertTriangle,
  Sparkles,
  BarChart2
} from 'lucide-react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  Legend, 
  ReferenceLine 
} from 'recharts';
import { ManagementZone, WhatIfScenarioInput } from '../types';
import { runWhatIfScenario } from '../services/digitalTwinEngine';
import { useLanguage } from '../contexts/LanguageContext';

interface WhatIfSimulatorProps {
  zones: ManagementZone[];
  selectedZone: ManagementZone;
  onSelectZone: (zone: ManagementZone) => void;
}

export const WhatIfSimulator: React.FC<WhatIfSimulatorProps> = ({
  zones,
  selectedZone,
  onSelectZone
}) => {
  const { t } = useLanguage();
  const [irrigationMm, setIrrigationMm] = useState<number>(10.0);
  const [rainFactor, setRainFactor] = useState<number>(1.0);
  const [heatWaveDegC, setHeatWaveDegC] = useState<number>(2.0);
  const [horizonDays, setHorizonDays] = useState<number>(7);

  const scenarioInput: WhatIfScenarioInput = {
    targetZoneId: selectedZone.id,
    irrigationActionMm: irrigationMm,
    forecastRainFactor: rainFactor,
    heatWaveScenarioDegC: heatWaveDegC,
    horizonDays
  };

  const simulationResults = runWhatIfScenario(selectedZone, scenarioInput);

  // Maximum stress day and cumulative yield impact
  const maxStressDay = simulationResults.reduce((prev, curr) => curr.cwsi > prev.cwsi ? curr : prev, simulationResults[0]);
  const totalYieldImpact = simulationResults[simulationResults.length - 1]?.estimatedYieldImpactPct || 0;
  const totalDrainageLoss = simulationResults.reduce((acc, r) => acc + r.drainageLossMm, 0);

  return (
    <div className="space-y-6">
      
      {/* Top Banner */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-4 sm:p-5 rounded-2xl flex flex-wrap items-center justify-between gap-4 shadow-xl">
        <div className="flex items-center gap-3.5">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-indigo-700 flex items-center justify-center shadow-lg shadow-purple-950/50 border border-purple-400/40">
            <Sliders className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white tracking-tight">
              {t('whatIf.title')}
            </h2>
            <p className="text-xs text-slate-600 dark:text-slate-400 mt-0.5">
              {t('whatIf.subtitle')}
            </p>
          </div>
        </div>

        {/* Zone Selector */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-600 dark:text-slate-400 font-medium">{t('whatIf.targetZone')}</span>
          <select
            value={selectedZone.id}
            onChange={(e) => {
              const z = zones.find(item => item.id === e.target.value);
              if (z) onSelectZone(z);
            }}
            className="bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg px-3 py-1.5 text-xs font-semibold text-slate-900 dark:text-white focus:outline-none focus:border-purple-500"
          >
            {zones.map((z) => (
              <option key={z.id} value={z.id}>
                {z.name} ({z.soilTexture})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Control Sliders & Scenario Config */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        
        {/* Slider 1: Simulated Irrigation */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-4 rounded-xl space-y-2 shadow-md">
          <div className="flex justify-between items-center text-xs">
            <span className="text-slate-700 dark:text-slate-300 font-semibold flex items-center gap-1.5">
              <Droplet className="w-3.5 h-3.5 text-blue-400" />
              {t('whatIf.sliders.irrigation')}
            </span>
            <span className="font-mono font-bold text-blue-400 text-sm">{irrigationMm} mm</span>
          </div>
          <input
            type="range"
            min="0"
            max="30"
            step="1"
            value={irrigationMm}
            onChange={(e) => setIrrigationMm(parseFloat(e.target.value))}
            className="w-full accent-blue-500 cursor-pointer"
          />
          <p className="text-[10px] text-slate-600 dark:text-slate-400">{t('whatIf.sliders.irrigationHint')}</p>
        </div>

        {/* Slider 2: Rain Factor */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-4 rounded-xl space-y-2 shadow-md">
          <div className="flex justify-between items-center text-xs">
            <span className="text-slate-700 dark:text-slate-300 font-semibold flex items-center gap-1.5">
              <CloudRain className="w-3.5 h-3.5 text-purple-400" />
              {t('whatIf.sliders.rainFactor')}
            </span>
            <span className="font-mono font-bold text-purple-400 text-sm">{rainFactor}x</span>
          </div>
          <input
            type="range"
            min="0"
            max="2.0"
            step="0.2"
            value={rainFactor}
            onChange={(e) => setRainFactor(parseFloat(e.target.value))}
            className="w-full accent-purple-500 cursor-pointer"
          />
          <p className="text-[10px] text-slate-600 dark:text-slate-400">{t('whatIf.sliders.rainHint')}</p>
        </div>

        {/* Slider 3: Heatwave anomaly */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-4 rounded-xl space-y-2 shadow-md">
          <div className="flex justify-between items-center text-xs">
            <span className="text-slate-700 dark:text-slate-300 font-semibold flex items-center gap-1.5">
              <Sun className="w-3.5 h-3.5 text-amber-400" />
              {t('whatIf.sliders.heatWave')}
            </span>
            <span className="font-mono font-bold text-amber-400 text-sm">+{heatWaveDegC}°C</span>
          </div>
          <input
            type="range"
            min="0"
            max="8"
            step="0.5"
            value={heatWaveDegC}
            onChange={(e) => setHeatWaveDegC(parseFloat(e.target.value))}
            className="w-full accent-amber-500 cursor-pointer"
          />
          <p className="text-[10px] text-slate-600 dark:text-slate-400">{t('whatIf.sliders.heatHint')}</p>
        </div>

        {/* Slider 4: Horizon days */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-4 rounded-xl space-y-2 shadow-md">
          <div className="flex justify-between items-center text-xs">
            <span className="text-slate-700 dark:text-slate-300 font-semibold flex items-center gap-1.5">
              <BarChart2 className="w-3.5 h-3.5 text-emerald-400" />
              {t('whatIf.sliders.horizon')}
            </span>
            <span className="font-mono font-bold text-emerald-400 text-sm">{horizonDays} días</span>
          </div>
          <input
            type="range"
            min="3"
            max="14"
            step="1"
            value={horizonDays}
            onChange={(e) => setHorizonDays(parseInt(e.target.value))}
            className="w-full accent-emerald-500 cursor-pointer"
          />
          <p className="text-[10px] text-slate-600 dark:text-slate-400">{t('whatIf.sliders.horizonHint')}</p>
        </div>

      </div>

      {/* Outcome Cards Deck */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-4 rounded-xl space-y-1">
          <span className="text-xs text-slate-600 dark:text-slate-400 font-medium">{t('whatIf.outcomes.maxStress')}</span>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-slate-900 dark:text-white">{maxStressDay.cwsi}</span>
            <span className={`text-xs font-semibold px-2 py-0.5 rounded ${
              maxStressDay.cwsi > 0.5 ? 'bg-rose-500/20 text-rose-300' : 'bg-emerald-500/20 text-emerald-300'
            }`}>
              {t('whatIf.outcomes.onDay', { day: maxStressDay.dayIndex, date: maxStressDay.date })}
            </span>
          </div>
        </div>

        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-4 rounded-xl space-y-1">
          <span className="text-xs text-slate-600 dark:text-slate-400 font-medium">{t('whatIf.outcomes.yieldImpact')}</span>
          <div className="flex items-baseline gap-2">
            <span className={`text-2xl font-bold font-mono ${totalYieldImpact > 4 ? 'text-rose-400' : 'text-emerald-400'}`}>
              -{totalYieldImpact}%
            </span>
            <span className="text-xs text-slate-600 dark:text-slate-400 font-medium">{t('whatIf.outcomes.kyModel')}</span>
          </div>
        </div>

        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-4 rounded-xl space-y-1">
          <span className="text-xs text-slate-600 dark:text-slate-400 font-medium">{t('whatIf.outcomes.drainageLoss')}</span>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-blue-400">{totalDrainageLoss.toFixed(1)} mm</span>
            <span className="text-xs text-slate-600 dark:text-slate-400 font-medium">{t('whatIf.outcomes.overFc')}</span>
          </div>
        </div>

      </div>

      {/* Forward Simulation Chart */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-4 sm:p-5 rounded-2xl space-y-4 shadow-xl">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-purple-400" />
            {t('whatIf.curve.title')}
          </h3>
          <span className="text-xs text-slate-600 dark:text-slate-400 font-mono">{t('whatIf.curve.model')}</span>
        </div>

        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={simulationResults} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="date" stroke="#64748b" fontSize={10} />
              <YAxis stroke="#64748b" fontSize={10} domain={[0, 40]} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.5rem', fontSize: '11px' }} 
                itemStyle={{ color: '#e2e8f0' }}
              />
              <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />

              <ReferenceLine y={selectedZone.fieldCapacity * 100} label={{ value: t('telemetry.fieldCap'), fill: '#10b981', fontSize: 10 }} stroke="#10b981" strokeDasharray="3 3" />
              <ReferenceLine y={selectedZone.wiltingPoint * 100} label={{ value: t('telemetry.wiltingPoint'), fill: '#ef4444', fontSize: 10 }} stroke="#ef4444" strokeDasharray="3 3" />

              <Line type="monotone" dataKey="moistureTopLayer" name={t('whatIf.curve.moistureTop')} stroke="#38bdf8" strokeWidth={2.5} />
              <Line type="monotone" dataKey="moistureDeepLayer" name={t('whatIf.curve.moistureDeep')} stroke="#818cf8" strokeWidth={2} />
              <Line type="monotone" dataKey="etcMm" name={t('whatIf.curve.etcDaily')} stroke="#f59e0b" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

    </div>
  );
};
