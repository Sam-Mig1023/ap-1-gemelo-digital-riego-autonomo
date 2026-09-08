import React, { useState } from 'react';
import { 
  Code2, 
  Database, 
  Server, 
  Cpu, 
  Terminal, 
  Copy, 
  Check, 
  FileCode, 
  Layers, 
  Boxes,
  ArrowRight,
  Sparkles,
  GitBranch,
  ShieldCheck
} from 'lucide-react';
import { CODEBASE_DELIVERABLES, CodeFile } from '../services/codebaseData';
import { useLanguage } from '../contexts/LanguageContext';

export const ArchitectureAndCodeViewer: React.FC = () => {
  const { t } = useLanguage();
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedFile, setSelectedFile] = useState<CodeFile>(CODEBASE_DELIVERABLES[0]);
  const [copied, setCopied] = useState<boolean>(false);
  const [activeSubTab, setActiveSubTab] = useState<'architecture' | 'codebase' | 'er_diagram' | 'api_spec'>('architecture');

  const filteredFiles = selectedCategory === 'all'
    ? CODEBASE_DELIVERABLES
    : CODEBASE_DELIVERABLES.filter(f => f.category === selectedCategory);

  const handleCopyCode = () => {
    navigator.clipboard.writeText(selectedFile.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-6">
      
      {/* Top Banner */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-4 sm:p-5 rounded-2xl flex flex-wrap items-center justify-between gap-4 shadow-xl">
        <div className="flex items-center gap-3.5">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-500 to-cyan-700 flex items-center justify-center shadow-lg shadow-emerald-950/50 border border-emerald-400/40">
            <Code2 className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white tracking-tight">
              {t('codeViewer.title')}
            </h2>
            <p className="text-xs text-slate-600 dark:text-slate-400 mt-0.5">
              {t('codeViewer.subtitle')}
            </p>
          </div>
        </div>

        {/* Sub-Tab Navigation */}
        <div className="flex items-center bg-slate-50 dark:bg-slate-950 p-1 rounded-xl border border-slate-200 dark:border-slate-800 text-xs">
          {[
            { id: 'architecture', label: t('codeViewer.tabs.architecture'), icon: Boxes },
            { id: 'codebase', label: t('codeViewer.tabs.codebase'), icon: Terminal },
            { id: 'er_diagram', label: t('codeViewer.tabs.er'), icon: Database },
            { id: 'api_spec', label: t('codeViewer.tabs.api'), icon: Server }
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeSubTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveSubTab(tab.id as any)}
                className={`flex items-center gap-1.5 px-3 py-1.5 font-medium rounded-lg transition-all ${
                  isActive
                    ? 'bg-emerald-600 text-white font-semibold shadow-sm'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Subtab 1: System Component Architecture & Data Pipeline */}
      {activeSubTab === 'architecture' && (
        <div className="space-y-6">
          
          {/* Visual Interactive Pipeline Diagram */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-6 rounded-2xl space-y-6 shadow-xl">
            <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-3">
              <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <Boxes className="w-4 h-4 text-emerald-400" />
                <span>{t('codeViewer.architecture.pipelineTitle')}</span>
              </h3>
              <span className="text-xs text-emerald-400 font-mono">{t('codeViewer.architecture.feedbackLoop')}</span>
            </div>

            {/* Pipeline Stage Blocks */}
            <div className="grid grid-cols-1 md:grid-cols-5 gap-3 relative">
              
              {/* Stage 1: Ingestion */}
              <div className="bg-slate-50 dark:bg-slate-950 p-4 rounded-xl border border-slate-200 dark:border-slate-800 space-y-2.5">
                <div className="w-7 h-7 rounded-lg bg-blue-500/20 text-blue-400 flex items-center justify-center text-xs font-bold font-mono">
                  01
                </div>
                <h4 className="text-xs font-bold text-slate-900 dark:text-white">{t('codeViewer.architecture.stages.0.title')}</h4>
                <p className="text-[11px] text-slate-600 dark:text-slate-400 leading-relaxed">
                  {t('codeViewer.architecture.stages.0.bullets.0')}<br />
                  {t('codeViewer.architecture.stages.0.bullets.1')}<br />
                  {t('codeViewer.architecture.stages.0.bullets.2')}<br />
                  {t('codeViewer.architecture.stages.0.bullets.3')}
                </p>
                <span className="text-[10px] text-blue-400 bg-blue-950/60 px-2 py-0.5 rounded block text-center border border-blue-500/30">
                  {t('codeViewer.architecture.stages.0.storage')}
                </span>
              </div>

              {/* Stage 2: Fusion Pipeline */}
              <div className="bg-slate-50 dark:bg-slate-950 p-4 rounded-xl border border-slate-200 dark:border-slate-800 space-y-2.5">
                <div className="w-7 h-7 rounded-lg bg-purple-500/20 text-purple-400 flex items-center justify-center text-xs font-bold font-mono">
                  02
                </div>
                <h4 className="text-xs font-bold text-slate-900 dark:text-white">{t('codeViewer.architecture.stages.1.title')}</h4>
                <p className="text-[11px] text-slate-600 dark:text-slate-400 leading-relaxed">
                  {t('codeViewer.architecture.stages.1.bullets.0')}<br />
                  {t('codeViewer.architecture.stages.1.bullets.1')}<br />
                  {t('codeViewer.architecture.stages.1.bullets.2')}<br />
                  {t('codeViewer.architecture.stages.1.bullets.3')}
                </p>
                <span className="text-[10px] text-purple-400 bg-purple-950/60 px-2 py-0.5 rounded block text-center border border-purple-500/30">
                  {t('codeViewer.architecture.stages.1.storage')}
                </span>
              </div>

              {/* Stage 3: RL Core */}
              <div className="bg-slate-50 dark:bg-slate-950 p-4 rounded-xl border border-emerald-500/40 shadow-lg shadow-emerald-950/30 space-y-2.5">
                <div className="w-7 h-7 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center text-xs font-bold font-mono">
                  03
                </div>
                <h4 className="text-xs font-bold text-emerald-400">{t('codeViewer.architecture.stages.2.title')}</h4>
                <p className="text-[11px] text-slate-700 dark:text-slate-300 leading-relaxed">
                  {t('codeViewer.architecture.stages.2.bullets.0')}<br />
                  {t('codeViewer.architecture.stages.2.bullets.1')}<br />
                  {t('codeViewer.architecture.stages.2.bullets.2')}<br />
                  {t('codeViewer.architecture.stages.2.bullets.3')}
                </p>
                <span className="text-[10px] text-emerald-300 bg-emerald-950/80 px-2 py-0.5 rounded block text-center border border-emerald-500/40 font-semibold">
                  {t('codeViewer.architecture.stages.2.storage')}
                </span>
              </div>

              {/* Stage 4: Execution */}
              <div className="bg-slate-50 dark:bg-slate-950 p-4 rounded-xl border border-slate-200 dark:border-slate-800 space-y-2.5">
                <div className="w-7 h-7 rounded-lg bg-amber-500/20 text-amber-400 flex items-center justify-center text-xs font-bold font-mono">
                  04
                </div>
                <h4 className="text-xs font-bold text-slate-900 dark:text-white">{t('codeViewer.architecture.stages.3.title')}</h4>
                <p className="text-[11px] text-slate-600 dark:text-slate-400 leading-relaxed">
                  {t('codeViewer.architecture.stages.3.bullets.0')}<br />
                  {t('codeViewer.architecture.stages.3.bullets.1')}<br />
                  {t('codeViewer.architecture.stages.3.bullets.2')}<br />
                  {t('codeViewer.architecture.stages.3.bullets.3')}
                </p>
                <span className="text-[10px] text-amber-400 bg-amber-950/60 px-2 py-0.5 rounded block text-center border border-amber-500/30">
                  {t('codeViewer.architecture.stages.3.storage')}
                </span>
              </div>

              {/* Stage 5: Feedback & Calibration */}
              <div className="bg-slate-50 dark:bg-slate-950 p-4 rounded-xl border border-blue-500/40 space-y-2.5">
                <div className="w-7 h-7 rounded-lg bg-blue-500/20 text-blue-400 flex items-center justify-center text-xs font-bold font-mono">
                  05
                </div>
                <h4 className="text-xs font-bold text-blue-400">{t('codeViewer.architecture.stages.4.title')}</h4>
                <p className="text-[11px] text-slate-600 dark:text-slate-400 leading-relaxed">
                  {t('codeViewer.architecture.stages.4.bullets.0')}<br />
                  {t('codeViewer.architecture.stages.4.bullets.1')}<br />
                  {t('codeViewer.architecture.stages.4.bullets.2')}<br />
                  {t('codeViewer.architecture.stages.4.bullets.3')}
                </p>
                <span className="text-[10px] text-blue-300 bg-blue-950/80 px-2 py-0.5 rounded block text-center border border-blue-500/40 font-semibold">
                  {t('codeViewer.architecture.stages.4.storage')}
                </span>
              </div>

            </div>

            {/* Assumptions & Physical Models Note */}
            <div className="bg-slate-50/60 dark:bg-slate-950/80 p-4 rounded-xl border border-slate-200 dark:border-slate-800 space-y-2 text-xs text-slate-700 dark:text-slate-300">
              <h4 className="font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-emerald-400" />
                <span>{t('codeViewer.architecture.assumptionsTitle')}</span>
              </h4>
              <ul className="list-disc list-inside space-y-1 text-slate-600 dark:text-slate-400 text-[11px]">
                <li dangerouslySetInnerHTML={{__html: t('codeViewer.architecture.assumptions.0')}}></li>
                <li dangerouslySetInnerHTML={{__html: t('codeViewer.architecture.assumptions.1')}}></li>
                <li dangerouslySetInnerHTML={{__html: t('codeViewer.architecture.assumptions.2')}}></li>
                <li dangerouslySetInnerHTML={{__html: t('codeViewer.architecture.assumptions.3')}}></li>
              </ul>
            </div>

          </div>

        </div>
      )}

      {/* Subtab 2: Interactive Codebase Browser */}
      {activeSubTab === 'codebase' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          {/* File Tree Explorer (4 Cols) */}
          <div className="lg:col-span-4 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-4 rounded-2xl space-y-3 shadow-lg">
            <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-2.5">
              <span className="text-xs font-bold text-slate-800 dark:text-slate-200 uppercase tracking-wider flex items-center gap-1.5">
                <FileCode className="w-3.5 h-3.5 text-emerald-400" />
                {t('codeViewer.codebase.browserTitle')}
              </span>
              <span className="text-[10px] text-slate-600 dark:text-slate-400 font-mono">{filteredFiles.length} {t('codeViewer.codebase.filesSuffix')}</span>
            </div>

            {/* Category Filter */}
            <div className="flex flex-wrap gap-1">
              {[
                { key: 'all', label: t('codeViewer.codebase.categories.all') },
                { key: 'backend', label: t('codeViewer.codebase.categories.backend') },
                { key: 'database', label: t('codeViewer.codebase.categories.database') },
                { key: 'ml_rl', label: t('codeViewer.codebase.categories.mlrl') },
                { key: 'infrastructure', label: t('codeViewer.codebase.categories.infra') },
                { key: 'tests', label: t('codeViewer.codebase.categories.tests') }
              ].map((cat) => (
                <button
                  key={cat.key}
                  onClick={() => setSelectedCategory(cat.key)}
                  className={`px-2 py-0.5 text-[10px] rounded font-medium transition-all ${
                    selectedCategory === cat.key
                      ? 'bg-emerald-600 text-white font-bold'
                      : 'bg-slate-50 dark:bg-slate-950 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                  }`}
                >
                  {cat.label}
                </button>
              ))}
            </div>

            {/* Files List */}
            <div className="space-y-1 max-h-[480px] overflow-y-auto pr-1">
              {filteredFiles.map((file) => {
                const isSelected = file.path === selectedFile.path;
                return (
                  <button
                    key={file.path}
                    onClick={() => setSelectedFile(file)}
                    className={`w-full text-left p-2.5 rounded-lg border transition-all flex items-start gap-2.5 ${
                      isSelected
                        ? 'bg-emerald-950/40 border-emerald-500/50 text-emerald-300'
                        : 'bg-slate-50/60 dark:bg-slate-950/60 border-slate-200/80 dark:border-slate-800/80 text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-white'
                    }`}
                  >
                    <Terminal className="w-4 h-4 mt-0.5 flex-shrink-0 text-emerald-400" />
                    <div className="overflow-hidden">
                      <span className="text-xs font-mono font-semibold block truncate">{file.path}</span>
                      <span className="text-[10px] text-slate-500 block truncate">{file.description}</span>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Code Viewer Panel (8 Cols) */}
          <div className="lg:col-span-8 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl overflow-hidden shadow-2xl flex flex-col">
            
            <div className="bg-slate-950 p-3.5 border-b border-slate-800 flex items-center justify-between">
              <div className="flex items-center gap-2 font-mono text-xs text-slate-300">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-400" />
                <span className="font-bold text-white">{selectedFile.path}</span>
                <span className="text-[10px] text-slate-400 bg-slate-800 px-2 py-0.5 rounded uppercase">
                  {selectedFile.language}
                </span>
              </div>

              <button
                onClick={handleCopyCode}
                className="flex items-center gap-1.5 px-3 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-medium border border-slate-700 transition-all"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copied ? t('codeViewer.codebase.copied') : t('codeViewer.codebase.copy')}</span>
              </button>
            </div>

            <pre className="p-4 sm:p-5 text-xs font-mono text-slate-200 bg-slate-950 overflow-x-auto max-h-[500px] leading-relaxed">
              <code>{selectedFile.content}</code>
            </pre>

          </div>

        </div>
      )}

      {/* Subtab 3: Database ER Diagram & PostGIS */}
      {activeSubTab === 'er_diagram' && (
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-6 rounded-2xl space-y-6 shadow-xl">
          <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-3">
            <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <Database className="w-4 h-4 text-emerald-400" />
              <span>{t('codeViewer.er.title')}</span>
            </h3>
            <span className="text-xs text-slate-600 dark:text-slate-400">SRID: 4326 (WGS 84)</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            
            {/* Table 1: agricultural_fields */}
            <div className="bg-slate-50 dark:bg-slate-950 p-4 rounded-xl border border-slate-200 dark:border-slate-800 space-y-2">
              <div className="flex justify-between items-center border-b border-slate-200 dark:border-slate-800 pb-1.5">
                <span className="font-mono font-bold text-xs text-emerald-400">agricultural_fields</span>
                <span className="text-[10px] text-slate-500">Entidad PostGIS</span>
              </div>
              <ul className="text-xs font-mono space-y-1 text-slate-700 dark:text-slate-300">
                <li><span className="text-blue-400">id:</span> String(36) [PK]</li>
                <li><span className="text-blue-400">tenant_id:</span> String(64) [FK]</li>
                <li><span className="text-purple-400">boundary_geom:</span> Geometry(Polygon)</li>
                <li><span className="text-slate-600 dark:text-slate-400">total_area_ha:</span> Float</li>
                <li><span className="text-slate-600 dark:text-slate-400">crop_name:</span> String(100)</li>
                <li><span className="text-slate-600 dark:text-slate-400">kc_factor:</span> Float</li>
              </ul>
            </div>

            {/* Table 2: management_zones */}
            <div className="bg-slate-50 dark:bg-slate-950 p-4 rounded-xl border border-slate-200 dark:border-slate-800 space-y-2">
              <div className="flex justify-between items-center border-b border-slate-200 dark:border-slate-800 pb-1.5">
                <span className="font-mono font-bold text-xs text-teal-400">management_zones</span>
                <span className="text-[10px] text-slate-500">Sector VRI PostGIS</span>
              </div>
              <ul className="text-xs font-mono space-y-1 text-slate-700 dark:text-slate-300">
                <li><span className="text-blue-400">id:</span> String(36) [PK]</li>
                <li><span className="text-blue-400">field_id:</span> String(36) [FK]</li>
                <li><span className="text-purple-400">zone_polygon:</span> Geometry(Polygon)</li>
                <li><span className="text-amber-400">saturated_k:</span> Float (Green-Ampt)</li>
                <li><span className="text-slate-600 dark:text-slate-400">field_capacity:</span> Float</li>
                <li><span className="text-slate-600 dark:text-slate-400">wilting_point:</span> Float</li>
              </ul>
            </div>

            {/* Table 3: sensor_readings */}
            <div className="bg-slate-50 dark:bg-slate-950 p-4 rounded-xl border border-blue-500/40 space-y-2">
              <div className="flex justify-between items-center border-b border-slate-200 dark:border-slate-800 pb-1.5">
                <span className="font-mono font-bold text-xs text-blue-400">sensor_readings</span>
                <span className="text-[10px] text-blue-300 bg-blue-950 px-1.5 py-0.5 rounded font-bold">Hypertable</span>
              </div>
              <ul className="text-xs font-mono space-y-1 text-slate-700 dark:text-slate-300">
                <li><span className="text-blue-400">timestamp:</span> DateTime [PK/Index]</li>
                <li><span className="text-blue-400">sensor_id:</span> String(64) [PK]</li>
                <li><span className="text-slate-600 dark:text-slate-400">zone_id:</span> String(36) [Index]</li>
                <li><span className="text-emerald-400">vwc_10cm, 30cm, 60cm:</span> Float</li>
                <li><span className="text-amber-400">canopy_temp_c:</span> Float</li>
                <li><span className="text-rose-400">anomaly_score:</span> Float</li>
              </ul>
            </div>

          </div>
        </div>
      )}

      {/* Subtab 4: API Specification */}
      {activeSubTab === 'api_spec' && (
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-6 rounded-2xl space-y-4 shadow-xl">
          <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-3">
            <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <Server className="w-4 h-4 text-emerald-400" />
              <span>{t('codeViewer.api.title')}</span>
            </h3>
            <span className="text-xs text-emerald-400 font-mono">REST + WebSockets</span>
          </div>

          <div className="space-y-2.5 text-xs font-mono">
            {[
              { method: 'POST', path: '/api/v1/auth/login', desc: t('codeViewer.api.endpoints.0') },
              { method: 'GET', path: '/api/v1/fields/{field_id}/zones', desc: t('codeViewer.api.endpoints.1') },
              { method: 'POST', path: '/api/v1/sensors/telemetry/ingest', desc: t('codeViewer.api.endpoints.2') },
              { method: 'POST', path: '/api/v1/rl/infer-vri-rates', desc: t('codeViewer.api.endpoints.3') },
              { method: 'POST', path: '/api/v1/irrigation/execute-decision', desc: t('codeViewer.api.endpoints.4') },
              { method: 'POST', path: '/api/v1/digital-twin/what-if', desc: t('codeViewer.api.endpoints.5') },
              { method: 'GET', path: '/api/v1/reports/export/{format}', desc: t('codeViewer.api.endpoints.6') },
              { method: 'WS', path: '/ws/telemetry/{field_id}', desc: t('codeViewer.api.endpoints.7') }
            ].map((ep, i) => (
              <div key={i} className="bg-slate-50 dark:bg-slate-950 p-3 rounded-xl border border-slate-200 dark:border-slate-800 flex flex-wrap items-center justify-between gap-2">
                <div className="flex items-center gap-2.5">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    ep.method === 'GET' ? 'bg-blue-500/20 text-blue-400' :
                    ep.method === 'POST' ? 'bg-emerald-500/20 text-emerald-400' :
                    'bg-purple-500/20 text-purple-400'
                  }`}>
                    {ep.method}
                  </span>
                  <span className="text-slate-900 dark:text-white font-bold">{ep.path}</span>
                </div>
                <span className="text-slate-600 dark:text-slate-400 text-[11px] font-sans">{ep.desc}</span>
              </div>
            ))}
          </div>
        </div>
      )}

    </div>
  );
};
