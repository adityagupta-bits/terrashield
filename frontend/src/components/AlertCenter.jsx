import React from 'react';
import { AlertTriangle, BellRing, CheckCircle, ShieldAlert, Users } from 'lucide-react';

export default function AlertCenter({
  alerts = [],
  onExecuteAction,
  onOpenWhatsApp
}) {
  const activeAlerts = alerts.filter(a => a.is_active);

  if (activeAlerts.length === 0) {
    return (
      <div style={{ padding: '16px 18px', borderBottom: '1px solid var(--border-subtle)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <CheckCircle size={18} color="var(--accent-emerald)" />
          <div>
            <div style={{ fontWeight: 700, fontSize: '0.84rem', color: 'var(--accent-emerald)' }}>
              All Sectors Safe & Within Baseline
            </div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: 2 }}>
              Continuous multi-hop monitoring active across 20 sensor nodes.
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={{ padding: '14px 16px', borderBottom: '1px solid var(--border-subtle)' }}>
      <div className="section-header" style={{ padding: '0 0 10px 0' }}>
        <span style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--accent-rose)', fontWeight: 800 }}>
          <ShieldAlert size={15} />
          ACTIVE INCIDENTS ({activeAlerts.length})
        </span>
        <span className="section-badge" style={{ background: 'var(--accent-rose-subtle)', color: 'var(--accent-rose)', border: '1px solid var(--accent-rose-border)' }}>
          HIGH PRIORITY
        </span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {activeAlerts.map((alert) => {
          const isEmergency = alert.severity === 'EMERGENCY';

          return (
            <div
              key={alert.id}
              className={`alert-card ${isEmergency ? '' : 'warning'}`}
            >
              {/* Alert Title & Severity */}
              <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 8 }}>
                <div>
                  <div className="alert-card-title">
                    {alert.title}
                  </div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', marginTop: 2 }}>
                    📍 {alert.location_name} • Radius: <b>{alert.radius_km} km</b>
                  </div>
                </div>

                <span style={{
                  fontSize: '0.65rem',
                  fontWeight: 800,
                  padding: '2px 7px',
                  borderRadius: 'var(--radius-sm)',
                  background: isEmergency ? '#dc2626' : '#d97706',
                  color: '#ffffff'
                }}>
                  {alert.severity}
                </span>
              </div>

              {/* Alert Description */}
              <div style={{ fontSize: '0.75rem', color: '#334155', lineHeight: 1.45 }}>
                {alert.description}
              </div>

              {/* Human-as-a-Sensor Verification Pill */}
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '6px 10px',
                background: '#ffffff',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-sm)',
                fontSize: '0.72rem'
              }}>
                <span>
                  {alert.verified_by_human ? (
                    <span style={{ color: 'var(--accent-emerald)', fontWeight: 600 }}>
                      ✅ Ground Truth Verified by Sarpanch
                    </span>
                  ) : (
                    <span style={{ color: 'var(--accent-amber)', fontWeight: 600 }}>
                      ⏳ WhatsApp Verification Dispatched...
                    </span>
                  )}
                </span>
                <button
                  onClick={() => onOpenWhatsApp && onOpenWhatsApp(alert.id)}
                  style={{
                    background: 'transparent',
                    border: 'none',
                    color: '#0284c7',
                    fontSize: '0.7rem',
                    fontWeight: 700,
                    cursor: 'pointer',
                    textDecoration: 'underline'
                  }}
                >
                  Inspect Chat
                </button>
              </div>

              {/* Action Dispatch Buttons */}
              <div style={{ display: 'flex', gap: '8px', marginTop: 4 }}>
                <button
                  className="btn btn-danger"
                  style={{ flex: 1, padding: '5px 8px', fontSize: '0.72rem', justifyContent: 'center' }}
                  disabled={alert.evacuation_triggered}
                  onClick={() => onExecuteAction(alert.id, 'EVACUATE')}
                >
                  <BellRing size={13} />
                  {alert.evacuation_triggered ? 'Sirens Active' : 'Sound Evacuation'}
                </button>

                <button
                  className="btn btn-primary"
                  style={{ flex: 1, padding: '5px 8px', fontSize: '0.72rem', justifyContent: 'center' }}
                  disabled={alert.ndrf_dispatched}
                  onClick={() => onExecuteAction(alert.id, 'DISPATCH_NDRF')}
                >
                  <Users size={13} />
                  {alert.ndrf_dispatched ? 'NDRF Deployed' : 'Deploy NDRF'}
                </button>

                <button
                  className="btn btn-outline"
                  style={{ padding: '5px 8px', fontSize: '0.72rem' }}
                  onClick={() => onExecuteAction(alert.id, 'RESOLVE')}
                >
                  Resolve
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
