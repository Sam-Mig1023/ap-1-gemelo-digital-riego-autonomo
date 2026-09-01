import React, { useState } from 'react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  Legend, 
  ReferenceLine,
  AreaChart,
  Area
} from 'recharts';
import { 
  Activity, 
  Thermometer, 
  CloudRain, 
  AlertTriangle, 
  CheckCircle2, 
  ShieldAlert, 
  Radio,
  Clock
} from 'lucide-react';
import { SensorTelemetry, ManagementZone } from '../types';
import { evaluateSensorAnomalies } from '../services/anomalyDetectionEngine';

interface TelemetryAnalyticsProps {
  sensors: SensorTelemetry[];
  zones: ManagementZone[];
  selectedZone: ManagementZone;
}

export const TelemetryAnalytics: React.FC<TelemetryAnalyticsProps> = ({
  sensors,
  zones,
  selectedZone
}) => {
  const [timeRange, setTimeRange] = useState<'24h' | '7d' | '30d'>('24h');

  // Synthetic timeseries data generator for selected zone
  const generateMoistureTimeseries = () => {
    const data = [];
    const baseDate = new Date();
    for (let i = 24; i >= 0; i--) {
      const time = new Date(baseDate.getTime() - i * 3600 * 1000);
      const timeStr = time.toLocaleTimeString('es-PE', { hour: '2-digit', minute: '2-digit' });
      
      // Diurnal cycle
      const hour = time.getHours();
      const tempVariation = Math.sin((hour - 8) * (Math.PI / 12)) * 4.5;
      const airTemp = Number((24.0 + tempVariation).toFixed(1));
      const canopyTemp = Number((airTemp + (selectedZone.cwsi > 0.4 ? 3.8 : -1.2)).toFixed(1));
      
      const moisture10 = Number((selectedZone.currentMoisture10cm + Math.sin(i * 0.3) * 0.8).toFixed(1));
      const moisture30 = Number((selectedZone.currentMoisture30cm + Math.sin(i * 0.2) * 0.5).toFixed(1));
      const moisture60 = Number((selectedZone.currentMoisture60cm + Math.sin(i * 0.1) * 0.3).toFixed(1));

      data.push({
        time: timeStr,
        moisture10cm: moisture10,
        moisture30cm: moisture30,
        moisture60cm: moisture60,
        fieldCapacity: Number((selectedZone.fieldCapacity * 100).toFixed(1)),
        wiltingPoint: Number((selectedZone.wiltingPoint * 100).toFixed(1)),
        airTemp,
        canopyTemp,
        cwsi: selectedZone.cwsi,
        etcMm: Number((0.2 + Math.max(0, tempVariation * 0.08)).toFixed(2))
      });
    }
    return data;
  };

  const timeseriesData = generateMoistureTimeseries();

  return (
    <div className="space-y-6">
      
      {/* Header Bar */}
      <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl flex flex-wrap items-center justify-between gap-3 shadow-lg">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-blue-500/20 text-blue-400 border border-blue-500/30 flex items-center justify-center">
            <Activity className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white">Telemetría de Sensores & Series Temporales TimescaleDB</h2>
            <p className="text-xs text-slate-400">
              Datos transmitidos cada 15 min vía LoRaWAN/NB-IoT • Zona activa: <strong className="text-white">{selectedZone.name}</strong>
            </p>
          </div>
        </div>

        {/* Time Range Selector */}
        <div className="flex items-center bg-slate-950 p-1 rounded-lg border border-slate-800 text-xs">
          {(['24h', '7d', '30d'] as const).map((r) => (
            <button
              key={r}
              onClick={() => setTimeRange(r)}
              className={`px-3 py-1 font-medium rounded transition-all ${
                timeRange === r
                  ? 'bg-blue-600 text-white font-semibold shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {r.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Main Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Chart 1: Multi-depth Soil Moisture Dynamics */}
        <div className="bg-slate-900 border border-slate-800 p-4 sm:p-5 rounded-2xl space-y-3 shadow-xl">
          <div className="flex items-center justify-between">
            <h3 className="text-xs sm:text-sm font-bold text-white flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-blue-400" />
              Dinámica de Humedad Volumétrica Multiprofundidad (%)
            </h3>
            <span className="text-[10px] text-slate-400 font-mono">Sondas TDR / FDR</span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={timeseriesData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="time" stroke="#64748b" fontSize={10} />
                <YAxis stroke="#64748b" fontSize={10} domain={[5, 45]} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.5rem', fontSize: '11px' }} 
                  itemStyle={{ color: '#e2e8f0' }}
                />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
                
                {/* Reference thresholds */}
                <ReferenceLine y={selectedZone.fieldCapacity * 100} label={{ value: 'Cap. Campo', fill: '#10b981', fontSize: 10 }} stroke="#10b981" strokeDasharray="4 4" />
                <ReferenceLine y={selectedZone.wiltingPoint * 100} label={{ value: 'P. Marchitez', fill: '#ef4444', fontSize: 10 }} stroke="#ef4444" strokeDasharray="4 4" />

                <Line type="monotone" dataKey="moisture10cm" name="Estrato 10cm" stroke="#38bdf8" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="moisture30cm" name="Estrato 30cm (Raíz)" stroke="#3b82f6" strokeWidth={2.5} dot={false} />
                <Line type="monotone" dataKey="moisture60cm" name="Estrato 60cm" stroke="#1d4ed8" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 2: Canopy Thermal IRT vs Ambient Temp & CWSI */}
        <div className="bg-slate-900 border border-slate-800 p-4 sm:p-5 rounded-2xl space-y-3 shadow-xl">
          <div className="flex items-center justify-between">
            <h3 className="text-xs sm:text-sm font-bold text-white flex items-center gap-2">
              <Thermometer className="w-4 h-4 text-amber-400" />
              Termografía Infrarroja de Dosel (IRT) vs Aire (°C)
            </h3>
            <span className="text-[10px] text-amber-400 font-mono">CWSI: {selectedZone.cwsi}</span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={timeseriesData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="canopyGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#f59e0b" stopOpacity={0.0}/>
                  </linearGradient>
                  <linearGradient id="airGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#06b6d4" stopOpacity={0.0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="time" stroke="#64748b" fontSize={10} />
                <YAxis stroke="#64748b" fontSize={10} domain={[15, 38]} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.5rem', fontSize: '11px' }} 
                  itemStyle={{ color: '#e2e8f0' }}
                />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />

                <Area type="monotone" dataKey="canopyTemp" name="Temp Dosel IRT (°C)" stroke="#f59e0b" strokeWidth={2} fill="url(#canopyGrad)" />
                <Area type="monotone" dataKey="airTemp" name="Temp Aire Ambiente (°C)" stroke="#06b6d4" strokeWidth={2} fill="url(#airGrad)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>

      {/* Telemetry Stream Ingestion Table & Anomaly Detector */}
      <div className="bg-slate-900 border border-slate-800 p-4 sm:p-5 rounded-2xl space-y-4 shadow-xl">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-3">
          <div className="flex items-center gap-2">
            <Radio className="w-4 h-4 text-emerald-400" />
            <h3 className="text-sm font-bold text-white">Transductores Activos & Detector de Anomalías (Isolation Forest)</h3>
          </div>
          <span className="text-xs text-slate-400">
            Filtro de calidad de datos antes de ingresar al buffer del agente RL
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950 text-slate-400 font-semibold border-b border-slate-800">
              <tr>
                <th className="p-3">ID Sensor</th>
                <th className="p-3">Tipo / Transductor</th>
                <th className="p-3">Zona</th>
                <th className="p-3">Última Lectura</th>
                <th className="p-3">Batería & RSSI</th>
                <th className="p-3">Calidad (0-100)</th>
                <th className="p-3">Score Anomalía</th>
                <th className="p-3">Estado RL</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-slate-300">
              {sensors.map((sensor) => {
                const anomalyEval = evaluateSensorAnomalies(sensor);
                const zone = zones.find(z => z.id === sensor.zoneId);

                return (
                  <tr key={sensor.id} className="hover:bg-slate-800/50 transition-colors">
                    <td className="p-3 font-mono font-bold text-white flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-emerald-400" />
                      {sensor.sensorId}
                    </td>
                    <td className="p-3 capitalize text-slate-300">
                      {sensor.sensorType.replace('_', ' ')}
                    </td>
                    <td className="p-3 text-slate-300">{zone?.name.split('(')[0] || sensor.zoneId}</td>
                    <td className="p-3 font-mono text-slate-200">
                      {sensor.readings.volumetricWaterContent_10cm !== undefined
                        ? `10cm: ${sensor.readings.volumetricWaterContent_10cm}% | 30cm: ${sensor.readings.volumetricWaterContent_30cm}%`
                        : sensor.readings.canopyTemperatureC !== undefined
                        ? `Dosel: ${sensor.readings.canopyTemperatureC}°C`
                        : `Amb: ${sensor.readings.ambientAirTempC}°C | Rad: ${sensor.readings.solarRadiationWm2} W/m²`}
                    </td>
                    <td className="p-3 font-mono text-slate-300">
                      {sensor.batteryLevel}% • {sensor.rssi} dBm
                    </td>
                    <td className="p-3">
                      <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-mono font-semibold">
                        {sensor.qualityScore}%
                      </span>
                    </td>
                    <td className="p-3">
                      <span className={`px-2 py-0.5 rounded font-mono font-semibold ${
                        anomalyEval.anomalyScore > 0.6
                          ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                          : 'bg-slate-800 text-slate-400'
                      }`}>
                        {anomalyEval.anomalyScore}
                      </span>
                    </td>
                    <td className="p-3">
                      {anomalyEval.isAnomaly ? (
                        <span className="flex items-center gap-1 text-rose-400 font-semibold text-[11px]">
                          <AlertTriangle className="w-3.5 h-3.5" />
                          Anomalía (Safe Mode)
                        </span>
                      ) : (
                        <span className="flex items-center gap-1 text-emerald-400 font-semibold text-[11px]">
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          Alimentando RL
                        </span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
};
