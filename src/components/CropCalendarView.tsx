import React from 'react';
import { Calendar as CalendarIcon, Leaf, TrendingUp, Sun, Snowflake } from 'lucide-react';
import { ManagementZone } from '../types';

interface CropCalendarViewProps {
  zones: ManagementZone[];
}

export const CropCalendarView: React.FC<CropCalendarViewProps> = ({ zones }) => {
  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center shadow-lg shadow-emerald-500/20">
          <CalendarIcon className="w-6 h-6 text-white" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Calendario Fenológico de Cultivos</h2>
          <p className="text-slate-500 dark:text-slate-400">Visualización de etapas de desarrollo, cálculo de Kc dinámico y fechas clave.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {zones.map((zone) => {
          if (!zone.plantingDate || !zone.harvestDate) return null;
          
          const start = new Date(zone.plantingDate).getTime();
          const end = new Date(zone.harvestDate).getTime();
          const today = new Date().getTime();
          const progress = Math.max(0, Math.min(100, ((today - start) / (end - start)) * 100));
          const flow = zone.floweringDate ? new Date(zone.floweringDate).getTime() : 0;
          const flowPct = flow ? Math.max(0, Math.min(100, ((flow - start) / (end - start)) * 100)) : 50;
          
          return (
            <div key={zone.id} className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm">
              <div className="flex justify-between items-start mb-6">
                <div>
                  <h3 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
                    <Leaf className="w-5 h-5 text-emerald-500" />
                    {zone.cropName || 'Cultivo Desconocido'}
                  </h3>
                  <p className="text-sm text-slate-500">{zone.name}</p>
                </div>
                <div className="text-right">
                  <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 text-sm font-semibold">
                    <TrendingUp className="w-4 h-4" />
                    Kc Actual: {zone.kc || 0.8}
                  </span>
                  <p className="text-xs font-medium text-slate-500 mt-1 capitalize">{zone.cropStage || 'Fase desconocida'}</p>
                </div>
              </div>

              <div className="relative pt-8 pb-4">
                {/* Track */}
                <div className="w-full bg-slate-100 dark:bg-slate-800 h-3 rounded-full relative">
                  {/* Progress Fill */}
                  <div className="absolute top-0 left-0 h-full bg-gradient-to-r from-emerald-400 to-emerald-600 rounded-full" style={{ width: `${progress}%` }}></div>
                  
                  {/* Current Day Marker */}
                  <div className="absolute top-1/2 -translate-y-1/2 w-5 h-5 bg-white border-4 border-emerald-600 rounded-full shadow-md z-10" style={{ left: `calc(${progress}% - 10px)` }}></div>
                  
                  {/* Flowering Marker */}
                  <div className="absolute top-0 h-full w-1 bg-amber-400" style={{ left: `${flowPct}%` }}></div>
                </div>

                {/* Timeline Labels */}
                <div className="flex justify-between mt-3 text-xs font-medium text-slate-500">
                  <div className="flex flex-col items-start">
                    <span className="text-slate-700 dark:text-slate-300">Siembra</span>
                    <span>{zone.plantingDate}</span>
                  </div>
                  
                  <div className="flex flex-col items-center absolute -translate-x-1/2" style={{ left: `${flowPct}%` }}>
                    <span className="text-amber-600 dark:text-amber-400 flex items-center gap-1"><Sun className="w-3 h-3"/> Floración</span>
                    <span>{zone.floweringDate}</span>
                  </div>
                  
                  <div className="flex flex-col items-end">
                    <span className="text-slate-700 dark:text-slate-300">Cosecha</span>
                    <span>{zone.harvestDate}</span>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
