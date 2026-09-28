import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useStats, useAlerts, useNodes } from '../../hooks/useData';
import { useUIStore } from '../../store/uiStore';
import { MapView } from '../../components/map/MapView';
import { NodeDetailDrawer } from '../../components/nodes/NodeDetailDrawer';
import { DemoControlDock } from '../../components/demo/DemoControlDock';
import { SarpanchChatModal } from '../../components/whatsapp/SarpanchChatModal';
import { api } from '../../api/client';
import { useQueryClient } from '@tanstack/react-query';

export const Dashboard: React.FC = () => {
  const { t } = useTranslation();
  const { data: stats } = useStats();
  const { data: alerts } = useAlerts({ status: 'ACTIVE' });
  const { data: nodes } = useNodes();
  const { selectedNodeId, setSelectedNodeId } = useUIStore();
  const queryClient = useQueryClient();

  const [sarpanchModalOpen, setSarpanchModalOpen] = useState(false);
  const [selectedAlertForSarpanch, setSelectedAlertForSarpanch] = useState<any>(null);

  const criticalAlerts = alerts?.filter(a => a.severity === 'CRITICAL') || [];
  const selectedNode = nodes?.find(n => n.node_id === selectedNodeId);

  const handleAcknowledge = async (id: number) => {
    try {
      await api.updateAlertStatus(id, 'ACKNOWLEDGED');
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
      queryClient.invalidateQueries({ queryKey: ['stats'] });
    } catch (e: any) {
      alert(`Error acknowledging alert: ${e.message}`);
    }
  };

  const handleDeployNdrf = async (id: number) => {
    try {
      await api.deployNdrf(id);
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
      alert('🚨 NDRF 1st Battalion (Patgaon Guwahati) dispatched to incident coordinates!');
    } catch (e: any) {
      alert(`Error: ${e.message}`);
    }
  };

  return (
    <div className="space-y-4 pb-20">
      {/* Top Stat Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-3.5 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-medium">Active Incidents</span>
            <span className={`w-2 h-2 rounded-full ${(stats?.active_alerts ?? 0) > 0 ? 'bg-rose-500 animate-pulse' : 'bg-emerald-400'}`}></span>
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-white">{stats?.active_alerts ?? 0}</span>
            <span className="text-[11px] text-rose-400 font-medium">
              {(stats?.active_alerts ?? 0) > 0 ? `${criticalAlerts.length} Critical` : 'All normal'}
            </span>
          </div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-3.5 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-medium">Telemetry Nodes</span>
            <span className="text-[10px] text-emerald-400 font-mono bg-emerald-950/80 px-1.5 py-0.5 rounded border border-emerald-800">
              5 Hardware
            </span>
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-cyan-400">{stats?.online_nodes ?? 20}</span>
            <span className="text-[11px] text-slate-400">/ {stats?.total_nodes ?? 20} operational</span>
          </div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-3.5 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-medium">Resilient Mesh Relay</span>
            <span className="text-xs">📶</span>
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-xl font-bold font-mono text-emerald-400">
              {stats?.blackout_mode ? 'LoRa Fallback' : 'Active (Hybrid)'}
            </span>
            <span className="text-[11px] text-slate-400">
              {stats?.blackout_mode ? 'NODE-08 Rerouted' : 'P2P Synced'}
            </span>
          </div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-3.5 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-medium">72h Hazard Forecast</span>
            <span className="text-xs">🌧️</span>
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-xl font-bold font-mono text-amber-400">Moderate Risk</span>
            <span className="text-[11px] text-slate-400">GradientBoost</span>
          </div>
        </div>
      </div>

      {/* Main Grid: Interactive Map + Right-Hand Alert Feed */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 min-h-[580px]">
        {/* Left 2 Cols: Tactical Map */}
        <div className="lg:col-span-2 bg-slate-900/90 border border-slate-800 rounded-xl overflow-hidden flex flex-col shadow-lg">
          <div className="bg-slate-950/80 px-4 py-2.5 border-b border-slate-800 flex items-center justify-between text-xs">
            <div className="flex items-center gap-2">
              <span className="font-semibold text-slate-200">Brahmaputra - Kopili Basin Grid (Assam 16 June Incident)</span>
              <span className="text-slate-500">|</span>
              <span className="text-slate-400 font-mono">EPSG:4326 PostGIS Layer</span>
            </div>
            <div className="flex items-center gap-3 text-[11px]">
              <span className="flex items-center gap-1.5 text-slate-300">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 inline-block"></span> Normal
              </span>
              <span className="flex items-center gap-1.5 text-slate-300">
                <span className="w-2.5 h-2.5 rounded-full bg-amber-500 inline-block"></span> Warning
              </span>
              <span className="flex items-center gap-1.5 text-slate-300">
                <span className="w-2.5 h-2.5 rounded-full bg-rose-500 inline-block animate-ping"></span> Critical
              </span>
            </div>
          </div>

          <div className="flex-1 min-h-[480px]">
            <MapView onSelectNode={(node) => setSelectedNodeId(node.node_id)} />
          </div>
        </div>

        {/* Right 1 Col: Live Incident Priority Queue */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl overflow-hidden flex flex-col shadow-lg">
          <div className="bg-slate-950/80 px-4 py-2.5 border-b border-slate-800 flex items-center justify-between">
            <h2 className="text-xs font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-2">
              <span>🚨</span>
              <span>Priority Incident Feed</span>
            </h2>
            <span className="text-[10px] font-mono bg-rose-950 text-rose-300 border border-rose-800 px-2 py-0.5 rounded-full">
              {alerts?.length || 0} active
            </span>
          </div>

          <div className="flex-1 overflow-y-auto p-3 space-y-2.5 max-h-[520px]">
            {(!alerts || alerts.length === 0) ? (
              <div className="h-full flex flex-col items-center justify-center text-center p-6 text-slate-500 text-xs">
                <span className="text-3xl mb-2">🛡️</span>
                <p>No active critical incidents.</p>
                <p className="text-[11px] text-slate-600 mt-1">All telemetry within safe baseline thresholds.</p>
              </div>
            ) : (
              alerts.map((alert) => (
                <div
                  key={alert.id}
                  className={`p-3 rounded-lg border text-xs transition-all ${
                    alert.severity === 'CRITICAL'
                      ? 'bg-rose-950/40 border-rose-700/60 text-slate-200'
                      : alert.severity === 'WARNING'
                      ? 'bg-amber-950/40 border-amber-700/60 text-slate-200'
                      : 'bg-slate-800/60 border-slate-700 text-slate-300'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <div className="font-semibold text-white flex items-center gap-1.5">
                        <span className={`px-1.5 py-0.2 text-[10px] font-bold rounded ${
                          alert.severity === 'CRITICAL' ? 'bg-rose-600 text-white' : 'bg-amber-600 text-black'
                        }`}>
                          {alert.severity}
                        </span>
                        <span>{alert.title}</span>
                      </div>
                      <div className="text-[11px] text-slate-400 mt-1 font-mono">
                        Node: <span className="text-cyan-400">{alert.node_id}</span> • {new Date(alert.created_at).toLocaleTimeString()}
                      </div>
                    </div>
                  </div>

                  {/* Delayed alert badge if delivered after outage */}
                  {alert.delivered_after_outage && (
                    <div className="mt-2 bg-amber-900/60 border border-amber-500/60 text-amber-200 px-2 py-1 rounded text-[11px] flex items-center gap-1.5 font-mono">
                      <span>⏳</span>
                      <span>DELIVERED AFTER OUTAGE (Buffered {alert.delivery_delay_sec || 60}s in LittleFS)</span>
                    </div>
                  )}

                  <p className="mt-2 text-slate-300 text-[11px] leading-relaxed">
                    {alert.description}
                  </p>

                  {/* Actions */}
                  <div className="mt-3 pt-2 border-t border-slate-800 flex flex-wrap items-center justify-between gap-2">
                    <div className="flex items-center gap-1.5">
                      <button
                        onClick={() => handleAcknowledge(alert.id)}
                        className="bg-slate-800 hover:bg-slate-700 text-slate-300 px-2 py-1 rounded text-[11px] border border-slate-700 transition-colors"
                      >
                        Acknowledge
                      </button>
                      <button
                        onClick={() => handleDeployNdrf(alert.id)}
                        className="bg-rose-900/80 hover:bg-rose-800 text-rose-100 px-2 py-1 rounded text-[11px] border border-rose-700 transition-colors flex items-center gap-1"
                      >
                        <span>🚒</span> Deploy NDRF
                      </button>
                    </div>

                    <button
                      onClick={() => {
                        setSelectedAlertForSarpanch(alert);
                        setSarpanchModalOpen(true);
                      }}
                      className="bg-emerald-900/80 hover:bg-emerald-800 text-emerald-200 px-2 py-1 rounded text-[11px] border border-emerald-700 transition-colors flex items-center gap-1 font-medium"
                    >
                      <span>💬</span> Sarpanch Verify
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Node Detail Drawer on select */}
      {selectedNode && (
        <NodeDetailDrawer
          node={selectedNode}
          onClose={() => setSelectedNodeId('')}
        />
      )}

      {/* Interactive Bottom Demo Controls */}
      <DemoControlDock />

      {/* Sarpanch Ground Truth Verification Modal */}
      {selectedAlertForSarpanch && (
        <SarpanchChatModal
          isOpen={sarpanchModalOpen}
          onClose={() => {
            setSarpanchModalOpen(false);
            setSelectedAlertForSarpanch(null);
          }}
          incidentTitle={selectedAlertForSarpanch.title}
          villageName={selectedAlertForSarpanch.location_name || 'Kampur Revenue Circle (Assam)'}
        />
      )}
    </div>
  );
};
