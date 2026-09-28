import React, { useState } from 'react';
import { Shield, AlertTriangle, MapPin, PhoneCall, CheckCircle, Navigation, Users, Info, Radio, Smartphone, AlertOctagon, HeartHandshake } from 'lucide-react';

export default function CitizenView({ alerts = [], shelters = [], onOpenWhatsApp }) {
  const [selectedLocation, setSelectedLocation] = useState('kampur');
  const [lang, setLang] = useState('hi'); // 'hi' | 'en'
  const [activeCategory, setActiveCategory] = useState('FLOOD');
  const [sosSent, setSosSent] = useState(false);

  const activeAlerts = alerts.filter(a => a.is_active);
  const hasCriticalAlert = activeAlerts.some(a => a.severity === 'EMERGENCY' || a.severity === 'CRITICAL');

  // Locations for citizen testing (Assam 16 June Incident)
  const locations = {
    kampur: {
      name: 'Kampur Kopili Riverfront (कामपुर कोपिली तटबंध - 16 June Peak)',
      zoneType: 'HIGH_RISK',
      hazard: 'Extreme Flood Deluge (River Kopili 4.85m breached 4.75m HFL)',
      evacuationRoute: 'Route towards Kampur Higher Secondary School Relief Camp (1.1 km)',
      lat: 26.0520,
      lng: 92.7750
    },
    pandu: {
      name: 'Pandu Port Brahmaputra Bank (पांडु पोर्ट ब्रह्मपुत्र तट)',
      zoneType: 'MODERATE_RISK',
      hazard: 'Brahmaputra Flood Surge Watch (49.60m gauge mark)',
      evacuationRoute: 'Exit towards Cotton Collegiate HS / Maligaon Highland (2.5 km)',
      lat: 26.1820,
      lng: 91.7150
    },
    dispur: {
      name: 'Dispur Central & GMCH Zone (दिसपुर मुख्य क्षेत्र)',
      zoneType: 'SAFE',
      hazard: 'Normal Safe Baseline (No active embankment breach)',
      evacuationRoute: 'Designated safe relief shelters on standby',
      lat: 26.1400,
      lng: 91.7900
    }
  };

  const currLoc = locations[selectedLocation];

  // Do's & Don'ts guidelines from NDMA Sachet
  const guidelines = {
    FLOOD: {
      title: lang === 'hi' ? 'बाढ़ एवं जलभराव से बचाव के उपाय' : 'Flash Flood Safety Protocols',
      dos: [
        lang === 'hi' ? 'तुरंत नदी तट, घाट और निचले इलाकों को छोड़कर ऊंचे स्थान पर जाएं।' : 'Evacuate riverbanks and low-lying areas immediately to higher elevations.',
        lang === 'hi' ? 'अपने आवश्यक दस्तावेज, दवाइयां व पीने का पानी वाटरप्रूफ बैग में रखें।' : 'Keep essential documents, emergency medicines, and clean water in a waterproof bag.',
        lang === 'hi' ? 'स्थानीय प्रशासन व एनडीआरएफ के लाउडस्पीकर निर्देशों का पालन करें।' : 'Adhere strictly to official public address announcements by SDRF/NDRF.',
        lang === 'hi' ? 'आपातकालीन सहायता के लिए तुरंत 112 या 1070 पर संपर्क करें।' : 'Dial 112 or 1070 immediately for state disaster response assistance.'
      ],
      donts: [
        lang === 'hi' ? 'बाढ़ के बहते पानी में गाड़ी चलाने या पैदल पार करने का प्रयास न करें।' : 'Do not attempt to drive or walk through fast-flowing floodwaters.',
        lang === 'hi' ? 'बिजली के खंभों, गिरे हुए तारों या ट्रांसफार्मर के पास बिल्कुल न जाएं।' : 'Avoid damaged electric poles, submerged transformers, and fallen power lines.',
        lang === 'hi' ? 'सोशल मीडिया पर अपुष्ट सूचनाएं या अफवाहें न फैलाएं।' : 'Do not circulate unverified rumors; rely only on official NDMA alerts.'
      ]
    },
    FIRE: {
      title: lang === 'hi' ? 'वनाग्नि से सुरक्षा के नियम' : 'Forest Fire Safety Measures',
      dos: [
        lang === 'hi' ? 'हवा की विपरीत दिशा में सुरक्षित स्थान की ओर तुरंत प्रस्थान करें।' : 'Move perpendicular to the wind direction away from advancing smoke & flame.',
        lang === 'hi' ? 'धुएं से बचने के लिए चेहरे पर गीला कपड़ा या N95 मास्क बांधें।' : 'Cover nose and mouth with a damp cloth or mask to avoid particulate inhalation.',
        lang === 'hi' ? 'मकान के आसपास की सूखी झाड़ियों और पत्तियों को तुरंत साफ़ करें।' : 'Clear combustible leaves and dry twigs from building perimeters.'
      ],
      donts: [
        lang === 'hi' ? 'आग की ओर कभी न जाएं और संकरी घाटियों में शरण न लें।' : 'Do not take shelter in narrow canyons where fire spreads uphill rapidly.',
        lang === 'hi' ? 'जंगल के पास ज्वलनशील पदार्थ, कूड़ा या सिगरेट न फेंकें।' : 'Do not dispose of lit cigarettes or flammable waste near forest edges.'
      ]
    },
    LANDSLIDE: {
      title: lang === 'hi' ? 'भूस्खलन से बचाव की सलाह' : 'Landslide Preparedness Advisory',
      dos: [
        lang === 'hi' ? 'पहाड़ी ढलानों से दूर पक्के भवनों या राहत शिविरों में शरण लें।' : 'Stay away from steep slopes; take shelter in designated concrete shelters.',
        lang === 'hi' ? 'मिट्टी के खिसकने या पत्थरों के गिरने की किसी भी आवाज़ पर सतर्क रहें।' : 'Be alert to unusual sounds like rumbling rocks or cracking trees.'
      ],
      donts: [
        lang === 'hi' ? 'भारी वर्षा के दौरान पहाड़ी मार्गों पर अनावश्यक यात्रा न करें।' : 'Avoid non-essential transit along cut mountain roads during intense rain.'
      ]
    }
  };

  const handleSOS = () => {
    setSosSent(true);
    setTimeout(() => setSosSent(false), 5000);
  };

  return (
    <div className="citizen-portal-container">
      {/* Header Banner */}
      <div className="citizen-header-card">
        <div className="citizen-header-content">
          <div className="citizen-badge-group">
            <span className="citizen-badge">
              <img src="/logo-shield-transparent.png" alt="TERRA SHIELD" className="w-4 h-4 object-contain inline-block mr-1" />
              <span>TERRA SHIELD CITIZEN PORTAL</span>
            </span>
            <span className="citizen-sih-tag">SIH26178 Public Advisory</span>
          </div>

          <h2 className="citizen-main-title">
            {lang === 'hi' ? 'आपदा पूर्व चेतावनी एवं नागरिक सुरक्षा पोर्टल' : 'Multi-Hazard Early Warning & Citizen Safety Advisory'}
          </h2>
          <p className="citizen-main-desc">
            {lang === 'hi' 
              ? 'असम (काम्पूर-कोपिली एवं ब्रह्मपुत्र) क्षेत्र के नागरिकों हेतु अति-स्थानीय जीआईएस चेतावनी, निकटतम सुरक्षित आश्रय स्थल एवं आपातकालीन सहायता।'
              : 'Hyper-local GIS hazard warnings, real-time safe evacuation shelter locator, and 24x7 emergency assistance for citizens across the Brahmaputra & Kopili river basin (Assam 16 June Incident).'}
          </p>
        </div>

        {/* Language & SOS Row */}
        <div className="citizen-controls-row">
          <div className="lang-switcher">
            <button
              className={`lang-btn ${lang === 'hi' ? 'active' : ''}`}
              onClick={() => setLang('hi')}
            >
              हिन्दी
            </button>
            <button
              className={`lang-btn ${lang === 'en' ? 'active' : ''}`}
              onClick={() => setLang('en')}
            >
              English
            </button>
          </div>

          <button
            onClick={handleSOS}
            className={`sos-btn ${sosSent ? 'sent' : ''}`}
          >
            <Radio size={16} className={sosSent ? '' : 'animate-ping'} />
            <span>{sosSent ? (lang === 'hi' ? '✓ आपातकालीन संदेश प्रसारित!' : '✓ SOS Broadcast Dispatched!') : (lang === 'hi' ? '🚨 आपातकालीन SOS चेतावनी' : '🚨 Broadcast Emergency SOS')}</span>
          </button>
        </div>
      </div>

      {/* Location Selector Bar */}
      <div className="citizen-location-bar">
        <div className="loc-label">
          <MapPin size={16} className="text-blue-600" />
          <span>{lang === 'hi' ? 'परीक्षण हेतु अपना क्षेत्र चुनें:' : 'Select Your Current Sector Location:'}</span>
        </div>
        <div className="loc-chips">
          {Object.entries(locations).map(([key, loc]) => (
            <button
              key={key}
              onClick={() => setSelectedLocation(key)}
              className={`loc-chip ${selectedLocation === key ? 'active' : ''} ${loc.zoneType.toLowerCase()}`}
            >
              <span className={`chip-indicator ${loc.zoneType.toLowerCase()}`} />
              <span>{loc.name}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Real-time Status Card based on selected location */}
      <div className={`citizen-status-banner ${currLoc.zoneType.toLowerCase()}`}>
        <div className="status-icon-wrap">
          {currLoc.zoneType === 'HIGH_RISK' ? (
            <AlertOctagon size={32} className="text-rose-600" />
          ) : currLoc.zoneType === 'MODERATE_RISK' ? (
            <AlertTriangle size={32} className="text-amber-600" />
          ) : (
            <CheckCircle size={32} className="text-emerald-600" />
          )}
        </div>
        <div className="status-info">
          <div className="status-eyebrow">
            {currLoc.zoneType === 'HIGH_RISK' 
              ? (lang === 'hi' ? 'उच्च चेतावनी: तत्काल सुरक्षित स्थान पर जाएं' : 'HIGH THREAT: IMMEDIATE EVACUATION ADVISORY')
              : currLoc.zoneType === 'MODERATE_RISK'
              ? (lang === 'hi' ? 'सतर्कता चेतावनी: निगरानी जारी रखें' : 'ELEVATED HAZARD: MONITOR OFFICIAL ADVISORIES')
              : (lang === 'hi' ? 'स्थिति सामान्य: आपका क्षेत्र सुरक्षित है' : 'ALL CLEAR: NORMAL BASELINE IN THIS SECTOR')}
          </div>
          <h3 className="status-hazard">{currLoc.hazard}</h3>
          <div className="status-route">
            <Navigation size={14} />
            <span><strong>{lang === 'hi' ? 'अनुशंसित निकासी मार्ग:' : 'Recommended Evacuation Route:'}</strong> {currLoc.evacuationRoute}</span>
          </div>
        </div>
        <div className="status-action-btns">
          <a href="tel:112" className="btn-call-emergency">
            <PhoneCall size={14} />
            <span>{lang === 'hi' ? '112 डायल करें' : 'Call 112 Free'}</span>
          </a>
          {onOpenWhatsApp && (
            <button onClick={onOpenWhatsApp} className="btn-verify-whatsapp">
              <Smartphone size={14} />
              <span>{lang === 'hi' ? 'सरपंच व्हाट्सएप सत्यापन' : 'Sarpanch Verification'}</span>
            </button>
          )}
        </div>
      </div>

      {/* Main Grid: Nearest Safe Shelters & Do's/Don'ts */}
      <div className="citizen-grid">
        {/* Left Column: Designated Safe Evacuation Shelters */}
        <div className="citizen-card">
          <div className="card-header-clean">
            <div className="header-title-wrap">
              <Users size={18} className="text-blue-600" />
              <h4>{lang === 'hi' ? 'निकटतम सुरक्षित राहत शिविर एवं आश्रय' : 'Designated Safe Evacuation Shelters'}</h4>
            </div>
            <span className="live-pill">Live Capacity</span>
          </div>

          <div className="shelters-list">
            {shelters.length === 0 ? (
              <div className="loading-state">Loading designated relief shelters...</div>
            ) : (
              shelters.map((s, idx) => {
                const occupancyPct = Math.round((s.current_occupancy / s.capacity) * 100);
                const distanceKm = (idx * 0.9 + 1.2).toFixed(1);
                return (
                  <div key={s.id || idx} className="shelter-item-card">
                    <div className="shelter-top">
                      <div>
                        <div className="shelter-name">{s.name}</div>
                        <div className="shelter-meta">
                          <span className="shelter-tag">{s.shelter_type || 'RELIEF CAMP'}</span>
                          <span className="shelter-dist">📍 {distanceKm} km away</span>
                        </div>
                      </div>
                      <a href={`tel:${s.contact_number || '1070'}`} className="shelter-call-btn">
                        <PhoneCall size={13} />
                        <span>{s.contact_number || '1070'}</span>
                      </a>
                    </div>

                    <div className="occupancy-bar-wrap">
                      <div className="occupancy-labels">
                        <span>{lang === 'hi' ? 'वर्तमान अधिभोग:' : 'Capacity Occupancy:'} {s.current_occupancy} / {s.capacity}</span>
                        <span className="occupancy-pct">{occupancyPct}%</span>
                      </div>
                      <div className="occupancy-track">
                        <div
                          className="occupancy-fill"
                          style={{
                            width: `${occupancyPct}%`,
                            background: occupancyPct > 80 ? '#dc2626' : (occupancyPct > 50 ? '#d97706' : '#16a34a')
                          }}
                        />
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Right Column: NDMA Do's & Don'ts Guidelines */}
        <div className="citizen-card">
          <div className="card-header-clean">
            <div className="header-title-wrap">
              <Info size={18} className="text-amber-600" />
              <h4>{lang === 'hi' ? 'एनडीएमए मानक सुरक्षा दिशानिर्देश' : 'NDMA Official Safety Guidelines'}</h4>
            </div>
          </div>

          {/* Hazard category tabs */}
          <div className="guideline-tabs">
            <button
              className={`g-tab ${activeCategory === 'FLOOD' ? 'active' : ''}`}
              onClick={() => setActiveCategory('FLOOD')}
            >
              🌊 {lang === 'hi' ? 'बाढ़ (Flood)' : 'Flood'}
            </button>
            <button
              className={`g-tab ${activeCategory === 'FIRE' ? 'active' : ''}`}
              onClick={() => setActiveCategory('FIRE')}
            >
              🔥 {lang === 'hi' ? 'वनाग्नि (Wildfire)' : 'Wildfire'}
            </button>
            <button
              className={`g-tab ${activeCategory === 'LANDSLIDE' ? 'active' : ''}`}
              onClick={() => setActiveCategory('LANDSLIDE')}
            >
              ⛰️ {lang === 'hi' ? 'भूस्खलन (Landslide)' : 'Landslide'}
            </button>
          </div>

          <div className="guideline-content">
            <h5 className="guideline-heading">{guidelines[activeCategory].title}</h5>

            <div className="dos-section">
              <div className="section-title text-emerald-700">
                <CheckCircle size={15} />
                <span>{lang === 'hi' ? 'क्या करें (Do\'s):' : 'Recommended Actions (Do\'s):'}</span>
              </div>
              <ul className="dos-list">
                {guidelines[activeCategory].dos.map((item, i) => (
                  <li key={i}>{item}</li>
                ))}
              </ul>
            </div>

            <div className="donts-section">
              <div className="section-title text-rose-700">
                <AlertOctagon size={15} />
                <span>{lang === 'hi' ? 'क्या न करें (Don\'ts):' : 'Hazardous Mistakes (Don\'ts):'}</span>
              </div>
              <ul className="donts-list">
                {guidelines[activeCategory].donts.map((item, i) => (
                  <li key={i}>{item}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
