import React, { useState, useEffect } from 'react';
import { 
  Layers, 
  Eye, 
  Zap, 
  Droplets, 
  CloudRain, 
  Thermometer, 
  MapPin, 
  Sparkles, 
  Gauge, 
  AlertTriangle,
  Play,
  RotateCw,
  Info
} from 'lucide-react';
import { 
  AgriculturalField, 
  ManagementZone, 
  SensorTelemetry, 
  WeatherRadarCell, 
  RLDecision 
} from '../types';

interface FieldGISMapProps {
  field: AgriculturalField;
  zones: ManagementZone[];
  sensors: SensorTelemetry[];
  radarCells: WeatherRadarCell[];
  decisions: RLDecision[];
  selectedZone: ManagementZone | null;
  onSelectZone: (zone: ManagementZone) => void;
  onTriggerIrrigation: (zoneId: string, depthMm: number) => void;
  systemMode: string;
}

type MapLayerMode = 'cwsi' | 'moisture' | 'radar' | 'soil_texture' | 'vri_rate';

export const FieldGISMap: React.FC<FieldGISMapProps> = ({
  field,
  zones,
  sensors,
  radarCells,
  decisions,
  selectedZone,
  onSelectZone,
  onTriggerIrrigation,
  systemMode
}) => {
  const [activeLayer, setActiveLayer] = useState<MapLayerMode>('cwsi');
  const [pivotAngle, setPivotAngle] = useState<number>(45);
  const [isPivotRotating, setIsPivotRotating] = useState<boolean>(true);
  const [hoveredZoneId, setHoveredZoneId] = useState<string | null>(null);

  // Pivot Arm Rotation simulation
  useEffect(() => {
    if (!isPivotRotating) return;
    const interval = setInterval(() => {
      setPivotAngle((prev) => (prev + 1.5) % 360);
    }, 120);
    return () => clearInterval(interval);
  }, [isPivotRotating]);

  const getZoneFillColor = (zone: ManagementZone) => {
    switch (activeLayer) {
      case 'cwsi':
        if (zone.cwsi > 0.65) return 'rgba(239, 68, 68, 0.75)'; // Red severe stress
        if (zone.cwsi > 0.40) return 'rgba(245, 158, 11, 0.70)'; // Amber moderate stress
        if (zone.cwsi > 0.20) return 'rgba(16, 185, 129, 0.65)'; // Emerald optimal
        return 'rgba(6, 182, 212, 0.65)'; // Cyan high water

      case 'moisture':
        // Based on % moisture
        if (zone.currentMoisture10cm < 14) return 'rgba(239, 68, 68, 0.75)';
        if (zone.currentMoisture10cm < 20) return 'rgba(245, 158, 11, 0.70)';
        if (zone.currentMoisture10cm < 28) return 'rgba(16, 185, 129, 0.70)';
        return 'rgba(59, 130, 246, 0.75)';

      case 'radar':
        // Reflectivity radar cell correlation
        return 'rgba(147, 51, 234, 0.60)';

      case 'soil_texture':
        if (zone.soilTexture === 'sandy_loam') return 'rgba(217, 119, 6, 0.70)'; // Sand amber
        if (zone.soilTexture === 'silt_loam') return 'rgba(13, 148, 136, 0.70)';  // Silt teal
        return 'rgba(180, 83, 9, 0.70)'; // Clay brown

      case 'vri_rate':
        if (zone.recommendedRateMm > 10) return 'rgba(37, 99, 235, 0.85)';
        if (zone.recommendedRateMm > 5) return 'rgba(59, 130, 246, 0.70)';
        if (zone.recommendedRateMm > 0) return 'rgba(147, 197, 253, 0.60)';
        return 'rgba(100, 116, 139, 0.40)';
    }
  };

  // Average CWSI across field
  const avgCwsi = Number((zones.reduce((acc, z) => acc + z.cwsi, 0) / zones.length).toFixed(2));
  const totalWaterDemandM3 = zones.reduce((acc, z) => acc + Math.round((z.recommendedRateMm / 1000) * z.areaHectares * 10000), 0);

  return (
    <div className="space-y-4">
      {/* Top KPI Metrics Deck */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
        
        <div className="bg-slate-900/90 border border-slate-800 p-3.5 rounded-xl">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-medium">Estrés Hídrico (CWSI)</span>
            <Thermometer className={`w-4 h-4 ${avgCwsi > 0.45 ? 'text-amber-400' : 'text-emerald-400'}`} />
          </div>
          <div className="mt-1 flex items-baseline gap-2">
            <span className="text-xl sm:text-2xl font-bold text-white">{avgCwsi}</span>
            <span className={`text-[11px] font-semibold px-1.5 py-0.5 rounded ${
              avgCwsi > 0.45 ? 'bg-amber-500/20 text-amber-300' : 'bg-emerald-500/20 text-emerald-300'
            }`}>
              {avgCwsi > 0.45 ? 'Estrés Moderado' : 'Óptimo'}
            </span>
          </div>
          <div className="mt-1.5 w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
            <div 
              className={`h-full rounded-full ${avgCwsi > 0.45 ? 'bg-amber-500' : 'bg-emerald-500'}`} 
              style={{ width: `${Math.min(100, avgCwsi * 100)}%` }}
            />
          </div>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 p-3.5 rounded-xl">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-medium">Demanda VRI (RL)</span>
            <Droplets className="w-4 h-4 text-blue-400" />
          </div>
          <div className="mt-1 flex items-baseline gap-2">
            <span className="text-xl sm:text-2xl font-bold text-blue-400">{totalWaterDemandM3.toLocaleString()}</span>
            <span className="text-xs text-slate-400 font-medium">m³ neto</span>
          </div>
          <p className="text-[11px] text-slate-400 mt-1">4 zonas de manejo activas</p>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 p-3.5 rounded-xl">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-medium">Ahorro Hídrico Temporada</span>
            <Sparkles className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="mt-1 flex items-baseline gap-2">
            <span className="text-xl sm:text-2xl font-bold text-emerald-400">{field.waterSavedM3Season.toLocaleString()}</span>
            <span className="text-xs text-slate-400 font-medium">m³ (-28.4%)</span>
          </div>
          <p className="text-[11px] text-emerald-400/80 mt-1">Vs. Riego por calendario tradicional</p>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 p-3.5 rounded-xl">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-medium">Ahorro Energía Bombeo</span>
            <Zap className="w-4 h-4 text-amber-400" />
          </div>
          <div className="mt-1 flex items-baseline gap-2">
            <span className="text-xl sm:text-2xl font-bold text-amber-400">{field.energySavedKwhSeason.toLocaleString()}</span>
            <span className="text-xs text-slate-400 font-medium">kWh</span>
          </div>
          <p className="text-[11px] text-slate-400 mt-1">Tarifa optimizada en horario valle</p>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 p-3.5 rounded-xl col-span-2 sm:col-span-1">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-medium">Radar Lluvia Prevista 24h</span>
            <CloudRain className="w-4 h-4 text-purple-400" />
          </div>
          <div className="mt-1 flex items-baseline gap-2">
            <span className="text-xl sm:text-2xl font-bold text-purple-300">3.4 mm</span>
            <span className="text-xs text-purple-400 font-semibold">22 dBZ</span>
          </div>
          <p className="text-[11px] text-slate-400 mt-1">Descontado automáticamente por RL</p>
        </div>

      </div>

      {/* Main Map Canvas and Control Header */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl">
        
        {/* Map Control Bar */}
        <div className="bg-slate-950/80 border-b border-slate-800 p-3 sm:p-4 flex flex-wrap items-center justify-between gap-3">
          
          {/* Layer Selector */}
          <div className="flex items-center gap-1.5 flex-wrap">
            <span className="text-xs font-semibold text-slate-400 mr-1 flex items-center gap-1">
              <Layers className="w-3.5 h-3.5 text-emerald-400" />
              Capa Visual:
            </span>

            {[
              { id: 'cwsi', label: 'Estrés CWSI (Termografía)', color: 'text-red-400' },
              { id: 'moisture', label: 'Humedad Suelo (10-30cm)', color: 'text-blue-400' },
              { id: 'vri_rate', label: 'Dosis Recomendada RL (mm)', color: 'text-emerald-400' },
              { id: 'radar', label: 'Radar Meteorológico (dBZ)', color: 'text-purple-400' },
              { id: 'soil_texture', label: 'Textura & Hidráulica', color: 'text-amber-400' },
            ].map((layer) => (
              <button
                key={layer.id}
                id={`map-layer-${layer.id}`}
                onClick={() => setActiveLayer(layer.id as MapLayerMode)}
                className={`px-2.5 py-1 text-xs font-medium rounded-lg border transition-all ${
                  activeLayer === layer.id
                    ? 'bg-slate-800 text-white border-emerald-500/50 shadow-sm font-semibold'
                    : 'bg-slate-900/60 text-slate-400 border-slate-800 hover:border-slate-700 hover:text-slate-200'
                }`}
              >
                {layer.label}
              </button>
            ))}
          </div>

          {/* Pivot Animation Controls */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsPivotRotating(!isPivotRotating)}
              className="flex items-center gap-1 px-2.5 py-1 text-xs font-medium rounded-lg bg-slate-800 text-slate-300 hover:text-white border border-slate-700 transition-all"
            >
              <RotateCw className={`w-3 h-3 ${isPivotRotating ? 'animate-spin' : ''}`} />
              <span>{isPivotRotating ? 'Pausar Pivot' : 'Girar Pivot'}</span>
            </button>
          </div>

        </div>

        {/* Map Grid Container with Interactive SVG */}
        <div className="relative p-4 sm:p-6 bg-radial from-slate-900 via-slate-950 to-slate-950 flex flex-col lg:flex-row gap-6 items-center justify-between">
          
          {/* Geospatial Canvas SVG */}
          <div className="relative w-full max-w-xl aspect-square bg-slate-950/90 rounded-2xl border border-slate-800 p-2 shadow-inner flex items-center justify-center overflow-hidden">
            
            {/* Background Map Grid Pattern */}
            <div className="absolute inset-0 opacity-10 bg-[linear-gradient(to_right,#10b981_1px,transparent_1px),linear-gradient(to_bottom,#10b981_1px,transparent_1px)] bg-[size:24px_24px]" />

            <svg viewBox="0 0 500 500" className="w-full h-full">
              <defs>
                {/* Sector Clip & Gradients */}
                <radialGradient id="radarScanGradient" cx="50%" cy="50%" r="50%">
                  <stop offset="0%" stopColor="#9333ea" stopOpacity="0.45" />
                  <stop offset="60%" stopColor="#c084fc" stopOpacity="0.25" />
                  <stop offset="100%" stopColor="#3b82f6" stopOpacity="0.0" />
                </radialGradient>

                <filter id="glowEffect">
                  <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                  <feMerge>
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                  </feMerge>
                </filter>
              </defs>

              {/* Field Circle Perimeter (Center Pivot Radius 400m = 200 SVG radius) */}
              <circle cx="250" cy="250" r="220" fill="none" stroke="#334155" strokeWidth="2" strokeDasharray="4 4" />
              <circle cx="250" cy="250" r="160" fill="none" stroke="#1e293b" strokeWidth="1.5" />
              <circle cx="250" cy="250" r="100" fill="none" stroke="#1e293b" strokeWidth="1.5" />

              {/* 4 Quadrants Management Zones */}
              {/* Zone 1: NW (Top Left) */}
              <path
                d="M 250 250 L 50 250 A 200 200 0 0 1 250 50 Z"
                fill={getZoneFillColor(zones[0])}
                stroke={selectedZone?.id === zones[0].id ? '#10b981' : '#475569'}
                strokeWidth={selectedZone?.id === zones[0].id ? 3 : 1.5}
                className="cursor-pointer transition-all hover:opacity-90"
                onClick={() => onSelectZone(zones[0])}
                onMouseEnter={() => setHoveredZoneId(zones[0].id)}
                onMouseLeave={() => setHoveredZoneId(null)}
              />

              {/* Zone 2: NE (Top Right) */}
              <path
                d="M 250 250 L 250 50 A 200 200 0 0 1 450 250 Z"
                fill={getZoneFillColor(zones[1])}
                stroke={selectedZone?.id === zones[1].id ? '#10b981' : '#475569'}
                strokeWidth={selectedZone?.id === zones[1].id ? 3 : 1.5}
                className="cursor-pointer transition-all hover:opacity-90"
                onClick={() => onSelectZone(zones[1])}
                onMouseEnter={() => setHoveredZoneId(zones[1].id)}
                onMouseLeave={() => setHoveredZoneId(null)}
              />

              {/* Zone 3: SW (Bottom Left) */}
              <path
                d="M 250 250 L 50 250 A 200 200 0 0 0 250 450 Z"
                fill={getZoneFillColor(zones[2])}
                stroke={selectedZone?.id === zones[2].id ? '#10b981' : '#475569'}
                strokeWidth={selectedZone?.id === zones[2].id ? 3 : 1.5}
                className="cursor-pointer transition-all hover:opacity-90"
                onClick={() => onSelectZone(zones[2])}
                onMouseEnter={() => setHoveredZoneId(zones[2].id)}
                onMouseLeave={() => setHoveredZoneId(null)}
              />

              {/* Zone 4: SE (Bottom Right) */}
              <path
                d="M 250 250 L 250 450 A 200 200 0 0 0 450 250 Z"
                fill={getZoneFillColor(zones[3])}
                stroke={selectedZone?.id === zones[3].id ? '#10b981' : '#475569'}
                strokeWidth={selectedZone?.id === zones[3].id ? 3 : 1.5}
                className="cursor-pointer transition-all hover:opacity-90"
                onClick={() => onSelectZone(zones[3])}
                onMouseEnter={() => setHoveredZoneId(zones[3].id)}
                onMouseLeave={() => setHoveredZoneId(null)}
              />

              {/* Weather Radar Storm Overlay (if radar active) */}
              {activeLayer === 'radar' && (
                <g opacity="0.75" className="animate-pulse">
                  <circle cx="340" cy="180" r="110" fill="url(#radarScanGradient)" filter="url(#glowEffect)" />
                  <circle cx="160" cy="320" r="80" fill="url(#radarScanGradient)" filter="url(#glowEffect)" />
                </g>
              )}

              {/* Sector Labels */}
              <text x="160" y="150" fill="#ffffff" fontSize="13" fontWeight="bold" textAnchor="middle">ZONA 1 (NW)</text>
              <text x="160" y="168" fill="#e2e8f0" fontSize="10" textAnchor="middle">H: {zones[0].currentMoisture10cm}% | {zones[0].recommendedRateMm}mm</text>

              <text x="340" y="150" fill="#ffffff" fontSize="13" fontWeight="bold" textAnchor="middle">ZONA 2 (NE)</text>
              <text x="340" y="168" fill="#e2e8f0" fontSize="10" textAnchor="middle">H: {zones[1].currentMoisture10cm}% | {zones[1].recommendedRateMm}mm</text>

              <text x="160" y="340" fill="#ffffff" fontSize="13" fontWeight="bold" textAnchor="middle">ZONA 3 (SW)</text>
              <text x="160" y="358" fill="#e2e8f0" fontSize="10" textAnchor="middle">H: {zones[2].currentMoisture10cm}% | {zones[2].recommendedRateMm}mm</text>

              <text x="340" y="340" fill="#ffffff" fontSize="13" fontWeight="bold" textAnchor="middle">ZONA 4 (SE)</text>
              <text x="340" y="358" fill="#e2e8f0" fontSize="10" textAnchor="middle">H: {zones[3].currentMoisture10cm}% | {zones[3].recommendedRateMm}mm</text>

              {/* Rotating Pivot Arm */}
              <g transform={`rotate(${pivotAngle}, 250, 250)`}>
                {/* Pivot Truss Line */}
                <line x1="250" y1="250" x2="450" y2="250" stroke="#38bdf8" strokeWidth="4" strokeLinecap="round" />
                <line x1="250" y1="250" x2="450" y2="250" stroke="#ffffff" strokeWidth="1.5" />
                
                {/* Spray droplet emitters along the pivot */}
                {[290, 330, 370, 410, 445].map((pos, i) => (
                  <g key={i}>
                    <circle cx={pos} cy="250" r="3.5" fill="#38bdf8" />
                    <circle cx={pos} cy="256" r="2" fill="#0284c7" opacity="0.8" className="animate-ping" />
                  </g>
                ))}
              </g>

              {/* Pivot Center Tower Hub */}
              <circle cx="250" cy="250" r="9" fill="#0284c7" stroke="#ffffff" strokeWidth="2.5" />

              {/* Sensor Markers */}
              {sensors.map((s, idx) => {
                // Map sensor coords to relative SVG positions
                const posMap: Record<string, { cx: number; cy: number }> = {
                  'sn-01': { cx: 170, cy: 190 },
                  'sn-02': { cx: 130, cy: 130 },
                  'sn-03': { cx: 330, cy: 190 },
                  'sn-04': { cx: 170, cy: 310 },
                  'sn-05': { cx: 330, cy: 310 },
                  'sn-06': { cx: 370, cy: 370 },
                  'sn-07': { cx: 250, cy: 250 }
                };
                const pos = posMap[s.id] || { cx: 250, cy: 250 };
                
                return (
                  <g key={s.id} className="cursor-pointer group">
                    <circle 
                      cx={pos.cx} 
                      cy={pos.cy} 
                      r="6.5" 
                      fill={s.sensorType.includes('irt') ? '#f59e0b' : '#10b981'} 
                      stroke="#ffffff" 
                      strokeWidth="1.5" 
                    />
                    <circle cx={pos.cx} cy={pos.cy} r="10" fill="none" stroke={s.sensorType.includes('irt') ? '#f59e0b' : '#10b981'} strokeWidth="1" opacity="0.6" className="animate-pulse" />
                  </g>
                );
              })}

            </svg>

            {/* Pivot Status Overlay Tag */}
            <div className="absolute bottom-3 left-3 bg-slate-900/90 backdrop-blur-md px-2.5 py-1 rounded-lg border border-slate-800 text-[11px] text-slate-300 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
              <span>Pivot Central: Sector {Math.floor(pivotAngle / 45) + 1} ({Math.round(pivotAngle)}°)</span>
            </div>

          </div>

          {/* Right Side: Selected Zone Profile & Control Panel */}
          <div className="w-full lg:w-96 space-y-3">
            {selectedZone ? (
              <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-4">
                
                {/* Zone Title & Status */}
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-bold text-white">{selectedZone.name}</h3>
                    <p className="text-xs text-slate-400 capitalize">Textura: {selectedZone.soilTexture.replace('_', ' ')} • {selectedZone.areaHectares} Ha</p>
                  </div>
                  <span className={`text-[11px] font-semibold px-2 py-0.5 rounded border ${
                    selectedZone.status === 'severe_stress'
                      ? 'bg-rose-500/20 text-rose-300 border-rose-500/40'
                      : selectedZone.status === 'mild_stress'
                      ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                      : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                  }`}>
                    {selectedZone.status === 'severe_stress' ? 'Estrés Severo' : selectedZone.status === 'mild_stress' ? 'Estrés Leve' : 'Óptimo'}
                  </span>
                </div>

                {/* Soil Profile Multi-depth Readout */}
                <div className="space-y-2 bg-slate-900/80 p-3 rounded-lg border border-slate-800">
                  <div className="text-xs font-semibold text-slate-300 flex items-center justify-between">
                    <span>Humedad Volumétrica (Sondas TDR)</span>
                    <span className="text-[10px] text-slate-400">CC: {(selectedZone.fieldCapacity * 100).toFixed(0)}% | PMP: {(selectedZone.wiltingPoint * 100).toFixed(0)}%</span>
                  </div>
                  
                  <div className="space-y-1.5 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400">Horizonte 10cm (Superficial):</span>
                      <span className="font-mono font-bold text-white">{selectedZone.currentMoisture10cm}%</span>
                    </div>
                    <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                      <div className="bg-blue-500 h-full rounded-full" style={{ width: `${Math.min(100, selectedZone.currentMoisture10cm * 2.5)}%` }} />
                    </div>

                    <div className="flex items-center justify-between">
                      <span className="text-slate-400">Horizonte 30cm (Bulbo radicular):</span>
                      <span className="font-mono font-bold text-white">{selectedZone.currentMoisture30cm}%</span>
                    </div>
                    <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                      <div className="bg-blue-600 h-full rounded-full" style={{ width: `${Math.min(100, selectedZone.currentMoisture30cm * 2.5)}%` }} />
                    </div>

                    <div className="flex items-center justify-between">
                      <span className="text-slate-400">Horizonte 60cm (Subsuelo):</span>
                      <span className="font-mono font-bold text-white">{selectedZone.currentMoisture60cm}%</span>
                    </div>
                    <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                      <div className="bg-blue-700 h-full rounded-full" style={{ width: `${Math.min(100, selectedZone.currentMoisture60cm * 2.5)}%` }} />
                    </div>
                  </div>
                </div>

                {/* Thermal & Physical Parameters */}
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="bg-slate-900/60 p-2.5 rounded-lg border border-slate-800/80">
                    <span className="text-slate-400 block text-[11px]">Temp Dosel IRT:</span>
                    <span className="text-sm font-bold text-amber-300">{selectedZone.currentCanopyTemp}°C</span>
                    <span className="text-[10px] text-slate-500 block">Amb: {selectedZone.ambientTemp}°C</span>
                  </div>
                  <div className="bg-slate-900/60 p-2.5 rounded-lg border border-slate-800/80">
                    <span className="text-slate-400 block text-[11px]">Conductividad Ksat:</span>
                    <span className="text-sm font-bold text-teal-300">{selectedZone.saturatedK} mm/h</span>
                    <span className="text-[10px] text-slate-500 block">Green-Ampt</span>
                  </div>
                </div>

                {/* RL Recommendation Action Card */}
                <div className="bg-gradient-to-br from-emerald-950/40 to-slate-900 p-3.5 rounded-xl border border-emerald-500/30 space-y-2.5">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-emerald-400 flex items-center gap-1">
                      <Zap className="w-3.5 h-3.5" />
                      Prescripción PPO RL:
                    </span>
                    <span className="text-xs font-mono font-bold text-white bg-emerald-500/20 px-2 py-0.5 rounded border border-emerald-500/40">
                      {selectedZone.recommendedRateMm} mm
                    </span>
                  </div>
                  
                  <p className="text-[11px] text-slate-300">
                    Volumen prescrito: <strong className="text-white font-mono">{Math.round((selectedZone.recommendedRateMm / 1000) * selectedZone.areaHectares * 10000)} m³</strong> para {selectedZone.areaHectares} Ha.
                  </p>

                  <button
                    id="execute-zone-irrigation-btn"
                    onClick={() => onTriggerIrrigation(selectedZone.id, selectedZone.recommendedRateMm)}
                    className="w-full py-2 px-3 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-xs flex items-center justify-center gap-1.5 transition-all shadow-md shadow-emerald-950/40"
                  >
                    <Play className="w-3.5 h-3.5" />
                    <span>Aplicar Dosis VRI ({selectedZone.recommendedRateMm} mm)</span>
                  </button>
                </div>

              </div>
            ) : (
              <div className="bg-slate-950 p-6 rounded-xl border border-slate-800 text-center space-y-2">
                <Info className="w-8 h-8 text-slate-500 mx-auto" />
                <p className="text-xs font-medium text-slate-300">Selecciona una zona en el mapa GIS</p>
                <p className="text-[11px] text-slate-500">Haz clic sobre cualquier cuadrante del pivot para ver su perfil hidráulico, sensores IRT y recomendación RL.</p>
              </div>
            )}
          </div>

        </div>

      </div>

    </div>
  );
};
