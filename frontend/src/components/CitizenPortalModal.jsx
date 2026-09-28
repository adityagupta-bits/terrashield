import React, { useState, useEffect } from 'react';
import { X, Smartphone, ShieldCheck, AlertOctagon } from 'lucide-react';
import { checkCitizenLocation } from '../services/api';

export default function CitizenPortalModal({ isOpen, onClose }) {
  const [lang, setLang] = useState('hi'); // 'en', 'hi'
  const [coords, setCoords] = useState({ lat: 26.1850, lon: 91.7500 });
  const [riskData, setRiskData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      checkRisk(coords.lat, coords.lon);
    }
  }, [isOpen, coords]);

  const checkRisk = async (lat, lon) => {
    setLoading(true);
    try {
      const data = await checkCitizenLocation(lat, lon);
      setRiskData(data);
    } catch (e) {
      console.error('Failed to check citizen risk', e);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  // Localized texts
  const translations = {
    en: {
      title: 'Citizen Disaster Safety Portal',
      subtitle: 'Hyper-Local Geofenced Early Warning System (Assam 16 June Incident)',
      safeStatus: 'YOUR ZONE IS SAFE',
      dangerStatus: 'EMERGENCY EVACUATION WARNING',
      cautionStatus: 'ELEVATED HAZARD CAUTION',
      nearestShelters: 'Designated Safe Evacuation Shelters',
      emergencyHelplines: 'Disaster Emergency Helplines',
      callNow: 'Call Free',
      changeLocation: 'Test Sector Location:',
      safeZone: 'Dispur Central (Safe)',
      floodZone: 'Kampur Kopili Riverfront (Flood Deluge)',
      fireZone: 'Karbi Anglong Slope (Slope Warning)'
    },
    hi: {
      title: 'नागरिक आपदा सुरक्षा पोर्टल',
      subtitle: 'अति-स्थानीय जीपीएस पूर्व चेतावनी प्रणाली (असम 16 जून घटना)',
      safeStatus: 'आपका क्षेत्र सुरक्षित है',
      dangerStatus: 'आपातकालीन निकासी चेतावनी',
      cautionStatus: 'सतर्कता चेतावनी: निगरानी जारी',
      nearestShelters: 'निकटतम सुरक्षित राहत शिविर व आश्रय',
      emergencyHelplines: 'आपदा आपातकालीन हेल्पलाइन',
      callNow: 'कॉल करें',
      changeLocation: 'परीक्षण हेतु क्षेत्र चुनें:',
      safeZone: 'दिसपुर मुख्य नगर (सुरक्षित)',
      floodZone: 'कामपुर कोपिली तटबंध (बाढ़ प्रभावित)',
      fireZone: 'कार्बी आंगलोंग ढलान (ढलान चेतावनी)'
    }
  };

  const t = translations[lang] || translations.hi;
  const isDanger = riskData?.status === 'DANGER';
  const isCaution = riskData?.status === 'CAUTION';

  return (
    <div className="modal-overlay">
      <div className="modal-content" style={{ maxWidth: '420px', borderRadius: '18px', border: '1px solid var(--border-subtle)' }}>
        {/* Mobile Device Frame Header */}
        <div style={{
          background: '#ffffff',
          padding: '14px 18px',
          borderBottom: '1px solid var(--border-subtle)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <div style={{ width: 28, height: 28, borderRadius: '6px', background: '#f0f9ff', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Smartphone size={16} color="#0284c7" />
            </div>
            <div>
              <div style={{ fontWeight: 800, fontSize: '0.88rem', color: '#0f172a' }}>{t.title}</div>
              <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>SIH26178 Citizen Mobile App</div>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <select
              value={lang}
              onChange={(e) => setLang(e.target.value)}
              style={{
                background: '#f8fafc',
                color: '#0f172a',
                border: '1px solid #cbd5e1',
                borderRadius: '6px',
                padding: '3px 8px',
                fontSize: '0.72rem',
                outline: 'none',
                fontWeight: 600
              }}
            >
              <option value="hi">हिन्दी</option>
              <option value="en">English</option>
            </select>
            <button
              onClick={onClose}
              style={{ background: 'transparent', border: 'none', color: '#64748b', cursor: 'pointer' }}
            >
              <X size={18} />
            </button>
          </div>
        </div>

        {/* Mobile Body */}
        <div className="modal-body" style={{ padding: '16px', gap: '14px', background: '#f8fafc' }}>
          {/* Quick Location Switcher */}
          <div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', fontWeight: 600 }}>{t.changeLocation}</div>
            <div style={{ display: 'flex', gap: 6, marginTop: 4 }}>
              <button
                className="btn btn-outline"
                style={{ flex: 1, padding: '5px', fontSize: '0.68rem', justifyContent: 'center' }}
                onClick={() => setCoords({ lat: 26.1850, lon: 91.7500 })}
              >
                {t.safeZone}
              </button>
              <button
                className="btn btn-outline"
                style={{ flex: 1, padding: '5px', fontSize: '0.68rem', borderColor: '#fca5a5', color: '#dc2626', justifyContent: 'center' }}
                onClick={() => setCoords({ lat: 26.0520, lon: 92.7750 })}
              >
                {t.floodZone}
              </button>
            </div>
          </div>

          {/* Citizen Threat Banner */}
          <div style={{
            background: isDanger ? '#fef2f2' : (isCaution ? '#fffbeb' : '#f0fdf4'),
            border: `1.5px solid ${isDanger ? '#fca5a5' : (isCaution ? '#fde68a' : '#bbf7d0')}`,
            borderRadius: '12px',
            padding: '16px 14px',
            textAlign: 'center',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '6px'
          }}>
            {isDanger ? (
              <AlertOctagon size={40} color="#dc2626" />
            ) : (
              <ShieldCheck size={40} color={isCaution ? '#d97706' : '#16a34a'} />
            )}

            <div style={{
              fontWeight: 800,
              fontSize: '1rem',
              color: isDanger ? '#991b1b' : (isCaution ? '#92400e' : '#166534')
            }}>
              {isDanger ? t.dangerStatus : (isCaution ? t.cautionStatus : t.safeStatus)}
            </div>

            <div style={{ fontSize: '0.78rem', color: '#334155', lineHeight: 1.4 }}>
              {riskData?.advisory || 'Checking environmental parameters...'}
            </div>

            <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginTop: 2 }}>
              GPS: {coords.lat.toFixed(4)}°N, {coords.lon.toFixed(4)}°E
            </div>
          </div>

          {/* Nearest Evacuation Shelters */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            <div style={{ fontSize: '0.74rem', fontWeight: 700, color: 'var(--text-secondary)' }}>
              {t.nearestShelters}
            </div>

            {(riskData?.nearest_shelters || []).map((shelter) => (
              <div
                key={shelter.id}
                style={{
                  background: '#ffffff',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: '8px',
                  padding: '10px 12px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  boxShadow: '0 1px 2px rgba(0,0,0,0.04)'
                }}
              >
                <div>
                  <div style={{ fontWeight: 700, fontSize: '0.8rem', color: '#0f172a' }}>
                    {shelter.name}
                  </div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                    📍 Distance: <b style={{ color: '#0f172a' }}>{shelter.distance_km} km</b> | Spots: <b style={{ color: '#16a34a' }}>{shelter.available_spots}</b>
                  </div>
                </div>
                <button
                  style={{
                    background: '#f0fdf4',
                    border: '1px solid #bbf7d0',
                    color: '#15803d',
                    borderRadius: '6px',
                    padding: '4px 10px',
                    fontSize: '0.7rem',
                    fontWeight: 700,
                    cursor: 'pointer'
                  }}
                >
                  Navigate
                </button>
              </div>
            ))}
          </div>

          {/* Emergency Helpline Numbers */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6, marginTop: 2 }}>
            <div style={{ fontSize: '0.74rem', fontWeight: 700, color: 'var(--text-secondary)' }}>
              {t.emergencyHelplines}
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
              <div style={{
                background: '#ffffff',
                border: '1px solid #fecaca',
                padding: '8px',
                borderRadius: '8px',
                textAlign: 'center'
              }}>
                <div style={{ fontSize: '0.68rem', color: '#991b1b', fontWeight: 600 }}>NDRF Control</div>
                <div style={{ fontWeight: 800, fontSize: '0.95rem', color: '#dc2626' }}>1078</div>
              </div>
              <div style={{
                background: '#ffffff',
                border: '1px solid #bae6fd',
                padding: '8px',
                borderRadius: '8px',
                textAlign: 'center'
              }}>
                <div style={{ fontSize: '0.68rem', color: '#0369a1', fontWeight: 600 }}>State Disaster Helpline</div>
                <div style={{ fontWeight: 800, fontSize: '0.95rem', color: '#0284c7' }}>1070</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
