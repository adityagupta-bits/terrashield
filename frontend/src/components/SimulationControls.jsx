import React, { useState } from 'react';
import { Waves, Flame, Wind, WifiOff, RotateCcw, Play } from 'lucide-react';
import { triggerSimulationScenario } from '../services/api';

export default function SimulationControls({
  onScenarioTriggered,
  isBlackoutActive
}) {
  const [activeScenario, setActiveScenario] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleTrigger = async (scenario) => {
    setLoading(true);
    setActiveScenario(scenario);
    try {
      const res = await triggerSimulationScenario(scenario);
      if (onScenarioTriggered) onScenarioTriggered(scenario, res);
    } catch (e) {
      console.error('Failed to trigger simulation scenario', e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      background: '#ffffff',
      borderTop: '1px solid var(--border-subtle)',
      padding: '10px 18px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      gap: '16px'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <div style={{
          width: 28,
          height: 28,
          borderRadius: '6px',
          background: '#f0f9ff',
          border: '1px solid #bae6fd',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <Play size={14} color="#0284c7" />
        </div>
        <div>
          <div style={{ fontSize: '0.8rem', fontWeight: 800, color: '#0f172a' }}>
            DEMO SCENARIO SANDBOX
          </div>
          <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>
            Simulate live multi-hazard sensor spikes & resilient mesh failover cascades
          </div>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        {/* Trigger 1: Flash Flood */}
        <button
          className="btn btn-outline"
          disabled={loading}
          onClick={() => handleTrigger('FLASH_FLOOD')}
          style={{ fontSize: '0.74rem', padding: '5px 10px' }}
        >
          <Waves size={13} color="#2563eb" />
          <span>Flash Flood</span>
        </button>

        {/* Trigger 2: Wildfire */}
        <button
          className="btn btn-outline"
          disabled={loading}
          onClick={() => handleTrigger('WILDFIRE')}
          style={{ fontSize: '0.74rem', padding: '5px 10px' }}
        >
          <Flame size={13} color="#ea580c" />
          <span>Wildfire</span>
        </button>

        {/* Trigger 3: Pollution */}
        <button
          className="btn btn-outline"
          disabled={loading}
          onClick={() => handleTrigger('POLLUTION_SPIKE')}
          style={{ fontSize: '0.74rem', padding: '5px 10px' }}
        >
          <Wind size={13} color="#7c3aed" />
          <span>AQI Smog</span>
        </button>

        {/* Trigger 4: Cellular Blackout */}
        <button
          className={`btn ${isBlackoutActive ? 'btn-danger' : 'btn-outline'}`}
          disabled={loading}
          onClick={() => handleTrigger('CELLULAR_BLACKOUT')}
          style={{ fontSize: '0.74rem', padding: '5px 10px' }}
        >
          <WifiOff size={13} color={isBlackoutActive ? '#fff' : '#d97706'} />
          <span>{isBlackoutActive ? 'Cellular Cut' : 'Cut Cellular'}</span>
        </button>

        {/* Trigger 5: Reset */}
        <button
          className="btn btn-outline"
          disabled={loading}
          onClick={() => handleTrigger('RESET')}
          style={{ fontSize: '0.74rem', padding: '5px 10px' }}
        >
          <RotateCcw size={13} color="#64748b" />
          <span>Reset</span>
        </button>
      </div>
    </div>
  );
}
