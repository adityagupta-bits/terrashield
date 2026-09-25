import React from 'react';
import { Radio, Wifi, WifiOff, Zap, Cpu, Layers } from 'lucide-react';

export default function MeshTopologyView({
  topology = { nodes: [], links: [], network_mode: 'HYBRID_CELLULAR' },
  selectedNodeId,
  onSelectNode,
  onToggleBlackout
}) {
  const isBlackout = topology.network_mode.includes('BLACKOUT');
  const nodes = topology.nodes || [];
  const links = topology.links || [];

  // Group nodes by hop level for structured tree-mesh layout
  const nodesByHop = {};
  nodes.forEach((n) => {
    const hop = n.hop_count || 0;
    if (!nodesByHop[hop]) nodesByHop[hop] = [];
    nodesByHop[hop].push(n);
  });

  const hopLevels = Object.keys(nodesByHop).map(Number).sort((a, b) => a - b);

  return (
    <div style={{
      width: '100%',
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      background: '#ffffff',
      padding: '20px',
      overflowY: 'auto'
    }}>
      {/* Network Header Banner */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        background: isBlackout ? 'var(--accent-amber-subtle)' : 'var(--accent-primary-subtle)',
        border: `1px solid ${isBlackout ? 'var(--accent-amber-border)' : '#bae6fd'}`,
        borderRadius: 'var(--radius-md)',
        padding: '12px 18px',
        marginBottom: '20px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {isBlackout ? (
            <WifiOff size={22} color="var(--accent-amber)" />
          ) : (
            <Wifi size={22} color="var(--accent-primary)" />
          )}
          <div>
            <div style={{
              fontWeight: 700,
              fontSize: '0.9rem',
              color: isBlackout ? '#92400e' : '#0369a1'
            }}>
              {isBlackout ? '⚠️ Cellular Blackout Active: 100% Offline Decentralized LoRa Mesh' : '🌐 Hybrid Mode: Cellular Sink with Multi-Hop Mesh Relay'}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
              {isBlackout 
                ? 'Primary GSM tower severed. Packets dynamically rerouted via LoRa P2P to Emergency Satellite Sink (NODE-08).'
                : 'Primary Gateway (GW-01) active. Edge sensor packets aggregate and stream upstream.'}
            </div>
          </div>
        </div>

        <button 
          className={`btn ${isBlackout ? 'btn-primary' : 'btn-danger'}`}
          style={{ padding: '6px 14px', fontSize: '0.75rem' }}
          onClick={onToggleBlackout}
        >
          <Zap size={14} />
          {isBlackout ? 'Restore Cellular Tower' : 'Sever Cellular (Test Mesh)'}
        </button>
      </div>

      {/* Cardless Topology Stats Strip */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(4, 1fr)',
        gap: '16px',
        marginBottom: '22px',
        padding: '12px 16px',
        background: '#f8fafc',
        border: '1px solid var(--border-subtle)',
        borderRadius: 'var(--radius-md)'
      }}>
        <div>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>
            Total Network Nodes
          </div>
          <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#0f172a', fontFamily: 'JetBrains Mono' }}>
            {nodes.length}
          </div>
          <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>Distributed ESP32 units</div>
        </div>

        <div>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>
            Active Gateways
          </div>
          <div style={{ fontSize: '1.4rem', fontWeight: 800, color: isBlackout ? 'var(--accent-amber)' : 'var(--accent-emerald)', fontFamily: 'JetBrains Mono' }}>
            {topology.active_gateways || 1}
          </div>
          <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>
            {isBlackout ? 'LoRa Backup Sink' : 'GSM + WiFi Gateway'}
          </div>
        </div>

        <div>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>
            Max Hop Depth
          </div>
          <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#0f172a', fontFamily: 'JetBrains Mono' }}>
            {Math.max(0, ...hopLevels)} Hops
          </div>
          <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>P2P multi-hop tiers</div>
        </div>

        <div>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>
            Mesh Link Edges
          </div>
          <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#0284c7', fontFamily: 'JetBrains Mono' }}>
            {links.length}
          </div>
          <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>Active ad-hoc routes</div>
        </div>
      </div>

      {/* Multi-Hop Mesh Tier Visualization */}
      <div style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        gap: '16px'
      }}>
        <div style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
          Decentralized Packet Hopping Hierarchy
        </div>

        {hopLevels.map((hop) => (
          <div key={hop} style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              fontSize: '0.72rem',
              fontWeight: 700,
              color: hop === 0 ? '#0284c7' : 'var(--text-muted)'
            }}>
              <span>{hop === 0 ? 'LEVEL 0: SINK GATEWAY (GSM / SATELLITE SINK)' : `LEVEL ${hop}: RELAY NODES (+${hop} HOPS)`}</span>
              <div style={{ flex: 1, height: '1px', background: 'var(--border-subtle)' }} />
            </div>

            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
              {(nodesByHop[hop] || []).map((node) => {
                const isSelected = node.id === selectedNodeId;
                const isOffline = node.status.includes('OFFLINE');
                const isEmergencySink = node.status === 'EMERGENCY_SINK';

                return (
                  <div
                    key={node.id}
                    onClick={() => onSelectNode && onSelectNode(node.id)}
                    style={{
                      padding: '10px 14px',
                      background: isSelected 
                        ? 'var(--accent-primary-subtle)' 
                        : (isOffline ? 'var(--accent-rose-subtle)' : '#ffffff'),
                      border: `1px solid ${
                        isSelected 
                          ? '#0284c7' 
                          : (isOffline ? 'var(--accent-rose-border)' : 'var(--border-subtle)')
                      }`,
                      borderRadius: 'var(--radius-md)',
                      cursor: 'pointer',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '4px',
                      minWidth: '160px',
                      boxShadow: isSelected ? '0 0 0 2px rgba(2,132,199,0.2)' : 'var(--shadow-subtle)',
                      transition: 'all 0.15s ease'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <span style={{ fontWeight: 800, fontSize: '0.84rem', color: isOffline ? '#dc2626' : '#0f172a' }}>
                        {node.id}
                      </span>
                      <span style={{
                        fontSize: '0.62rem',
                        fontWeight: 700,
                        padding: '1px 6px',
                        borderRadius: '4px',
                        background: isOffline ? '#fee2e2' : (isEmergencySink ? '#fef3c7' : '#e0f2fe'),
                        color: isOffline ? '#dc2626' : (isEmergencySink ? '#b45309' : '#0369a1')
                      }}>
                        {node.is_gateway ? 'GATEWAY' : `${node.hazard_type.toUpperCase()}`}
                      </span>
                    </div>

                    <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)' }}>
                      {node.name.length > 22 ? `${node.name.substring(0, 20)}...` : node.name}
                    </div>

                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      fontSize: '0.68rem',
                      color: 'var(--text-muted)',
                      marginTop: '4px'
                    }}>
                      <span>Parent: <b style={{ color: '#0f172a' }}>{node.parent_node_id || 'Root'}</b></span>
                      <span>🔋 {node.battery_pct.toFixed(0)}%</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
