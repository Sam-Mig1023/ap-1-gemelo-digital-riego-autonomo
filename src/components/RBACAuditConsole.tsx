import React, { useState } from 'react';
import { 
  ShieldCheck, 
  Key, 
  Lock, 
  Users, 
  FileText, 
  CheckCircle, 
  XCircle, 
  Hash, 
  Search,
  Terminal
} from 'lucide-react';
import { UserRole, UserProfile, AuditLogEntry } from '../types';
import { useLanguage } from '../contexts/LanguageContext';

interface RBACAuditConsoleProps {
  users: UserProfile[];
  auditLogs: AuditLogEntry[];
  activeRole: UserRole;
  onRoleChange: (role: UserRole) => void;
}

export const RBACAuditConsole: React.FC<RBACAuditConsoleProps> = ({
  users,
  auditLogs,
  activeRole,
  onRoleChange
}) => {
  const { t } = useLanguage();
  const [searchTerm, setSearchTerm] = useState<string>('');

  const permissionsMatrix = [
    { permission: t('rbac.permissions.matrix.0'), superadmin: true, agronomist: true, farmer: true, field_technician: true, rl_agent_system: true },
    { permission: t('rbac.permissions.matrix.1'), superadmin: true, agronomist: true, farmer: true, field_technician: false, rl_agent_system: false },
    { permission: t('rbac.permissions.matrix.2'), superadmin: true, agronomist: true, farmer: true, field_technician: false, rl_agent_system: false },
    { permission: t('rbac.permissions.matrix.3'), superadmin: true, agronomist: true, farmer: false, field_technician: false, rl_agent_system: false },
    { permission: t('rbac.permissions.matrix.4'), superadmin: true, agronomist: true, farmer: false, field_technician: false, rl_agent_system: true },
    { permission: t('rbac.permissions.matrix.5'), superadmin: true, agronomist: false, farmer: false, field_technician: true, rl_agent_system: false },
    { permission: t('rbac.permissions.matrix.6'), superadmin: true, agronomist: false, farmer: false, field_technician: false, rl_agent_system: false },
  ];

  const filteredLogs = auditLogs.filter(log => 
    log.action.toLowerCase().includes(searchTerm.toLowerCase()) ||
    log.userEmail.toLowerCase().includes(searchTerm.toLowerCase()) ||
    log.details.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      
      {/* Top Banner */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-4 sm:p-5 rounded-2xl flex flex-wrap items-center justify-between gap-4 shadow-xl">
        <div className="flex items-center gap-3.5">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-700 flex items-center justify-center shadow-lg shadow-indigo-950/50 border border-indigo-400/40">
            <ShieldCheck className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white tracking-tight">
              {t('rbac.title')}
            </h2>
            <p className="text-xs text-slate-600 dark:text-slate-400 mt-0.5">
              {t('rbac.subtitle')}
            </p>
          </div>
        </div>
      </div>

      {/* Permissions Matrix */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-4 sm:p-5 rounded-2xl space-y-4 shadow-xl">
        <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-3">
          <div className="flex items-center gap-2">
            <Key className="w-4 h-4 text-indigo-400" />
            <h3 className="text-sm font-bold text-slate-900 dark:text-white">{t('rbac.permissions.title')}</h3>
          </div>
          <span className="text-xs text-slate-600 dark:text-slate-400">
            {t('rbac.permissions.subtitle')}
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 dark:bg-slate-950 text-slate-600 dark:text-slate-400 font-semibold border-b border-slate-200 dark:border-slate-800">
              <tr>
                <th className="p-3">{t('rbac.permissions.columns.permission')}</th>
                <th className="p-3 text-center">{t('rbac.permissions.columns.superadmin')}</th>
                <th className="p-3 text-center">{t('rbac.permissions.columns.agronomist')}</th>
                <th className="p-3 text-center">{t('rbac.permissions.columns.farmer')}</th>
                <th className="p-3 text-center">{t('rbac.permissions.columns.technician')}</th>
                <th className="p-3 text-center">{t('rbac.permissions.columns.agent')}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 dark:divide-slate-800 text-slate-700 dark:text-slate-300">
              {permissionsMatrix.map((item, i) => (
                <tr key={i} className="hover:bg-slate-100/50 dark:hover:bg-slate-800/50 transition-colors">
                  <td className="p-3 font-medium text-slate-800 dark:text-slate-200">{item.permission}</td>
                  
                  <td className="p-3 text-center">
                    {item.superadmin ? (
                      <CheckCircle className="w-4 h-4 text-emerald-400 mx-auto" />
                    ) : (
                      <XCircle className="w-4 h-4 text-slate-600 mx-auto" />
                    )}
                  </td>
                  
                  <td className="p-3 text-center">
                    {item.agronomist ? (
                      <CheckCircle className="w-4 h-4 text-emerald-400 mx-auto" />
                    ) : (
                      <XCircle className="w-4 h-4 text-slate-600 mx-auto" />
                    )}
                  </td>

                  <td className="p-3 text-center">
                    {item.farmer ? (
                      <CheckCircle className="w-4 h-4 text-emerald-400 mx-auto" />
                    ) : (
                      <XCircle className="w-4 h-4 text-slate-600 mx-auto" />
                    )}
                  </td>

                  <td className="p-3 text-center">
                    {item.field_technician ? (
                      <CheckCircle className="w-4 h-4 text-emerald-400 mx-auto" />
                    ) : (
                      <XCircle className="w-4 h-4 text-slate-600 mx-auto" />
                    )}
                  </td>

                  <td className="p-3 text-center">
                    {item.rl_agent_system ? (
                      <CheckCircle className="w-4 h-4 text-emerald-400 mx-auto" />
                    ) : (
                      <XCircle className="w-4 h-4 text-slate-600 mx-auto" />
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Immutable Audit Trail Table */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-4 sm:p-5 rounded-2xl space-y-4 shadow-xl">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 dark:border-slate-800 pb-3">
          <div className="flex items-center gap-2">
            <Hash className="w-4 h-4 text-emerald-400" />
            <h3 className="text-sm font-bold text-slate-900 dark:text-white">{t('rbac.audit.title')}</h3>
          </div>

          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-600 dark:text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder={t('rbac.audit.searchPlaceholder')}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-slate-100 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-900 dark:text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 w-48 sm:w-64"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 dark:bg-slate-950 text-slate-600 dark:text-slate-400 font-semibold border-b border-slate-200 dark:border-slate-800">
              <tr>
                <th className="p-3">{t('rbac.audit.columns.timestamp')}</th>
                <th className="p-3">{t('rbac.audit.columns.userRole')}</th>
                <th className="p-3">{t('rbac.audit.columns.action')}</th>
                <th className="p-3">{t('rbac.audit.columns.resource')}</th>
                <th className="p-3">{t('rbac.audit.columns.details')}</th>
                <th className="p-3">{t('rbac.audit.columns.signature')}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 dark:divide-slate-800 text-slate-700 dark:text-slate-300">
              {filteredLogs.map((log) => (
                <tr key={log.id} className="hover:bg-slate-100/50 dark:hover:bg-slate-800/50 transition-colors">
                  <td className="p-3 font-mono text-slate-600 dark:text-slate-400 whitespace-nowrap">
                    {new Date(log.timestamp).toLocaleTimeString('es-PE')}
                  </td>
                  <td className="p-3">
                    <span className="font-semibold text-slate-900 dark:text-white block">{log.userEmail}</span>
                    <span className="text-[10px] text-indigo-400 uppercase font-mono">
                      {log.userRole === 'superadmin' ? t('rbac.audit.roles.superadmin') :
                       log.userRole === 'agronomist' ? t('rbac.audit.roles.agronomist') :
                       log.userRole === 'farmer' ? t('rbac.audit.roles.farmer') :
                       log.userRole === 'field_technician' ? t('rbac.audit.roles.technician') :
                       log.userRole === 'rl_agent_system' ? t('rbac.audit.roles.agent') :
                       log.userRole}
                    </span>
                  </td>
                  <td className="p-3 font-mono font-bold text-emerald-400">{log.action}</td>
                  <td className="p-3 text-slate-700 dark:text-slate-300 font-mono text-[11px]">{log.resource}</td>
                  <td className="p-3 text-slate-700 dark:text-slate-300 max-w-xs">{log.details}</td>
                  <td className="p-3 font-mono text-[10px] text-slate-500 truncate max-w-[120px]" title={log.sha256Signature}>
                    {log.sha256Signature.substring(0, 16)}...
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
