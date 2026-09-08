import React, { useState, useEffect } from 'react';
import { useTheme } from './contexts/ThemeContext';
import { useLanguage } from './contexts/LanguageContext';
import {
  INITIAL_FIELD,
  INITIAL_ZONES,
  INITIAL_SENSORS,
  INITIAL_RADAR_GRID,
  INITIAL_RL_DECISIONS,
  INITIAL_USERS,
  INITIAL_AUDIT_LOGS,
  INITIAL_SCHEDULED_REPORTS
} from './data/mockData';
import {
  AgriculturalField,
  ManagementZone,
  SensorTelemetry,
  WeatherRadarCell,
  RLDecision,
  UserRole,
  SystemOperationMode,
  AuditLogEntry,
  OfflineQueueItem,
  ClosedLoopFeedback
} from './types';
import { runRLPolicyInference } from './services/rlAgentEngine';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { FieldGISMap } from './components/FieldGISMap';
import { RLDecisionConsole } from './components/RLDecisionConsole';
import { TelemetryAnalytics } from './components/TelemetryAnalytics';
import { WhatIfSimulator } from './components/WhatIfSimulator';
import { ReportExportStudio } from './components/ReportExportStudio';
import { RBACAuditConsole } from './components/RBACAuditConsole';
import { ArchitectureAndCodeViewer } from './components/ArchitectureAndCodeViewer';
import { ClosedLoopFeedbackModal } from './components/ClosedLoopFeedbackModal';
import { AgronomicChatbot } from './components/AgronomicChatbot';

export default function App() {
  useTheme();
  const { t } = useLanguage();
  const [field, setField] = useState<AgriculturalField>(INITIAL_FIELD);
  const [zones, setZones] = useState<ManagementZone[]>(INITIAL_ZONES);
  const [sensors, setSensors] = useState<SensorTelemetry[]>(INITIAL_SENSORS);
  const [radarCells, setRadarCells] = useState<WeatherRadarCell[]>(INITIAL_RADAR_GRID);
  const [decisions, setDecisions] = useState<RLDecision[]>(INITIAL_RL_DECISIONS);
  const [auditLogs, setAuditLogs] = useState<AuditLogEntry[]>(INITIAL_AUDIT_LOGS);
  const [scheduledReports, setScheduledReports] = useState(INITIAL_SCHEDULED_REPORTS);

  // UI & Global Session States
  const [activeTab, setActiveTab] = useState<string>('gis-map');
  const [activeRole, setActiveRole] = useState<UserRole>('agronomist');
  const [systemMode, setSystemMode] = useState<SystemOperationMode>('assisted');
  const [isOnline, setIsOnline] = useState<boolean>(true);
  const [offlineQueue, setOfflineQueue] = useState<OfflineQueueItem[]>([]);
  const [selectedZone, setSelectedZone] = useState<ManagementZone>(INITIAL_ZONES[0]);

  // Sidebar state
  const [isSidebarOpen, setIsSidebarOpen] = useState<boolean>(false);

  // Auto-close sidebar en desktop (<lg) cuando la ventana crece
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 1024) {
        setIsSidebarOpen(false);
      }
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const handleToggleSidebar = () => setIsSidebarOpen((prev) => !prev);
  const handleCloseSidebar = () => setIsSidebarOpen(false);

  // Active Feedback Modal
  const [feedbackDecision, setFeedbackDecision] = useState<RLDecision | null>(null);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 4000);
  };

  // Helper to record audit log
  const recordAudit = (action: string, resource: string, details: string) => {
    const newLog: AuditLogEntry = {
      id: `aud-${Date.now()}`,
      timestamp: new Date().toISOString(),
      userId: activeRole,
      userEmail: activeRole === 'superadmin' ? 'admin.global@agrotech.ai' : activeRole === 'agronomist' ? 'agronomo.senior@agricola.pe' : 'productor.campo@sanpablo.com',
      userRole: activeRole,
      action,
      resource,
      details,
      clientIp: '190.237.45.112',
      sha256Signature: Array.from({ length: 64 }, () => Math.floor(Math.random() * 16).toString(16)).join('')
    };
    setAuditLogs(prev => [newLog, ...prev]);
  };

  // Online / Offline Connectivity Toggle
  const handleToggleOnline = () => {
    if (!isOnline) {
      // Replay offline queue
      if (offlineQueue.length > 0) {
        showToast(t('app.toast.syncComplete', { count: offlineQueue.length }));
        setOfflineQueue([]);
      }
      setIsOnline(true);
    } else {
      setIsOnline(false);
      showToast(t('app.toast.offlineActivated'));
    }
  };

  // Approve Decision
  const handleApproveDecision = (decisionId: string) => {
    if (!isOnline) {
      setOfflineQueue(prev => [...prev, {
        id: `off-${Date.now()}`,
        actionType: 'approve_irrigation',
        payload: { decisionId },
        queuedAt: new Date().toISOString(),
        synced: false
      }]);
      showToast(t('app.toast.approvedOffline'));
    }

    setDecisions(prev => prev.map(d => {
      if (d.id === decisionId) {
        return {
          ...d,
          status: 'approved',
          approvedBy: activeRole === 'agronomist' ? 'Ing. Valeria Domínguez (Agrónomo)' : 'Administrador',
          approvalTimestamp: new Date().toISOString()
        };
      }
      return d;
    }));

    const dec = decisions.find(d => d.id === decisionId);
    recordAudit(
      'APPROVE_IRRIGATION_DECISION',
      `RLDecision/${decisionId} (${dec?.zoneName})`,
      `Aprobada dosis de ${dec?.recommendedDepthMm} mm. Ventana ${dec?.executionWindowHours.start}-${dec?.executionWindowHours.end}.`
    );
    showToast(t('app.toast.decisionApproved', { id: decisionId }));
  };

  // Manual Override
  const handleManualOverride = (decisionId: string, customDepthMm: number, reason: string) => {
    setDecisions(prev => prev.map(d => {
      if (d.id === decisionId) {
        return {
          ...d,
          recommendedDepthMm: customDepthMm,
          recommendedVolumeM3: Math.round((customDepthMm / 1000) * (selectedZone.areaHectares * 10000)),
          overriddenManually: true,
          overrideReason: reason,
          status: 'approved',
          approvedBy: `Anulación Manual (${activeRole})`
        };
      }
      return d;
    }));

    // Update zone recommended rate
    setZones(prev => prev.map(z => {
      if (z.id === selectedZone.id) {
        return { ...z, recommendedRateMm: customDepthMm };
      }
      return z;
    }));

    recordAudit(
      'MANUAL_OVERRIDE_VRI',
      `RLDecision/${decisionId} (${selectedZone.name})`,
      `Dosis modificada manualmente a ${customDepthMm} mm. Motivo: ${reason}`
    );
    showToast(t('app.toast.manualOverrideApplied', { depth: customDepthMm, zone: selectedZone.name }));
  };

  // Re-infer all zones with PPO RL Agent
  const handleRecomputeAllRL = () => {
    const updatedDecisions = zones.map(z => runRLPolicyInference(z, radarCells[0], sensors[0], false));
    setDecisions(updatedDecisions);
    
    // Also update zone recommended rates
    setZones(prev => prev.map(z => {
      const dec = updatedDecisions.find(d => d.zoneId === z.id);
      return dec ? { ...z, recommendedRateMm: dec.recommendedDepthMm } : z;
    }));

    recordAudit(
      'RECOMPUTE_RL_POLICY_INFERENCE',
      `AgriculturalField/${field.id}`,
      'Inferencia de política PPO-VRI ejecutada sobre las 4 zonas de manejo.'
    );
    showToast(t('app.toast.ppoInferenceComplete'));
  };

  // Direct trigger of irrigation from GIS Map
  const handleTriggerIrrigation = (zoneId: string, depthMm: number) => {
    const zone = zones.find(z => z.id === zoneId);
    if (!zone) return;

    setZones(prev => prev.map(z => {
      if (z.id === zoneId) {
        return {
          ...z,
          appliedRateMm: depthMm,
          status: 'optimal'
        };
      }
      return z;
    }));

    recordAudit(
      'EXECUTE_VRI_NOZZLE_SPRAY',
      `ManagementZone/${zoneId}`,
      `Aplicación de ${depthMm} mm iniciada en boquillas del pivot central.`
    );
    showToast(t('app.toast.irrigationDispatched', { depth: depthMm, zone: zone.name }));

    // Prepare decision for feedback evaluation
    const matchingDec = decisions.find(d => d.zoneId === zoneId) || decisions[0];
    setFeedbackDecision(matchingDec);
  };

  // Commit post-irrigation calibration to Digital Twin
  const handleCommitRecalibration = (feedback: ClosedLoopFeedback, updatedZone: ManagementZone) => {
    setZones(prev => prev.map(z => z.id === updatedZone.id ? updatedZone : z));
    setSelectedZone(updatedZone);

    // Update field savings
    setField(prev => ({
      ...prev,
      waterSavedM3Season: prev.waterSavedM3Season + Math.round((updatedZone.recommendedRateMm / 1000) * updatedZone.areaHectares * 10000 * 0.28)
    }));

    recordAudit(
      'COMMIT_CLOSED_LOOP_RECALIBRATION',
      `SoilHydraulics/${updatedZone.id}`,
      `Calibración post-riego aplicada. Ksat actualizado a ${updatedZone.saturatedK} mm/h (Ajuste: ${feedback.ksatAdjustmentPct}%).`
    );
    showToast(t('app.toast.recalibrationSaved', { zone: updatedZone.name }));
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 flex font-sans overflow-x-hidden">

      {/* Sidebar de Navegación Lateral */}
      <Sidebar
        isOpen={isSidebarOpen}
        onClose={handleCloseSidebar}
        activeTab={activeTab}
        onTabChange={setActiveTab}
      />

      {/* Columna principal: Header + Contenido + Footer */}
      <div className="flex flex-col flex-1 min-w-0">

        {/* Global Toast Notification */}
        {toastMessage && (
          <div className="fixed bottom-6 right-6 z-[60] bg-emerald-500 dark:bg-emerald-600 text-white px-4 py-3 rounded-xl shadow-2xl border-emerald-300 dark:border-emerald-400 border text-xs font-semibold flex items-center gap-2 animate-bounce">
            <span>✓</span>
            <span>{toastMessage}</span>
          </div>
        )}

        {/* Main App Header */}
        <Header
          field={field}
          activeRole={activeRole}
          onRoleChange={setActiveRole}
          systemMode={systemMode}
          onSystemModeChange={setSystemMode}
          isOnline={isOnline}
          onToggleOnline={handleToggleOnline}
          offlineQueueCount={offlineQueue.length}
          onToggleSidebar={handleToggleSidebar}
        />

        {/* Main Content Area */}
        <main className="flex-1 w-full mx-auto px-4 sm:px-6 lg:px-8 xl:px-10 py-6 max-w-none">
          <div className="max-w-7xl mx-auto">
            {activeTab === 'gis-map' && (
              <FieldGISMap
                field={field}
                zones={zones}
                sensors={sensors}
                radarCells={radarCells}
                decisions={decisions}
                selectedZone={selectedZone}
                onSelectZone={setSelectedZone}
                onTriggerIrrigation={handleTriggerIrrigation}
                systemMode={systemMode}
              />
            )}

            {activeTab === 'rl-engine' && (
              <RLDecisionConsole
                zones={zones}
                decisions={decisions}
                radarCells={radarCells}
                sensors={sensors}
                activeRole={activeRole}
                systemMode={systemMode}
                onApproveDecision={handleApproveDecision}
                onManualOverride={handleManualOverride}
                onRecomputeAllRL={handleRecomputeAllRL}
                onTriggerFeedbackModal={(dec) => setFeedbackDecision(dec)}
              />
            )}

            {activeTab === 'telemetry' && (
              <TelemetryAnalytics
                sensors={sensors}
                zones={zones}
                selectedZone={selectedZone}
              />
            )}

            {activeTab === 'what-if' && (
              <WhatIfSimulator
                zones={zones}
                selectedZone={selectedZone}
                onSelectZone={setSelectedZone}
              />
            )}

            {activeTab === 'reports' && (
              <ReportExportStudio
                field={field}
                zones={zones}
                sensors={sensors}
                decisions={decisions}
                auditLogs={auditLogs}
                scheduledReports={scheduledReports}
                currentUserName={activeRole === 'superadmin' ? 'Dr. Alejandro Morales (Superadmin)' : 'Ing. Valeria Domínguez (Agrónomo)'}
              />
            )}

            {activeTab === 'rbac-audit' && (
              <RBACAuditConsole
                users={INITIAL_USERS}
                auditLogs={auditLogs}
                activeRole={activeRole}
                onRoleChange={setActiveRole}
              />
            )}

            {activeTab === 'codebase' && (
              <ArchitectureAndCodeViewer />
            )}
          </div>
        </main>

        {/* Post-Irrigation Closed-Loop Feedback Modal */}
        {feedbackDecision && (
          <ClosedLoopFeedbackModal
            decision={feedbackDecision}
            zone={zones.find(z => z.id === feedbackDecision.zoneId) || zones[0]}
            onClose={() => setFeedbackDecision(null)}
            onCommitRecalibration={handleCommitRecalibration}
          />
        )}

        {/* Footer */}
        <footer className="border-t border-slate-200 dark:border-slate-900 bg-slate-100 dark:bg-slate-950 text-slate-600 dark:text-slate-400 py-4 px-6 text-center text-xs">
          <p>
            {t('app.footer')}
          </p>
        </footer>

        {/* Chatbot Agronómico con Groq y Voz (STT/TTS) */}
        <AgronomicChatbot
          field={field}
          zones={zones}
          decisions={decisions}
          sensors={sensors}
          radarCells={radarCells}
        />

      </div>
    </div>
  );
}
