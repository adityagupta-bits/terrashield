import React, { useState, useRef, useEffect } from 'react';
import { Shield, Radio, AlertTriangle, MessageSquare, Smartphone, Zap, Play, ChevronDown, Waves, Flame, Wind, RotateCcw } from 'lucide-react';
import { triggerSimulationScenario } from '../services/api';

export default function Navbar({
  wsConnected,
  networkMode,
  activeAlertsCount,
  onOpenWhatsApp,
  onOpenCitizenPortal,
  onToggleBlackout,
  blackoutActive,
  onScenarioTriggered
}) {
  const [scenarioMenuOpen, setScenarioMenuOpen] = useState(false);
  const [simLoading, setSimLoading] = useState(false);
  const [activeScenario, setActiveScenario] = useState(null);
  const dropdownRef = useRef(null);

  const threatSeverity = activeAlertsCount > 0 ? (activeAlertsCount >= 2 ? 'EMERGENCY' : 'CAUTION') : 'NORMAL';

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(e) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setScenarioMenuOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleScenario = async (scenario) => {
    setSimLoading(true);
    setActiveScenario(scenario);
    setScenarioMenuOpen(false);
    try {
      const res = await triggerSimulationScenario(scenario);
      if (onScenarioTriggered) onScenarioTriggered(scenario, res);
    } catch (e) {
      console.error('Failed to trigger scenario:', e);
    } finally {
      setSimLoading(false);
    }
  };

  return (
    <header className="navbar">
      {/* Brand Section */}
      <div className="brand-section">
        <div className="brand-icon">
          <Shield size={20} />
        </div>
        <div>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <span className="brand-title">TERRA SHIELD</span>
            <span className="brand-badge">SIH26178</span>
          </div>
          <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', fontWeight: 500 }}>
            Resilient AI Environmental Monitoring & Mesh Network
          </div>
        </div>
      </div>

      {/* Telemetry & Network Status */}
      <div className="nav-stats">
        {/* WebSocket Real-time Status */}
        <div className="status-pill">
          <span className={`status-indicator ${wsConnected ? 'online' : 'emergency'}`} />
          <span style={{ color: wsConnected ? 'var(--accent-emerald)' : 'var(--accent-rose)' }}>
            {wsConnected ? 'Telemetry Live' : 'Connecting...'}
          </span>
        </div>

        {/* Network Mode Status */}
        <button
          onClick={onToggleBlackout}
          className="status-pill"
          style={{
            cursor: 'pointer',
            borderColor: blackoutActive ? 'var(--accent-amber)' : 'var(--border-subtle)',
            background: blackoutActive ? 'var(--accent-amber-subtle)' : '#ffffff'
          }}
          title="Click to toggle cellular infrastructure blackout"
        >
          <Radio size={13} color={blackoutActive ? 'var(--accent-amber)' : 'var(--accent-primary)'} />
          <span style={{ color: blackoutActive ? 'var(--accent-amber)' : 'var(--text-primary)' }}>
            {blackoutActive ? 'Mesh Failover (Cellular Cut)' : 'Hybrid Cellular Uplink'}
          </span>
        </button>

        {/* Threat Level */}
        <div
          className="status-pill"
          style={{
            background: threatSeverity === 'EMERGENCY' ? 'var(--accent-rose-subtle)' : (threatSeverity === 'CAUTION' ? 'var(--accent-amber-subtle)' : '#ffffff'),
            borderColor: threatSeverity === 'EMERGENCY' ? 'var(--accent-rose-border)' : 'var(--border-subtle)'
          }}
        >
          <AlertTriangle
            size={13}
            color={threatSeverity === 'EMERGENCY' ? 'var(--accent-rose)' : (threatSeverity === 'CAUTION' ? 'var(--accent-amber)' : 'var(--accent-emerald)')}
          />
          <span>Status: </span>
          <strong
            style={{
              color: threatSeverity === 'EMERGENCY' ? 'var(--accent-rose)' : (threatSeverity === 'CAUTION' ? 'var(--accent-amber)' : 'var(--accent-emerald)')
            }}
          >
            {threatSeverity} ({activeAlertsCount})
          </strong>
        </div>
      </div>

      {/* Action Buttons & Scenario Simulator Dropdown */}
      <div className="nav-actions">
        {/* Scenario Simulator Dropdown (Clean, Cardless Alternative to Bottom Dock) */}
        <div style={{ position: 'relative' }} ref={dropdownRef}>
          <button
            className="btn btn-outline"
            onClick={() => setScenarioMenuOpen(!scenarioMenuOpen)}
            disabled={simLoading}
            style={{ fontSize: '0.8rem', padding: '6px 12px' }}
          >
            <Play size={13} color="var(--accent-primary)" />
            <span>{simLoading ? 'Simulating...' : 'Simulate Scenarios'}</span>
            <ChevronDown size={13} />
          </button>

          {scenarioMenuOpen && (
            <div style={{
              position: 'absolute',
              top: 'calc(100% + 6px)',
              right: 0,
              width: '240px',
              background: '#ffffff',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-md)',
              boxShadow: 'var(--shadow-lg)',
              zIndex: 1100,
              padding: '6px',
              display: 'flex',
              flexDirection: 'column',
              gap: '2px'
            }}>
              <div style={{
                fontSize: '0.68rem',
                fontWeight: 700,
                color: 'var(--text-muted)',
                padding: '6px 10px',
                textTransform: 'uppercase',
                letterSpacing: '0.04em'
              }}>
                Disaster Injections
              </div>

              <button
                onClick={() => handleScenario('FLASH_FLOOD')}
                style={{
                  display: 'flex', alignItems: 'center', gap: 8, padding: '8px 10px',
                  background: 'transparent', border: 'none', borderRadius: '6px',
                  cursor: 'pointer', textAlign: 'left', fontSize: '0.78rem', color: '#0f172a'
                }}
                onMouseEnter={(e) => e.currentTarget.style.background = '#f8fafc'}
                onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
              >
                <Waves size={14} color="#0284c7" />
                <div>
                  <div style={{ fontWeight: 600 }}>Flash Flood Surge</div>
                  <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>+1.9m spike in Shivpuri</div>
                </div>
              </button>

              <button
                onClick={() => handleScenario('WILDFIRE')}
                style={{
                  display: 'flex', alignItems: 'center', gap: 8, padding: '8px 10px',
                  background: 'transparent', border: 'none', borderRadius: '6px',
                  cursor: 'pointer', textAlign: 'left', fontSize: '0.78rem', color: '#0f172a'
                }}
                onMouseEnter={(e) => e.currentTarget.style.background = '#f8fafc'}
                onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
              >
                <Flame size={14} color="#ea580c" />
                <div>
                  <div style={{ fontWeight: 600 }}>Wildfire Ridge Flare</div>
                  <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>44°C heat & wind in Chilla</div>
                </div>
              </button>

              <button
                onClick={() => handleScenario('POLLUTION_SPIKE')}
                style={{
                  display: 'flex', alignItems: 'center', gap: 8, padding: '8px 10px',
                  background: 'transparent', border: 'none', borderRadius: '6px',
                  cursor: 'pointer', textAlign: 'left', fontSize: '0.78rem', color: '#0f172a'
                }}
                onMouseEnter={(e) => e.currentTarget.style.background = '#f8fafc'}
                onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
              >
                <Wind size={14} color="#7c3aed" />
                <div>
                  <div style={{ fontWeight: 600 }}>AQI Smog Surge</div>
                  <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>Severe PM2.5 in Industrial zone</div>
                </div>
              </button>

              <div style={{ height: '1px', background: 'var(--border-subtle)', margin: '4px 0' }} />

              <button
                onClick={() => handleScenario('CELLULAR_BLACKOUT')}
                style={{
                  display: 'flex', alignItems: 'center', gap: 8, padding: '8px 10px',
                  background: 'transparent', border: 'none', borderRadius: '6px',
                  cursor: 'pointer', textAlign: 'left', fontSize: '0.78rem', color: '#0f172a'
                }}
                onMouseEnter={(e) => e.currentTarget.style.background = '#f8fafc'}
                onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
              >
                <Zap size={14} color="#d97706" />
                <div>
                  <div style={{ fontWeight: 600 }}>Cellular Blackout</div>
                  <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>Force offline LoRa mesh route</div>
                </div>
              </button>

              <button
                onClick={() => handleScenario('RESET')}
                style={{
                  display: 'flex', alignItems: 'center', gap: 8, padding: '8px 10px',
                  background: 'transparent', border: 'none', borderRadius: '6px',
                  cursor: 'pointer', textAlign: 'left', fontSize: '0.78rem', color: '#0f172a'
                }}
                onMouseEnter={(e) => e.currentTarget.style.background = '#f8fafc'}
                onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
              >
                <RotateCcw size={14} color="#64748b" />
                <div>
                  <div style={{ fontWeight: 600 }}>Reset Baseline</div>
                  <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>Restore safe thresholds</div>
                </div>
              </button>
            </div>
          )}
        </div>

        {/* WhatsApp Sarpanch Bot Modal */}
        <button className="btn btn-whatsapp" onClick={onOpenWhatsApp}>
          <MessageSquare size={14} />
          <span>Sarpanch WhatsApp</span>
        </button>

        {/* Citizen Portal Modal */}
        <button className="btn btn-primary" onClick={onOpenCitizenPortal}>
          <Smartphone size={14} />
          <span>Citizen Portal</span>
        </button>
      </div>
    </header>
  );
}
