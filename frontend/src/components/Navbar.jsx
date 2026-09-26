import React, { useState, useRef, useEffect } from 'react';
import { Shield, Radio, AlertTriangle, MessageSquare, Smartphone, Zap, Play, ChevronDown, Waves, Flame, Wind, RotateCcw, Activity } from 'lucide-react';
import { triggerSimulationScenario } from '../services/api';

export default function Navbar({
  wsConnected,
  networkMode,
  activeAlertsCount,
  onOpenWhatsApp,
  onOpenCitizenPortal,
  onToggleBlackout,
  blackoutActive,
  onScenarioTriggered,
  currentView = 'ADMIN',
  onToggleView
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
    <div className="wm-nav-wrapper">
      {/* Sleek Alert Ribbon (Watermelon Gridline Inspiration) */}
      <div className={`wm-alert-ribbon ${threatSeverity.toLowerCase()}`}>
        <div className="wm-ribbon-inner">
          <div className="wm-ribbon-tag">
            <span className="wm-tag-dot" />
            <span>{threatSeverity === 'EMERGENCY' ? 'CRITICAL ALERT' : (threatSeverity === 'CAUTION' ? 'ELEVATED WATCH' : 'SYSTEM OPTIMAL')}</span>
          </div>
          <div className="wm-ribbon-message">
            {threatSeverity === 'EMERGENCY' ? (
              <span>
                <strong>Flash Flood Warning:</strong> Upstream surge (+1.92m) detected in Shivpuri-Byasi Sector. Evacuation advisory in effect. Emergency Helplines: <strong>112</strong> / <strong>1070</strong>.
              </span>
            ) : threatSeverity === 'CAUTION' ? (
              <span>
                <strong>Hydrological Watch:</strong> Moderate rainfall across Garhwal basin. River telemetry active.
              </span>
            ) : (
              <span>
                <strong>All 20 Catchment Nodes Normal:</strong> Ganga-Chandrabhaga basin telemetry operational. Zero packet loss.
              </span>
            )}
          </div>
          <div className="wm-ribbon-meta">
            <span>Garhwal Basin</span>
            <span className="wm-meta-sep">•</span>
            <span>20 Nodes</span>
          </div>
        </div>
      </div>

      {/* Main Gridline Header Bar */}
      <header className="wm-navbar">
        {/* Left: Brand Lockup */}
        <div className="wm-brand">
          <div className="wm-brand-icon">
            <Shield size={17} strokeWidth={2.2} />
          </div>
          <div className="wm-brand-text">
            <span className="wm-brand-title">TERRA SHIELD</span>
            <span className="wm-brand-badge">SIH26178</span>
          </div>
        </div>

        {/* Center: Modern Segmented Switcher (Clean, Precision Rectangles) */}
        <div className="wm-segmented-control">
          <button
            className={`wm-segment-btn ${currentView === 'ADMIN' ? 'active' : ''}`}
            onClick={() => onToggleView && onToggleView('ADMIN')}
          >
            <Activity size={13} strokeWidth={2} />
            <span>Command Center</span>
          </button>
          <button
            className={`wm-segment-btn ${currentView === 'USER' ? 'active' : ''}`}
            onClick={() => onToggleView && onToggleView('USER')}
          >
            <Smartphone size={13} strokeWidth={2} />
            <span>Citizen Portal</span>
          </button>
        </div>

        {/* Right: Technical Badges & Controls */}
        <div className="wm-nav-right">
          {/* Telemetry WebSocket Status */}
          <div className="wm-tech-badge">
            <span className={`wm-status-dot ${wsConnected ? 'live' : 'offline'}`} />
            <span className="wm-tech-label">{wsConnected ? 'Telemetry Live' : 'Reconnecting'}</span>
          </div>

          {currentView === 'ADMIN' ? (
            <>
              {/* Network Routing Mode (Admin Command Center Only) */}
              <button
                onClick={onToggleBlackout}
                className={`wm-tech-badge clickable ${blackoutActive ? 'blackout' : ''}`}
                title="Toggle Cellular Blackout / LoRa Mesh Failover"
              >
                <Radio size={12} strokeWidth={2.2} />
                <span className="wm-tech-label">
                  {blackoutActive ? 'LoRa Mesh Failover' : 'Hybrid GSM'}
                </span>
              </button>

              {/* Scenario Simulation Trigger (Admin Command Center Only) */}
              <div className="wm-dropdown-anchor" ref={dropdownRef}>
                <button
                  className="wm-btn-dark"
                  onClick={() => setScenarioMenuOpen(!scenarioMenuOpen)}
                  disabled={simLoading}
                  title="Inject Disaster Simulation Scenarios (EOC Operators Only)"
                >
                  <Play size={11} fill="currentColor" />
                  <span>{simLoading ? 'Simulating...' : 'Simulate'}</span>
                  <ChevronDown size={12} />
                </button>

                {scenarioMenuOpen && (
                  <div className="wm-dropdown-menu">
                    <div className="wm-dropdown-title">Disaster Injections</div>

                    <button onClick={() => handleScenario('FLASH_FLOOD')} className="wm-dropdown-action">
                      <Waves size={14} className="text-sky-500" />
                      <div>
                        <div className="wm-action-head">Flash Flood Surge</div>
                        <div className="wm-action-sub">+1.92m spike in Shivpuri</div>
                      </div>
                    </button>

                    <button onClick={() => handleScenario('WILDFIRE')} className="wm-dropdown-action">
                      <Flame size={14} className="text-orange-500" />
                      <div>
                        <div className="wm-action-head">Wildfire Hotspot</div>
                        <div className="wm-action-sub">44°C heatwave in Chilla</div>
                      </div>
                    </button>

                    <button onClick={() => handleScenario('POLLUTION_SPIKE')} className="wm-dropdown-action">
                      <Wind size={14} className="text-purple-500" />
                      <div>
                        <div className="wm-action-head">Severe AQI Smog</div>
                        <div className="wm-action-sub">PM2.5 spike (345 ug/m3)</div>
                      </div>
                    </button>

                    <div className="wm-dropdown-line" />

                    <button onClick={() => handleScenario('CELLULAR_BLACKOUT')} className="wm-dropdown-action">
                      <Zap size={14} className="text-amber-500" />
                      <div>
                        <div className="wm-action-head">Cellular Blackout</div>
                        <div className="wm-action-sub">Decentralized LoRa routing</div>
                      </div>
                    </button>

                    <button onClick={() => handleScenario('RESET')} className="wm-dropdown-action">
                      <RotateCcw size={14} className="text-zinc-400" />
                      <div>
                        <div className="wm-action-head">Reset Baseline</div>
                        <div className="wm-action-sub">Restore all river levels</div>
                      </div>
                    </button>
                  </div>
                )}
              </div>

              {/* Sarpanch WhatsApp Trigger */}
              <button className="wm-btn-outline" onClick={onOpenWhatsApp} title="Launch Ground Truth Verification Bot">
                <MessageSquare size={13} className="text-emerald-600" />
                <span>WhatsApp Bot</span>
              </button>
            </>
          ) : (
            <>
              {/* Citizen-Facing Public Safety Controls (No Admin Simulation Buttons) */}
              <div className="wm-tech-badge" style={{ color: '#dc2626', borderColor: '#fecaca', background: '#fef2f2' }}>
                <span style={{ fontWeight: 700 }}>24x7 SOS: 112 / 1070</span>
              </div>

              <button className="wm-btn-outline" onClick={onOpenWhatsApp} title="Citizen WhatsApp Helpline">
                <MessageSquare size={13} className="text-emerald-600" />
                <span>WhatsApp Helpdesk</span>
              </button>
            </>
          )}
        </div>
      </header>
    </div>
  );
}
