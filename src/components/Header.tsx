import React from 'react';
import { 
  Droplet, 
  Cpu, 
  Wifi, 
  WifiOff, 
  ShieldCheck, 
  User, 
  Activity, 
  Sliders, 
  Layers, 
  RefreshCw,
  Bell
} from 'lucide-react';
import { SystemOperationMode, UserRole, AgriculturalField } from '../types';

interface HeaderProps {
  field: AgriculturalField;
  activeRole: UserRole;
  onRoleChange: (role: UserRole) => void;
  systemMode: SystemOperationMode;
  onSystemModeChange: (mode: SystemOperationMode) => void;
  isOnline: boolean;
  onToggleOnline: () => void;
  offlineQueueCount: number;
  activeTab: string;
  onTabChange: (tab: string) => void;
}

export const Header: React.FC<HeaderProps> = ({
  field,
  activeRole,
  onRoleChange,
  systemMode,
  onSystemModeChange,
  isOnline,
  onToggleOnline,
  offlineQueueCount,
  activeTab,
  onTabChange
}) => {
  const getRoleBadge = (role: UserRole) => {
    switch (role) {
      case 'superadmin':
        return { label: 'Superadmin', color: 'bg-purple-500/20 text-purple-300 border-purple-500/40' };
      case 'agronomist':
        return { label: 'Agrónomo Senior', color: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40' };
      case 'farmer':
        return { label: 'Productor Agrícola', color: 'bg-amber-500/20 text-amber-300 border-amber-500/40' };
      case 'field_technician':
        return { label: 'Técnico de Campo', color: 'bg-blue-500/20 text-blue-300 border-blue-500/40' };
      case 'rl_agent_system':
        return { label: 'RL Agent Autonomous', color: 'bg-rose-500/20 text-rose-300 border-rose-500/40' };
    }
  };

  const currentRoleInfo = getRoleBadge(activeRole);

  return (
    <header className="bg-slate-900 border-b border-slate-800 sticky top-0 z-40 shadow-xl">
      {/* Top Banner */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-3 flex flex-wrap items-center justify-between gap-4">
        
        {/* Brand & Field Info */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-700 flex items-center justify-center shadow-lg shadow-emerald-950/40 border border-emerald-400/30">
            <Droplet className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base sm:text-lg font-bold text-white tracking-tight flex items-center gap-2">
                CLOSED-LOOP DIGITAL TWIN <span className="text-emerald-400">VRI</span>
              </h1>
              <span className="px-2 py-0.5 text-xs font-semibold rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                PPO-RL Core
              </span>
            </div>
            <p className="text-xs text-slate-400 font-medium truncate max-w-md">
              {field.name} • {field.cropName} ({field.cropStage})
            </p>
          </div>
        </div>

        {/* System Controls & State Indicators */}
        <div className="flex flex-wrap items-center gap-2 sm:gap-3">
          
          {/* Operation Mode Selector */}
          <div className="flex items-center bg-slate-950/80 p-1 rounded-lg border border-slate-800">
            <span className="text-xs font-medium text-slate-400 px-2 flex items-center gap-1">
              <Sliders className="w-3.5 h-3.5 text-emerald-400" />
              Modo:
            </span>
            <button
              id="mode-manual-btn"
              onClick={() => onSystemModeChange('manual')}
              className={`px-2.5 py-1 text-xs font-medium rounded transition-all ${
                systemMode === 'manual'
                  ? 'bg-slate-700 text-white shadow-sm font-semibold'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Manual
            </button>
            <button
              id="mode-assisted-btn"
              onClick={() => onSystemModeChange('assisted')}
              className={`px-2.5 py-1 text-xs font-medium rounded transition-all ${
                systemMode === 'assisted'
                  ? 'bg-blue-600 text-white shadow-sm font-semibold'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Asistido
            </button>
            <button
              id="mode-autonomous-btn"
              onClick={() => onSystemModeChange('autonomous')}
              className={`px-2.5 py-1 text-xs font-medium rounded transition-all flex items-center gap-1 ${
                systemMode === 'autonomous'
                  ? 'bg-emerald-600 text-white shadow-sm font-semibold animate-pulse'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Cpu className="w-3 h-3" />
              Autónomo
            </button>
          </div>

          {/* Rural Offline / Online Simulator */}
          <button
            id="toggle-connectivity-btn"
            onClick={onToggleOnline}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-medium transition-all ${
              isOnline
                ? 'bg-slate-950 text-slate-300 border-slate-700 hover:border-slate-600'
                : 'bg-amber-950/40 text-amber-300 border-amber-500/40 hover:bg-amber-900/40'
            }`}
            title={isOnline ? 'Conexión activa con TimescaleDB y Celery' : 'Modo Rural Offline: Datos en cola local'}
          >
            {isOnline ? (
              <>
                <Wifi className="w-3.5 h-3.5 text-emerald-400" />
                <span>Online</span>
              </>
            ) : (
              <>
                <WifiOff className="w-3.5 h-3.5 text-amber-400" />
                <span>Rural Offline ({offlineQueueCount})</span>
              </>
            )}
          </button>

          {/* RBAC Role Switcher */}
          <div className="flex items-center gap-1.5 bg-slate-950/80 px-2.5 py-1 rounded-lg border border-slate-800">
            <User className="w-3.5 h-3.5 text-slate-400" />
            <select
              id="role-selector-dropdown"
              value={activeRole}
              onChange={(e) => onRoleChange(e.target.value as UserRole)}
              className="bg-transparent text-xs font-medium text-slate-200 focus:outline-none cursor-pointer pr-1"
            >
              <option value="superadmin" className="bg-slate-900 text-white">Superadmin (Global)</option>
              <option value="agronomist" className="bg-slate-900 text-white">Agrónomo Senior (Aprobador)</option>
              <option value="farmer" className="bg-slate-900 text-white">Productor Agrícola (Fundo)</option>
              <option value="field_technician" className="bg-slate-900 text-white">Técnico de Campo (IoT)</option>
              <option value="rl_agent_system" className="bg-slate-900 text-white">RL Agent (System Core)</option>
            </select>
            <span className={`px-1.5 py-0.5 text-[10px] font-semibold rounded border ${currentRoleInfo.color}`}>
              {currentRoleInfo.label}
            </span>
          </div>

        </div>
      </div>

      {/* Main Navigation Bar */}
      <nav className="bg-slate-950 border-t border-slate-800/80 px-4 sm:px-6">
        <div className="max-w-7xl mx-auto flex items-center overflow-x-auto space-x-1 sm:space-x-2 py-1 scrollbar-none">
          {[
            { id: 'gis-map', label: '1. Gemelo Digital & Mapa GIS', icon: Layers },
            { id: 'rl-engine', label: '2. Agente RL & Closed-Loop', icon: Cpu },
            { id: 'telemetry', label: '3. Telemetría & TimescaleDB', icon: Activity },
            { id: 'what-if', label: '4. Simulador What-If', icon: Sliders },
            { id: 'reports', label: '5. Reportes PDF/Word/Excel', icon: Droplet },
            { id: 'rbac-audit', label: '6. Roles & Auditoría SHA-256', icon: ShieldCheck },
            { id: 'codebase', label: '7. Arquitectura & Código FastAPI', icon: RefreshCw }
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                id={`tab-nav-${tab.id}`}
                onClick={() => onTabChange(tab.id)}
                className={`flex items-center gap-2 px-3 py-2 text-xs sm:text-sm font-medium rounded-lg whitespace-nowrap transition-colors ${
                  isActive
                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-emerald-400' : 'text-slate-500'}`} />
                {tab.label}
              </button>
            );
          })}
        </div>
      </nav>
    </header>
  );
};
