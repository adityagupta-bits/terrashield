import React, { useState } from 'react';
import { useAlerts } from '../../hooks/useData';
import { api } from '../../api/client';
import { useQueryClient } from '@tanstack/react-query';
import { SarpanchChatModal } from '../../components/whatsapp/SarpanchChatModal';

export const Alerts: React.FC = () => {
  const queryClient = useQueryClient();
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [severityFilter, setSeverityFilter] = useState<string>('');
  const [selectedAlertForSarpanch, setSelectedAlertForSarpanch] = useState<any>(null);

  const { data: alerts, isLoading } = useAlerts({
    status: statusFilter || undefined,
    severity: severityFilter || undefined
  });

  const handleUpdateStatus = async (id: number, status: string) => {
    try {
      await api.updateAlertStatus(id, status);
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
      queryClient.invalidateQueries({ queryKey: ['stats'] });
    } catch (err: any) {
      alert(`Failed to update status: ${err.message}`);
    }
  };

  const handleDeployNdrf = async (id: number) => {
    try {
      await api.deployNdrf(id);
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
      alert('🚒 NDRF quick deployment command registered!');
    } catch (err: any) {
      alert(`Error: ${err.message}`);
    }
  };

  const delayedAlertsCount = alerts?.filter(a => a.delivered_after_outage).length || 0;
  const criticalCount = alerts?.filter(a => a.severity === 'CRITICAL').length || 0;

  return (
    <div className="space-y-4 pb-12">
      {/* Header & Filter Toolbar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 bg-slate-900/90 border border-slate-800 p-4 rounded-xl">
        <div>
          <h1 className="text-lg font-bold text-white flex items-center gap-2">
            <span>🚨</span>
            <span>Incident Command & Alert Registry</span>
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Real-time hazard detection, on-device anomaly triggers, and delayed store-and-forward batch receipts.
          </p>
        </div>

        {/* Filter controls */}
        <div className="flex flex-wrap items-center gap-2">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-slate-800 text-slate-200 border border-slate-700 text-xs rounded-lg px-2.5 py-1.5 outline-none focus:border-cyan-500"
          >
            <option value="">All Statuses</option>
            <option value="ACTIVE">Active</option>
            <option value="ACKNOWLEDGED">Acknowledged</option>
            <option value="RESOLVED">Resolved</option>
          </select>

          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="bg-slate-800 text-slate-200 border border-slate-700 text-xs rounded-lg px-2.5 py-1.5 outline-none focus:border-cyan-500"
          >
            <option value="">All Severities</option>
            <option value="CRITICAL">Critical</option>
            <option value="WARNING">Warning</option>
            <option value="INFO">Info</option>
          </select>

          {(statusFilter || severityFilter) && (
            <button
              onClick={() => {
                setStatusFilter('');
                setSeverityFilter('');
              }}
              className="text-xs text-cyan-400 hover:text-cyan-300 underline px-1"
            >
              Reset
            </button>
          )}
        </div>
      </div>

      {/* Metrics Banner */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="bg-slate-900 border border-slate-800 p-3 rounded-lg">
          <div className="text-xs text-slate-400">Total Filtered Incidents</div>
          <div className="text-xl font-bold font-mono text-white mt-1">{alerts?.length || 0}</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-3 rounded-lg">
          <div className="text-xs text-slate-400">Critical Incidents</div>
          <div className="text-xl font-bold font-mono text-rose-400 mt-1">{criticalCount}</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-3 rounded-lg">
          <div className="text-xs text-slate-400">Delivered After Outage</div>
          <div className="text-xl font-bold font-mono text-amber-400 mt-1">{delayedAlertsCount}</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-3 rounded-lg">
          <div className="text-xs text-slate-400">Ground-Truth Verification</div>
          <div className="text-xl font-bold font-mono text-emerald-400 mt-1">WhatsApp Webhook Active</div>
        </div>
      </div>

      {/* Alert List Table / Cards */}
      <div className="space-y-3">
        {isLoading ? (
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-8 text-center text-slate-400 text-xs">
            Loading incident registry...
          </div>
        ) : !alerts || alerts.length === 0 ? (
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-12 text-center text-slate-500 text-sm">
            <span className="text-3xl block mb-2">🛡️</span>
            No incidents found matching the selected filters.
          </div>
        ) : (
          alerts.map((alert) => (
            <div
              key={alert.id}
              className={`bg-slate-900/90 border rounded-xl p-4 transition-all shadow-md ${
                alert.severity === 'CRITICAL'
                  ? 'border-rose-700/60'
                  : alert.severity === 'WARNING'
                  ? 'border-amber-700/60'
                  : 'border-slate-800'
              }`}
            >
              <div className="flex flex-col md:flex-row md:items-start justify-between gap-3">
                <div className="space-y-1.5 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded font-mono ${
                        alert.severity === 'CRITICAL'
                          ? 'bg-rose-600 text-white'
                          : alert.severity === 'WARNING'
                          ? 'bg-amber-600 text-black'
                          : 'bg-blue-600 text-white'
                      }`}
                    >
                      {alert.severity}
                    </span>

                    <span className="text-sm font-semibold text-white">{alert.title}</span>

                    <span
                      className={`text-[10px] font-semibold px-2 py-0.5 rounded border ${
                        alert.status === 'ACTIVE'
                          ? 'bg-rose-950 text-rose-300 border-rose-800'
                          : alert.status === 'ACKNOWLEDGED'
                          ? 'bg-amber-950 text-amber-300 border-amber-800'
                          : 'bg-emerald-950 text-emerald-300 border-emerald-800'
                      }`}
                    >
                      {alert.status}
                    </span>

                    {alert.hazard_type && (
                      <span className="text-[10px] text-slate-400 bg-slate-800 px-2 py-0.5 rounded border border-slate-700">
                        {alert.hazard_type.replace('_', ' ')}
                      </span>
                    )}
                  </div>

                  <div className="text-xs text-slate-400 font-mono flex flex-wrap items-center gap-x-3 gap-y-1">
                    <span>Node: <strong className="text-cyan-400">{alert.node_id}</strong></span>
                    <span>•</span>
                    <span>Trigger Time: {new Date(alert.created_at).toLocaleString()}</span>
                    {alert.location_name && (
                      <>
                        <span>•</span>
                        <span>Location: {alert.location_name}</span>
                      </>
                    )}
                  </div>

                  {/* Outage badge */}
                  {alert.delivered_after_outage && (
                    <div className="inline-flex items-center gap-2 bg-amber-950/80 border border-amber-500/70 text-amber-200 px-2.5 py-1 rounded-md text-xs font-mono">
                      <span>⏳</span>
                      <span>
                        DELIVERED AFTER OUTAGE — Field network was down; stored on LittleFS and forwarded ({alert.delivery_delay_sec || 60}s latency)
                      </span>
                    </div>
                  )}

                  <p className="text-xs text-slate-300 leading-relaxed pt-1">
                    {alert.description}
                  </p>
                </div>

                {/* Right Action buttons */}
                <div className="flex flex-wrap md:flex-col items-end gap-2 pt-2 md:pt-0">
                  {alert.status === 'ACTIVE' && (
                    <button
                      onClick={() => handleUpdateStatus(alert.id, 'ACKNOWLEDGED')}
                      className="bg-amber-700/80 hover:bg-amber-700 text-amber-100 px-3 py-1.5 rounded text-xs font-medium border border-amber-600 transition-colors"
                    >
                      Acknowledge
                    </button>
                  )}

                  {alert.status !== 'RESOLVED' && (
                    <button
                      onClick={() => handleUpdateStatus(alert.id, 'RESOLVED')}
                      className="bg-emerald-800/80 hover:bg-emerald-800 text-emerald-100 px-3 py-1.5 rounded text-xs font-medium border border-emerald-700 transition-colors"
                    >
                      Mark Resolved
                    </button>
                  )}

                  <button
                    onClick={() => handleDeployNdrf(alert.id)}
                    className="bg-rose-900/80 hover:bg-rose-800 text-rose-100 px-3 py-1.5 rounded text-xs font-medium border border-rose-700 transition-colors flex items-center gap-1"
                  >
                    <span>🚒</span> Deploy NDRF
                  </button>

                  <button
                    onClick={() => setSelectedAlertForSarpanch(alert)}
                    className="bg-emerald-950 hover:bg-emerald-900 text-emerald-300 border border-emerald-700/80 px-3 py-1.5 rounded text-xs font-medium transition-colors flex items-center gap-1"
                  >
                    <span>💬</span> Sarpanch Verification
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Sarpanch Chat Modal */}
      {selectedAlertForSarpanch && (
        <SarpanchChatModal
          isOpen={!!selectedAlertForSarpanch}
          onClose={() => setSelectedAlertForSarpanch(null)}
          incidentTitle={selectedAlertForSarpanch.title}
          villageName={selectedAlertForSarpanch.location_name || 'Shivpuri Panchayat'}
        />
      )}
    </div>
  );
};
