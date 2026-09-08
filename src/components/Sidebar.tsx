import React from 'react';
import {
  Layers,
  Cpu,
  Activity,
  Sliders,
  Droplet,
  ShieldCheck,
  RefreshCw,
  X,
  ChevronRight
} from 'lucide-react';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
  activeTab: string;
  onTabChange: (tab: string) => void;
}

const NAV_ITEMS: Array<{
  id: string;
  label: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
}> = [
  { id: 'gis-map', label: '1. Gemelo Digital & Mapa GIS', icon: Layers, description: 'Vista central del campo agrícola' },
  { id: 'rl-engine', label: '2. Agente RL & Closed-Loop', icon: Cpu, description: 'Decisiones PPO y aprobaciones' },
  { id: 'telemetry', label: '3. Telemetría & TimescaleDB', icon: Activity, description: 'Gráficos de sensores en tiempo real' },
  { id: 'what-if', label: '4. Simulador What-If', icon: Sliders, description: 'Escenarios de riego y pronóstico' },
  { id: 'reports', label: '5. Reportes PDF / Word / Excel', icon: Droplet, description: 'Generación y programación de informes' },
  { id: 'rbac-audit', label: '6. Roles & Auditoría SHA-256', icon: ShieldCheck, description: 'Gestión RBAC y trazabilidad' },
  { id: 'codebase', label: '7. Arquitectura & Código FastAPI', icon: RefreshCw, description: 'Documentación técnica integrada' }
];

export const Sidebar: React.FC<SidebarProps> = ({
  isOpen,
  onClose,
  activeTab,
  onTabChange
}) => {
  return (
    <>
      {/* Overlay backdrop para móvil */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-slate-950/60 backdrop-blur-sm transition-opacity duration-200 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar panel */}
      <aside
        className={`
          fixed top-0 left-0 z-50 h-full
          w-72
          bg-white dark:bg-slate-900
          border-r border-slate-200 dark:border-slate-800
          shadow-xl dark:shadow-2xl
          flex flex-col
          transition-transform duration-300 ease-out
          ${isOpen ? 'translate-x-0' : '-translate-x-full'}
          lg:sticky lg:top-0 lg:z-20 lg:h-screen
          lg:translate-x-0 lg:shadow-none
        `}
      >
        {/* Sidebar Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950/40">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-700 flex items-center justify-center shadow-lg shadow-emerald-950/40 border border-emerald-400/30 shrink-0">
              <Droplet className="w-5 h-5 text-white" />
            </div>
            <div className="flex flex-col leading-tight">
              <span className="text-[11px] font-bold tracking-widest text-emerald-500 uppercase">VRI Core</span>
              <span className="text-sm font-bold text-slate-900 dark:text-white truncate max-w-[150px]">
                Navigation
              </span>
            </div>
          </div>
          <button
            onClick={onClose}
            className="lg:hidden flex items-center justify-center w-9 h-9 rounded-lg
                       bg-slate-100 dark:bg-slate-800
                       text-slate-600 dark:text-slate-300
                       hover:bg-slate-200 dark:hover:bg-slate-700
                       hover:text-slate-900 dark:hover:text-white
                       transition-colors"
            aria-label="Cerrar menú"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Título sección */}
        <div className="px-5 pt-5 pb-2">
          <p className="text-[10px] font-semibold uppercase tracking-widest text-slate-400 dark:text-slate-500">
            Módulos del Sistema
          </p>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            {NAV_ITEMS.length} vistas principales
          </p>
        </div>

        {/* Lista de navegación */}
        <nav className="flex-1 overflow-y-auto px-3 pb-6 scrollbar-none">
          <ul className="space-y-1">
            {NAV_ITEMS.map((item, idx) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <React.Fragment key={item.id}>
                  <li>
                    <button
                      onClick={() => {
                        onTabChange(item.id);
                        if (window.innerWidth < 1024) onClose();
                      }}
                      className={`
                        w-full group relative flex items-center gap-3 px-3 py-3 rounded-xl text-left
                        transition-all duration-200
                        ${isActive
                          ? 'bg-emerald-500/10 dark:bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 border border-emerald-500/30 shadow-sm'
                          : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800/60 hover:text-slate-900 dark:hover:text-white border border-transparent'
                        }
                      `}
                    >
                      {isActive && (
                        <span className="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-3 w-1.5 h-8 rounded-r-full bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.6)]" />
                      )}

                      <div
                        className={`
                          w-9 h-9 rounded-lg flex items-center justify-center shrink-0 transition-colors
                          ${isActive
                            ? 'bg-emerald-500/20 text-emerald-600 dark:text-emerald-400'
                            : 'bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 group-hover:bg-slate-200 dark:group-hover:bg-slate-700 group-hover:text-slate-700 dark:group-hover:text-slate-200'
                          }
                        `}
                      >
                        <Icon className="w-4.5 h-4.5" />
                      </div>

                      <div className="flex-1 min-w-0">
                        <div className={`text-sm font-semibold truncate ${isActive ? 'text-emerald-700 dark:text-emerald-300' : ''}`}>
                          {item.label}
                        </div>
                        <div className={`text-[11px] mt-0.5 truncate ${isActive ? 'text-emerald-600/80 dark:text-emerald-400/80' : 'text-slate-400 dark:text-slate-500'}`}>
                          {item.description}
                        </div>
                      </div>

                      <ChevronRight
                        className={`
                          w-4 h-4 shrink-0 transition-all duration-200
                          ${isActive
                            ? 'text-emerald-500 translate-x-0 opacity-100'
                            : 'text-slate-300 dark:text-slate-600 opacity-0 -translate-x-1 group-hover:opacity-100 group-hover:translate-x-0 group-hover:text-slate-500 dark:group-hover:text-slate-400'
                          }
                        `}
                      />
                    </button>
                  </li>

                  {(idx === 1 || idx === 4) && (
                    <li className="my-3 -mx-1">
                      <div className="h-px bg-slate-200 dark:bg-slate-800/80" />
                    </li>
                  )}
                </React.Fragment>
              );
            })}
          </ul>
        </nav>

        {/* Footer del Sidebar */}
        <div className="px-4 py-4 border-t border-slate-200 dark:border-slate-800 bg-slate-50/60 dark:bg-slate-950/40">
          <div className="flex items-center gap-2 px-2 py-2 rounded-lg bg-gradient-to-r from-emerald-500/10 to-teal-500/10 border border-emerald-500/20 dark:border-emerald-500/30">
            <div className="w-6 h-6 rounded-md bg-emerald-500 flex items-center justify-center shrink-0">
              <Cpu className="w-3.5 h-3.5 text-white" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-[11px] font-bold text-emerald-700 dark:text-emerald-400 leading-tight">
                PPO-RL Engine v4.2
              </p>
              <p className="text-[10px] text-emerald-600/70 dark:text-emerald-500/80 leading-tight">
                Closed-Loop • Online
              </p>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};
