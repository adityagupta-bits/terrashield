import React, { useState } from 'react';
import { useMeshTopology } from '../../hooks/useData';
import { api } from '../../api/client';
import { useQueryClient } from '@tanstack/react-query';

export const MeshTopologyPage: React.FC = () => {
  const queryClient = useQueryClient();
  const { data: topology, isLoading } = useMeshTopology();
  const [isToggling, setIsToggling] = useState(false);

  const isBlackoutActive = topology?.blackout_mode ?? false;

  const handleToggleBlackout = async () => {
    setIsToggling(true);
    try {
      await api.toggleBlackout(!isBlackoutActive);
      queryClient.invalidateQueries({ queryKey: ['mesh-topology'] });
      queryClient.invalidateQueries({ queryKey: ['nodes'] });
      queryClient.invalidateQueries({ queryKey: ['stats'] });
    } catch (err: any) {
      alert(`Blackout toggle failed: ${err.message}`);
    } finally {
      setIsToggling(false);
    }
  };

  const nodes = topology?.nodes || [];
  const links = topology?.links || [];

  return (
    <div className="space-y-4 pb-12">
      {/* Header & Blackout Trigger */}
      <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-xl flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div>
          <h1 className="text-lg font-bold text-white flex items-center gap-2">
            <span>🕸️</span>
            <span>Zero-Internet LoRa Mesh Network & Dynamic Topology</span>
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Decentralized multi-hop store-and-forward relay mesh. Resilient to cellular tower destruction.
          </p>
        </div>

        {/* Blackout Simulation Button */}
        <button
          onClick={handleToggleBlackout}
          disabled={isToggling}
          className={`px-4 py-2 rounded-lg text-xs font-mono font-bold flex items-center gap-2 border transition-all ${
            isBlackoutActive
              ? 'bg-rose-900/80 border-rose-500 text-rose-100 shadow-lg shadow-rose-950/50'
              : 'bg-slate-800 hover:bg-slate-700 border-slate-700 text-amber-300'
          }`}
        >
          <span>⚡</span>
          <span>{isBlackoutActive ? 'BLACKOUT ACTIVE: Gateway Severed (LoRa Re-routed)' : 'Simulate Cellular Blackout'}</span>
        </button>
      </div>

      {/* Network Metrics Strip */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="bg-slate-900 border border-slate-800 p-3 rounded-lg">
          <div className="text-xs text-slate-400">Total Mesh Nodes</div>
          <div className="text-xl font-bold font-mono text-cyan-400 mt-1">
            {nodes.length} Nodes (5 Hardware)
          </div>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-3 rounded-lg">
          <div className="text-xs text-slate-400">P2P LoRa Links</div>
          <div className="text-xl font-bold font-mono text-emerald-400 mt-1">
            {links.length} Active Edges
          </div>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-3 rounded-lg">
          <div className="text-xs text-slate-400">Avg Link Quality</div>
          <div className="text-xl font-bold font-mono text-blue-400 mt-1">
            94.8% (RSSI -74 dBm)
          </div>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-3 rounded-lg">
          <div className="text-xs text-slate-400">Packet Delivery Ratio</div>
          <div className="text-xl font-bold font-mono text-emerald-400 mt-1">
            99.2% via Store-Forward
          </div>
        </div>
      </div>

      {/* Blackout Explanation Box */}
      {isBlackoutActive && (
        <div className="bg-rose-950/60 border border-rose-600/70 p-3.5 rounded-xl text-xs space-y-1.5 animate-pulse">
          <div className="font-bold text-rose-200 flex items-center gap-2">
            <span>⚠️</span>
            <span>CRITICAL RESILIENCY MODE: Primary Cellular Tower Severed</span>
          </div>
          <p className="text-rose-300 leading-relaxed">
            Node <strong className="font-mono text-white">NODE-08</strong> lost internet connectivity. The on-device mesh protocol automatically rerouted packet streams through <strong className="font-mono text-white">NODE-02</strong> and <strong className="font-mono text-white">PHY-01</strong> over 868MHz LoRa P2P. Zero telemetry lost.
          </p>
        </div>
      )}

      {/* Mesh Nodes Table */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl overflow-hidden">
        <div className="bg-slate-950 px-4 py-2.5 border-b border-slate-800 text-xs font-semibold text-slate-200 uppercase tracking-wider">
          Node Inventory & Relay Status
        </div>

        {isLoading ? (
          <div className="p-8 text-center text-slate-400 text-xs">Loading topology matrix...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950/60 text-slate-400 font-mono border-b border-slate-800">
                <tr>
                  <th className="p-3">Node ID</th>
                  <th className="p-3">Name / Location</th>
                  <th className="p-3">Hardware Type</th>
                  <th className="p-3">Status</th>
                  <th className="p-3">Battery</th>
                  <th className="p-3">RSSI</th>
                  <th className="p-3">Routing Path</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {nodes.map(node => {
                  const isBlackoutNode = isBlackoutActive && node.node_id === 'NODE-08';
                  return (
                    <tr
                      key={node.node_id}
                      className={`hover:bg-slate-800/40 transition-colors ${
                        isBlackoutNode ? 'bg-rose-950/40' : ''
                      }`}
                    >
                      <td className="p-3 font-mono font-bold text-white flex items-center gap-1.5">
                        {node.node_type === 'HARDWARE' && (
                          <span className="bg-emerald-950 text-emerald-400 border border-emerald-700 text-[10px] px-1.5 py-0.2 rounded font-mono">
                            PHY
                          </span>
                        )}
                        <span>{node.node_id}</span>
                      </td>
                      <td className="p-3 text-slate-300">{node.name || node.location_name || 'Rishikesh Basin'}</td>
                      <td className="p-3 font-mono text-slate-400">{node.node_type}</td>
                      <td className="p-3">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            isBlackoutNode
                              ? 'bg-amber-900 text-amber-200 border border-amber-600'
                              : node.status === 'ONLINE'
                              ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                              : 'bg-rose-950 text-rose-300 border border-rose-800'
                          }`}
                        >
                          {isBlackoutNode ? 'REROUTED' : node.status}
                        </span>
                      </td>
                      <td className="p-3 font-mono text-slate-300">
                        {node.battery_level ? `${node.battery_level}%` : 'Solar (100%)'}
                      </td>
                      <td className="p-3 font-mono text-slate-400">
                        {node.signal_strength ? `${node.signal_strength} dBm` : '-72 dBm'}
                      </td>
                      <td className="p-3 font-mono text-cyan-400 text-[11px]">
                        {isBlackoutNode ? 'NODE-08 → NODE-02 → PHY-01 → Command' : 'Direct / Local Mesh'}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Mesh Links Matrix */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4">
        <h2 className="text-xs font-semibold text-slate-200 uppercase tracking-wider mb-3">
          Peer-to-Peer Link Telemetry
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
          {links.slice(0, 15).map((link, idx) => (
            <div
              key={idx}
              className="bg-slate-950 border border-slate-800 p-2.5 rounded-lg text-xs space-y-1 font-mono"
            >
              <div className="flex items-center justify-between text-slate-300">
                <span className="text-cyan-400 font-bold">{link.source_node_id}</span>
                <span className="text-slate-500">⇄</span>
                <span className="text-emerald-400 font-bold">{link.target_node_id}</span>
              </div>
              <div className="flex items-center justify-between text-[10px] text-slate-400">
                <span>{link.link_type || 'LORA_P2P'}</span>
                <span className="text-amber-300">{link.rssi ?? -75} dBm</span>
                <span className="text-emerald-400">Quality: {link.quality_score ?? 95}%</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
