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
  RefreshCw,
  Bell,
  Sun,
  Moon,
  Menu
} from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
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
  onToggleSidebar: () => void;
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
  onToggleSidebar
}) => {
  const { theme, toggleTheme } = useTheme();
  
  const getRoleBadge = (role: UserRole) => {
    switch (role) {
      case 'superadmin':
        return { label: 'Superadmin', color: 'bg-purple-500/20 text-purple-300 dark:text-purple-300 border-purple-500/40' };
      case 'agronomist':
        return { label: 'Agrónomo Senior', color: 'bg-emerald-500/20 text-emerald-300 dark:text-emerald-300 border-emerald-500/40' };
      case 'farmer':
        return { label: 'Productor Agrícola', color: 'bg-amber-500/20 text-amber-300 dark:text-amber-300 border-amber-500/40' };
      case 'field_technician':
        return { label: 'Técnico de Campo', color: 'bg-blue-500/20 text-blue-300 dark:text-blue-300 border-blue-500/40' };
      case 'rl_agent_system':
        return { label: 'RL Agent Autonomous', color: 'bg-rose-500/20 text-rose-300 dark:text-rose-300 border-rose-500/40' };
    }
  };

  const currentRoleInfo = getRoleBadge(activeRole);

  return (
    <header className="bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 border-b sticky top-0 z-40 shadow-md dark:shadow-xl">
      {/* Top Banner */}
      <div className="max-w-full px-4 sm:px-6 xl:px-8 py-3 flex flex-wrap lg:flex-nowrap items-center justify-between gap-3 lg:gap-4">

        {/* Botón Hamburguesa (toggle sidebar) */}
        <button
          onClick={onToggleSidebar}
          className="lg:hidden flex items-center justify-center w-10 h-10 rounded-xl
                     bg-slate-100 dark:bg-slate-800
                     text-slate-700 dark:text-slate-200
                     hover:bg-slate-200 dark:hover:bg-slate-700
                     hover:text-slate-900 dark:hover:text-white
                     border border-slate-200 dark:border-slate-700
                     transition-all shrink-0"
          aria-label="Abrir menú de navegación"
          title="Abrir menú"
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Brand & Field Info */}
        <div className="flex items-center gap-3 min-w-0 lg:min-w-[340px] xl:min-w-[420px] 2xl:flex-1 2xl:max-w-2xl">
          <div className="w-10 h-10 shrink-0 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-700 flex items-center justify-center shadow-lg shadow-emerald-950/40 border border-emerald-400/30">
            <Droplet className="w-5 h-5 text-white" />
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-2 min-w-0">
              <h1 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white tracking-tight flex items-center gap-2 min-w-0 whitespace-nowrap overflow-hidden">
                CLOSED-LOOP DIGITAL TWIN <span className="text-emerald-400 shrink-0">VRI</span>
              </h1>
              <span className="hidden xl:inline-flex shrink-0 px-2 py-0.5 text-xs font-semibold rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                PPO-RL Core
              </span>
            </div>
            <p className="text-xs text-slate-600 dark:text-slate-400 font-medium truncate">
              {field.name} • {field.cropName} ({field.cropStage})
            </p>
          </div>
        </div>

        {/* System Controls & State Indicators */}
        <div className="flex flex-wrap lg:flex-nowrap w-full lg:w-auto items-center justify-end gap-1.5 sm:gap-2 xl:gap-2.5 shrink-0">
          
          {/* Theme Toggle Button */}
          <button
            onClick={toggleTheme}
            className="flex shrink-0 items-center gap-1.5 px-2.5 py-1.5 rounded-lg border text-xs font-medium transition-all bg-slate-100 dark:bg-slate-950 text-slate-700 dark:text-slate-300 border-slate-300 dark:border-slate-700 hover:border-slate-400 dark:hover:border-slate-600 hover:bg-slate-200 dark:hover:text-slate-100"
            title={`Cambiar a ${theme === 'dark' ? 'modo claro' : 'modo oscuro'}`}
          >
            {theme === 'dark' ? (
              <>
                <Sun className="w-3.5 h-3.5 text-yellow-400" />
                <span className="hidden sm:inline">Claro</span>
              </>
            ) : (
              <>
                <Moon className="w-3.5 h-3.5 text-slate-600" />
                <span className="hidden sm:inline">Oscuro</span>
              </>
            )}
          </button>
          
          {/* Operation Mode Selector */}
          <div className="flex shrink-0 items-center bg-slate-100 dark:bg-slate-950/80 border-slate-300 dark:border-slate-800 p-1 rounded-lg border">
            <span className="text-xs font-medium text-slate-600 dark:text-slate-400 px-1.5 xl:px-2 flex items-center gap-1">
              <Sliders className="w-3.5 h-3.5 text-emerald-400 hidden xl:inline" />
              <span className="hidden xl:inline">Modo:</span>
            </span>
            <button
              id="mode-manual-btn"
              onClick={() => onSystemModeChange('manual')}
              className={`px-2 xl:px-2.5 py-1 text-xs font-medium rounded transition-all ${
                systemMode === 'manual'
                  ? 'bg-slate-300 dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm font-semibold'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
              }`}
            >
              Manual
            </button>
            <button
              id="mode-assisted-btn"
              onClick={() => onSystemModeChange('assisted')}
              className={`px-2 xl:px-2.5 py-1 text-xs font-medium rounded transition-all ${
                systemMode === 'assisted'
                  ? 'bg-blue-600 text-white shadow-sm font-semibold'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
              }`}
            >
              Asistido
            </button>
            <button
              id="mode-autonomous-btn"
              onClick={() => onSystemModeChange('autonomous')}
              className={`px-2 xl:px-2.5 py-1 text-xs font-medium rounded transition-all flex items-center gap-1 ${
                systemMode === 'autonomous'
                  ? 'bg-emerald-600 text-white shadow-sm font-semibold animate-pulse'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
              }`}
            >
              <Cpu className="w-3 h-3" />
              <span className="hidden sm:inline">Autónomo</span>
              <span className="sm:hidden">Auto</span>
            </button>
          </div>

          {/* Rural Offline / Online Simulator */}
          <button
            id="toggle-connectivity-btn"
            onClick={onToggleOnline}
            className={`flex shrink-0 items-center gap-1.5 px-2.5 xl:px-3 py-1.5 rounded-lg border text-xs font-medium transition-all ${
              isOnline
                ? 'bg-slate-100 dark:bg-slate-950 text-slate-700 dark:text-slate-300 border-slate-300 dark:border-slate-700 hover:border-slate-400 dark:hover:border-slate-600'
                : 'bg-amber-100/60 dark:bg-amber-950/40 text-amber-700 dark:text-amber-300 border-amber-400/60 dark:border-amber-500/40 hover:bg-amber-200/60 dark:hover:bg-amber-900/40'
            }`}
            title={isOnline ? 'Conexión activa con TimescaleDB y Celery' : 'Modo Rural Offline: Datos en cola local'}
          >
            {isOnline ? (
              <>
                <Wifi className="w-3.5 h-3.5 text-emerald-400" />
                <span className="hidden sm:inline">Online</span>
              </>
            ) : (
              <>
                <WifiOff className="w-3.5 h-3.5 text-amber-400" />
                <span className="sm:hidden">Offline ({offlineQueueCount})</span>
                <span className="hidden sm:inline">Rural Offline ({offlineQueueCount})</span>
              </>
            )}
          </button>

          {/* RBAC Role Switcher */}
          <div className="flex shrink-0 items-center gap-1.5 bg-slate-100 dark:bg-slate-950/80 border-slate-300 dark:border-slate-800 px-2 xl:px-2.5 py-1 rounded-lg border max-w-[320px] xl:max-w-none">
            <User className="w-3.5 h-3.5 text-slate-600 dark:text-slate-400 hidden sm:inline" />
            <select
              id="role-selector-dropdown"
              value={activeRole}
              onChange={(e) => onRoleChange(e.target.value as UserRole)}
              className="bg-transparent text-xs font-medium text-slate-900 dark:text-slate-200 focus:outline-none cursor-pointer pr-1 min-w-0 max-w-[180px] xl:max-w-none"
            >
              <option value="superadmin" className="bg-slate-100 dark:bg-slate-900 text-slate-900 dark:text-white">Superadmin</option>
              <option value="agronomist" className="bg-slate-100 dark:bg-slate-900 text-slate-900 dark:text-white">Agrónomo Senior</option>
              <option value="farmer" className="bg-slate-100 dark:bg-slate-900 text-slate-900 dark:text-white">Productor Agrícola</option>
              <option value="field_technician" className="bg-slate-100 dark:bg-slate-900 text-slate-900 dark:text-white">Técnico de Campo</option>
              <option value="rl_agent_system" className="bg-slate-100 dark:bg-slate-900 text-slate-900 dark:text-white">RL Agent</option>
            </select>
            <span className={`hidden sm:inline-flex px-1.5 py-0.5 text-[10px] font-semibold rounded border ${currentRoleInfo.color}`}>
              {currentRoleInfo.label}
            </span>
          </div>

        </div>
      </div>
    </header>
  );
};
