import React, { useState } from 'react';
import { 
  FileText, 
  FileSpreadsheet, 
  FileCheck, 
  Download, 
  Clock, 
  CheckCircle2, 
  Calendar, 
  Send,
  Sparkles,
  Layers
} from 'lucide-react';
import { 
  AgriculturalField, 
  ManagementZone, 
  SensorTelemetry, 
  RLDecision, 
  AuditLogEntry, 
  ScheduledReport 
} from '../types';
import { 
  generateExecutivePDF, 
  generateWordDocx, 
  generateExcelWorkbook, 
  generateCSVExport, 
  generateJSONExport 
} from '../services/reportGenerators';

interface ReportExportStudioProps {
  field: AgriculturalField;
  zones: ManagementZone[];
  sensors: SensorTelemetry[];
  decisions: RLDecision[];
  auditLogs: AuditLogEntry[];
  scheduledReports: ScheduledReport[];
  currentUserName: string;
}

export const ReportExportStudio: React.FC<ReportExportStudioProps> = ({
  field,
  zones,
  sensors,
  decisions,
  auditLogs,
  scheduledReports,
  currentUserName
}) => {
  const [isExporting, setIsExporting] = useState<string | null>(null);
  const [scheduledList, setScheduledList] = useState<ScheduledReport[]>(scheduledReports);
  const [notificationMsg, setNotificationMsg] = useState<string | null>(null);

  const payload = {
    field,
    zones,
    sensors,
    decisions,
    auditLogs,
    generatedBy: currentUserName
  };

  const handleExport = async (format: 'pdf' | 'docx' | 'xlsx' | 'csv' | 'json') => {
    setIsExporting(format);
    try {
      if (format === 'pdf') {
        generateExecutivePDF(payload);
      } else if (format === 'docx') {
        await generateWordDocx(payload);
      } else if (format === 'xlsx') {
        generateExcelWorkbook(payload);
      } else if (format === 'csv') {
        generateCSVExport(payload);
      } else if (format === 'json') {
        generateJSONExport(payload);
      }
      setNotificationMsg(`Reporte en formato ${format.toUpperCase()} generado y descargado exitosamente.`);
    } catch (err) {
      console.error(err);
      setNotificationMsg(`Error al generar reporte: ${String(err)}`);
    } finally {
      setIsExporting(null);
      setTimeout(() => setNotificationMsg(null), 4500);
    }
  };

  const handleTriggerDispatch = (report: ScheduledReport) => {
    setNotificationMsg(`Tarea Celery encolada: Envío programado "${report.title}" despachado a ${report.recipients.join(', ')}.`);
    setTimeout(() => setNotificationMsg(null), 4500);
  };

  return (
    <div className="space-y-6">
      
      {/* Header Banner */}
      <div className="bg-slate-900 border border-slate-800 p-4 sm:p-5 rounded-2xl flex flex-wrap items-center justify-between gap-4 shadow-xl">
        <div className="flex items-center gap-3.5">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-700 flex items-center justify-center shadow-lg shadow-emerald-950/50 border border-emerald-400/40">
            <FileText className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-base sm:text-lg font-bold text-white tracking-tight">
              Módulo de Reportes Ejecutivos & Exportación de Datos
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Generación de documentos ejecutivos (PDF/Word/Excel) y automatización con Celery Beat
            </p>
          </div>
        </div>
      </div>

      {notificationMsg && (
        <div className="bg-emerald-950/40 border border-emerald-500/40 p-3.5 rounded-xl text-xs text-emerald-300 flex items-center gap-2 animate-fadeIn">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
          <span>{notificationMsg}</span>
        </div>
      )}

      {/* Export Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        {/* PDF Executive Report */}
        <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl space-y-3.5 shadow-lg flex flex-col justify-between hover:border-emerald-500/50 transition-all">
          <div className="space-y-2">
            <div className="w-10 h-10 rounded-xl bg-rose-500/20 text-rose-400 border border-rose-500/30 flex items-center justify-center">
              <FileText className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-bold text-white">Informe Ejecutivo PDF</h3>
            <p className="text-xs text-slate-400">
              Documento formal para gerencia y propietarios con tablas de balance hídrico, ahorro en m³, métricas de estrés y firmas.
            </p>
          </div>

          <button
            id="export-pdf-btn"
            onClick={() => handleExport('pdf')}
            disabled={isExporting === 'pdf'}
            className="w-full py-2 px-3 rounded-xl bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold flex items-center justify-center gap-2 transition-all shadow-md shadow-rose-950/40"
          >
            <Download className="w-3.5 h-3.5" />
            <span>{isExporting === 'pdf' ? 'Generando...' : 'Descargar PDF'}</span>
          </button>
        </div>

        {/* Word .docx Agronomic Document */}
        <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl space-y-3.5 shadow-lg flex flex-col justify-between hover:border-blue-500/50 transition-all">
          <div className="space-y-2">
            <div className="w-10 h-10 rounded-xl bg-blue-500/20 text-blue-400 border border-blue-500/30 flex items-center justify-center">
              <FileCheck className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-bold text-white">Informe Técnico Word (.docx)</h3>
            <p className="text-xs text-slate-400">
              Documento editable para agrónomos y asesores técnicos, con capítulos de análisis bio-físico, justificación del modelo RL y firmas.
            </p>
          </div>

          <button
            id="export-docx-btn"
            onClick={() => handleExport('docx')}
            disabled={isExporting === 'docx'}
            className="w-full py-2 px-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold flex items-center justify-center gap-2 transition-all shadow-md shadow-blue-950/40"
          >
            <Download className="w-3.5 h-3.5" />
            <span>{isExporting === 'docx' ? 'Generando...' : 'Descargar Word (.docx)'}</span>
          </button>
        </div>

        {/* Excel .xlsx Multi-tab Workbook */}
        <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl space-y-3.5 shadow-lg flex flex-col justify-between hover:border-emerald-500/50 transition-all">
          <div className="space-y-2">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center justify-center">
              <FileSpreadsheet className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-bold text-white">Libro de Datos Excel (.xlsx)</h3>
            <p className="text-xs text-slate-400">
              Libro multi-pestaña: Resumen Campo, Zonas de Manejo, Telemetría Cruda, Registro de Decisiones RL y Auditoría RBAC.
            </p>
          </div>

          <button
            id="export-xlsx-btn"
            onClick={() => handleExport('xlsx')}
            disabled={isExporting === 'xlsx'}
            className="w-full py-2 px-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold flex items-center justify-center gap-2 transition-all shadow-md shadow-emerald-950/40"
          >
            <Download className="w-3.5 h-3.5" />
            <span>{isExporting === 'xlsx' ? 'Generando...' : 'Descargar Excel (.xlsx)'}</span>
          </button>
        </div>

        {/* CSV / JSON Raw Streams */}
        <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl space-y-3.5 shadow-lg flex flex-col justify-between hover:border-purple-500/50 transition-all">
          <div className="space-y-2">
            <div className="w-10 h-10 rounded-xl bg-purple-500/20 text-purple-400 border border-purple-500/30 flex items-center justify-center">
              <Layers className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-bold text-white">Exportación Cruda (CSV / JSON)</h3>
            <p className="text-xs text-slate-400">
              Exportación masiva de series temporales de sensores y estado del Gemelo Digital para analítica externa en R o Python.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-2">
            <button
              id="export-csv-btn"
              onClick={() => handleExport('csv')}
              className="py-2 px-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 flex items-center justify-center gap-1 transition-all"
            >
              <Download className="w-3 h-3 text-purple-400" />
              <span>CSV</span>
            </button>
            <button
              id="export-json-btn"
              onClick={() => handleExport('json')}
              className="py-2 px-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 flex items-center justify-center gap-1 transition-all"
            >
              <Download className="w-3 h-3 text-emerald-400" />
              <span>JSON</span>
            </button>
          </div>
        </div>

      </div>

      {/* Celery Beat Scheduled Reports Automation Table */}
      <div className="bg-slate-900 border border-slate-800 p-4 sm:p-5 rounded-2xl space-y-4 shadow-xl">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-3">
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-emerald-400" />
            <h3 className="text-sm font-bold text-white">Programación de Reportes Automáticos (Celery Beat Daemon)</h3>
          </div>
          <span className="text-xs text-slate-400">
            Despacho asíncrono vía worker Redis/Celery
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950 text-slate-400 font-semibold border-b border-slate-800">
              <tr>
                <th className="p-3">Título del Reporte</th>
                <th className="p-3">Formato</th>
                <th className="p-3">Frecuencia</th>
                <th className="p-3">Destinatarios</th>
                <th className="p-3">Último Despacho</th>
                <th className="p-3">Estado</th>
                <th className="p-3">Acción Inmediata</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-slate-300">
              {scheduledList.map((rep) => (
                <tr key={rep.id} className="hover:bg-slate-800/50 transition-colors">
                  <td className="p-3 font-semibold text-white">{rep.title}</td>
                  <td className="p-3">
                    <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono font-bold uppercase text-[10px]">
                      {rep.format}
                    </span>
                  </td>
                  <td className="p-3 capitalize text-slate-300">{rep.frequency.replace('_', ' ')}</td>
                  <td className="p-3 text-slate-400 font-mono text-[11px]">
                    {rep.recipients.join(', ')}
                  </td>
                  <td className="p-3 font-mono text-slate-400">{rep.lastGenerated}</td>
                  <td className="p-3">
                    <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 text-[10px] font-bold">
                      {rep.status.toUpperCase()}
                    </span>
                  </td>
                  <td className="p-3">
                    <button
                      onClick={() => handleTriggerDispatch(rep)}
                      className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 text-[11px] font-medium border border-slate-700 flex items-center gap-1 transition-all"
                    >
                      <Send className="w-3 h-3 text-emerald-400" />
                      <span>Despachar Ahora</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
};
