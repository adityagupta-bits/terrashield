import React from 'react';
import { Droplet, Thermometer, Wind, Eye, Battery, Radio, TrendingUp, AlertTriangle } from 'lucide-react';

export default function TelemetryPanel({
  node,
  history = [],
  aiForecast = null
}) {
  if (!node) {
    return (
      <div style={{ textAlign: 'center', padding: '40px 20px', color: 'var(--text-muted)' }}>
        <Eye size={28} style={{ margin: '0 auto 10px auto', opacity: 0.5 }} />
        <p style={{ fontSize: '0.82rem' }}>Select any sensor node on the map to inspect live edge telemetry and AI forecasts.</p>
      </div>
    );
  }

  const isFloodNode = node.hazard_type === 'flood' || node.hazard_type === 'multi';
  const isFireNode = node.hazard_type === 'fire';

  // Latest historical reading
  const latest = history[history.length - 1] || {};
  const waterLevel = latest.water_level_m !== undefined ? latest.water_level_m : (node.water_level_m || 1.8);
  const waterRoc = latest.water_rate_of_change !== undefined ? latest.water_rate_of_change : (node.water_rate_of_change || 0.0);
  const tempC = latest.temperature_c !== undefined ? latest.temperature_c : (node.temperature_c || 26.5);
  const humPct = latest.humidity_pct !== undefined ? latest.humidity_pct : (node.humidity_pct || 55.0);
  const windSpd = latest.wind_speed_kmh !== undefined ? latest.wind_speed_kmh : (node.wind_speed_kmh || 12.0);

  // SVG Chart Dimensions & Data Normalization
  const chartWidth = 360;
  const chartHeight = 110;
  const padding = { top: 12, right: 12, bottom: 20, left: 32 };

  // Generate combined points for chart: actual history + AI predicted 3-hour curve
  const histPoints = history.slice(-10).map((h, idx) => ({
    x: idx,
    y: h.water_level_m !== null && h.water_level_m !== undefined ? h.water_level_m : 1.8,
    isForecast: false
  }));

  const forecastPoints = (aiForecast?.flood_forecast_3h || []).map((f, idx) => ({
    x: (histPoints.length - 1) + (idx + 1),
    y: f.predicted_water_level_m,
    isForecast: true
  }));

  const allPoints = [...histPoints, ...forecastPoints];
  const maxY = Math.max(5.5, ...allPoints.map(p => p.y));
  const minY = 0.0;
  const totalX = Math.max(1, allPoints.length - 1);

  const getCoord = (p) => {
    const x = padding.left + (p.x / totalX) * (chartWidth - padding.left - padding.right);
    const y = chartHeight - padding.bottom - ((p.y - minY) / (maxY - minY)) * (chartHeight - padding.top - padding.bottom);
    return { x, y };
  };

  // Build SVG path strings
  const histCoords = histPoints.map(getCoord);
  const forecastCoords = [
    histCoords[histCoords.length - 1],
    ...forecastPoints.map(getCoord)
  ].filter(Boolean);

  const histPath = histCoords.reduce((acc, pt, idx) => `${acc} ${idx === 0 ? 'M' : 'L'} ${pt.x} ${pt.y}`, '');
  const forecastPath = forecastCoords.reduce((acc, pt, idx) => `${acc} ${idx === 0 ? 'M' : 'L'} ${pt.x} ${pt.y}`, '');

  // Danger threshold line Y coordinate (4.0 meters)
  const dangerThresholdY = chartHeight - padding.bottom - ((4.0 - minY) / (maxY - minY)) * (chartHeight - padding.top - padding.bottom);

  const isAlertLevel = waterLevel >= 4.0;
  const isWarningLevel = waterLevel >= 2.5 && waterLevel < 4.0;

  return (
    <div className="telemetry-section" style={{ borderTop: '1px solid var(--border-subtle)' }}>
      {/* Node Header - Cardless */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <div>
          <div style={{ fontSize: '0.98rem', fontWeight: 800, color: '#0f172a' }}>
            {node.name}
          </div>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: 2 }}>
            Node ID: <b style={{ color: '#0284c7' }}>{node.id}</b> • Mesh Hops: <b>{node.hop_count}</b> • Parent: {node.parent_node_id || 'Gateway'}
          </div>
        </div>

        <span style={{
          fontSize: '0.68rem',
          fontWeight: 700,
          padding: '2px 8px',
          borderRadius: 'var(--radius-full)',
          background: node.status.includes('OFFLINE') ? 'var(--accent-rose-subtle)' : 'var(--accent-emerald-subtle)',
          color: node.status.includes('OFFLINE') ? 'var(--accent-rose)' : 'var(--accent-emerald)',
          border: `1px solid ${node.status.includes('OFFLINE') ? 'var(--accent-rose-border)' : 'var(--accent-emerald-border)'}`
        }}>
          {node.status}
        </span>
      </div>

      {/* Primary Hero Telemetry Readout (Cardless) */}
      <div className="stat-metric-hero" style={{ marginTop: 2 }}>
        <div className="label">
          {isFloodNode ? 'River Stage (Ultrasonic)' : (isFireNode ? 'Ambient Forest Temperature' : 'Primary Sensor')}
        </div>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: 10 }}>
          <span className="value" style={{
            color: isAlertLevel ? 'var(--accent-rose)' : (isWarningLevel ? 'var(--accent-amber)' : '#0f172a')
          }}>
            {isFloodNode ? waterLevel.toFixed(2) : tempC.toFixed(1)}
            <span style={{ fontSize: '1rem', fontWeight: 500, color: 'var(--text-muted)', marginLeft: 4 }}>
              {isFloodNode ? 'meters' : '°C'}
            </span>
          </span>

          {isFloodNode && (
            <span style={{
              fontSize: '0.78rem',
              fontWeight: 700,
              color: waterRoc > 0.5 ? 'var(--accent-rose)' : (waterRoc > 0 ? 'var(--accent-amber)' : 'var(--accent-emerald)')
            }}>
              {waterRoc > 0 ? `▲ +${waterRoc.toFixed(2)} m/30m` : `▼ ${waterRoc.toFixed(2)} m/30m`}
            </span>
          )}
        </div>
      </div>

      {/* Clean Inline Data Strip (No Boxed Cards) */}
      <div className="stat-grid-row">
        <div className="stat-item">
          <span className="stat-label">Power & Storage</span>
          <span className="stat-val" style={{ color: '#0f172a' }}>
            🔋 {node.battery_pct.toFixed(0)}% <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Solar Active</span>
          </span>
        </div>

        <div className="stat-item">
          <span className="stat-label">LoRa Mesh Link</span>
          <span className="stat-val" style={{ color: '#0f172a' }}>
            📶 {node.signal_rssi || -68} dBm <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>SNR +9dB</span>
          </span>
        </div>

        <div className="stat-item">
          <span className="stat-label">Ambient Conditions</span>
          <span className="stat-val" style={{ color: '#0f172a' }}>
            {tempC.toFixed(1)}°C • {humPct.toFixed(0)}% RH
          </span>
        </div>

        <div className="stat-item">
          <span className="stat-label">Wind & Rain Vector</span>
          <span className="stat-val" style={{ color: '#0f172a' }}>
            {windSpd.toFixed(1)} km/h • 14 mm/h
          </span>
        </div>
      </div>

      {/* AI 3-Hour Predictive River Curve */}
      <div>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          fontSize: '0.74rem',
          fontWeight: 700,
          color: 'var(--text-secondary)',
          marginBottom: '6px'
        }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
            <TrendingUp size={13} color="#0284c7" />
            AI 3-HOUR PREDICTIVE HYDROGRAPH
          </span>
          <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>
            <span style={{ color: '#0284c7', fontWeight: 600 }}>── Actual</span> &nbsp;
            <span style={{ color: '#7c3aed', fontWeight: 600 }}>- - - AI Projected</span>
          </span>
        </div>

        <div className="chart-container-light">
          <svg width="100%" height="100%" viewBox={`0 0 ${chartWidth} ${chartHeight}`} preserveAspectRatio="none">
            {/* Danger Level Line at 4.0m */}
            <line
              x1={padding.left}
              y1={dangerThresholdY}
              x2={chartWidth - padding.right}
              y2={dangerThresholdY}
              stroke="#dc2626"
              strokeWidth="1.2"
              strokeDasharray="3, 3"
            />
            <text x={padding.left + 4} y={dangerThresholdY - 4} fill="#dc2626" fontSize="8" fontWeight="bold">
              CRITICAL DANGER THRESHOLD (4.0m)
            </text>

            {/* Historical Telemetry Path */}
            {histPath && (
              <path
                d={histPath}
                fill="none"
                stroke="#0284c7"
                strokeWidth="2"
                strokeLinecap="round"
              />
            )}

            {/* AI 3-Hour Predicted Curve (Dashed) */}
            {forecastPath && (
              <path
                d={forecastPath}
                fill="none"
                stroke="#7c3aed"
                strokeWidth="2"
                strokeDasharray="4, 4"
                strokeLinecap="round"
              />
            )}

            {/* Render Point Dots */}
            {histCoords.map((pt, i) => (
              <circle key={`hist-${i}`} cx={pt.x} cy={pt.y} r="2.5" fill="#0284c7" />
            ))}

            {forecastCoords.slice(1).map((pt, i) => (
              <circle key={`fc-${i}`} cx={pt.x} cy={pt.y} r="3" fill="#7c3aed" />
            ))}

            {/* Y Axis Labels */}
            <text x="4" y={dangerThresholdY + 3} fill="#64748b" fontSize="8">4m</text>
            <text x="4" y={chartHeight - padding.bottom} fill="#64748b" fontSize="8">0m</text>

            {/* X Axis Labels */}
            <text x={padding.left} y={chartHeight - 4} fill="#64748b" fontSize="8">Observed</text>
            <text x={chartWidth - 65} y={chartHeight - 4} fill="#7c3aed" fontSize="8" fontWeight="bold">+3h Ahead</text>
          </svg>
        </div>
      </div>

      {/* AI Risk Assessment Callout */}
      {aiForecast && (
        <div style={{
          background: isAlertLevel ? 'var(--accent-rose-subtle)' : 'var(--accent-primary-subtle)',
          border: `1px solid ${isAlertLevel ? 'var(--accent-rose-border)' : '#bae6fd'}`,
          borderRadius: 'var(--radius-md)',
          padding: '10px 12px',
          fontSize: '0.74rem',
          display: 'flex',
          gap: '10px'
        }}>
          <AlertTriangle
            size={15}
            color={isAlertLevel ? 'var(--accent-rose)' : '#0284c7'}
            style={{ flexShrink: 0, marginTop: 1 }}
          />
          <div>
            <div style={{ fontWeight: 700, color: '#0f172a', marginBottom: 2 }}>
              Edge & AI Early Warning Assessment
            </div>
            <div style={{ color: '#475569', lineHeight: 1.45 }}>
              {aiForecast.ai_summary}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
