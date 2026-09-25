import React, { useState, useEffect } from 'react';
import { api } from '../../api/client';
import { useQuery } from '@tanstack/react-query';

const PRESET_ZONES = [
  { name: 'Shivpuri River Basin', lat: 30.1350, lng: 78.3880, radius: 10 },
  { name: 'Tapovan / Lakshman Jhula', lat: 30.1280, lng: 78.3240, radius: 5 },
  { name: 'Byasi Flash-Flood Gorge', lat: 30.0869, lng: 78.2676, radius: 12 },
  { name: 'Chilla Forest Range', lat: 29.9800, lng: 78.2200, radius: 15 }
];

const TEMPLATES = [
  {
    id: 'FLASH_FLOOD_EVACUATION',
    title: 'Flash Flood Immediate Evacuation',
    severity: 'CRITICAL',
    en: 'URGENT EVACUATION: Water level surge detected in riverbed. Flash flood imminent. Evacuate immediately to designated relief shelters on higher ground. Do not attempt to cross bridges.',
    hi: 'अति आवश्यक चेतावनी: नदी में अचानक जलस्तर बढ़ने से बाढ़ का खतरा। तुरंत नजदीकी ऊंचे राहत शिविरों में पहुंचे। पुल पार करने का प्रयास न करें।'
  },
  {
    id: 'WILDFIRE_ALERT',
    title: 'Wildfire Proximity Warning',
    severity: 'CRITICAL',
    en: 'WILDFIRE ALERT: Rapidly spreading forest fire detected within your sector. Evacuate via main road towards civil shelters. Follow emergency authority instructions.',
    hi: 'दावानल चेतावनी: आपके क्षेत्र में तीव्र वन अग्नि फैल रही है। मुख्य सड़क मार्ग से सुरक्षित राहत शिविर की ओर प्रस्थान करें।'
  },
  {
    id: 'AIR_QUALITY_SMOKE',
    title: 'Hazardous Smoke & Gas Advisory',
    severity: 'WARNING',
    en: 'AIR QUALITY WARNING: Extreme particulate and smoke density detected. Keep doors and windows sealed. Wear N95 masks if outdoors.',
    hi: 'वायु गुणवत्ता चेतावनी: अत्यधिक धुआं व प्रदूषण स्तर दर्ज किया गया। घरों के दरवाजे खिड़कियां बंद रखें। बाहर निकलने पर मास्क पहनें।'
  },
  {
    id: 'ALL_CLEAR',
    title: 'All Clear / Threat Subsided',
    severity: 'INFO',
    en: 'ALL CLEAR: Environmental hazard levels have stabilized below critical thresholds. Emergency responders are standing down.',
    hi: 'खतरा टल गया: आपदा की स्थिति सामान्य हो गई है। आपातकालीन सेवाएं निगरानी बनाए हुए हैं।'
  }
];

export const Broadcast: React.FC = () => {
  const [lat, setLat] = useState(30.0869);
  const [lng, setLng] = useState(78.2676);
  const [radiusKm, setRadiusKm] = useState(10);
  const [selectedTemplateId, setSelectedTemplateId] = useState('FLASH_FLOOD_EVACUATION');
  const [isSending, setIsSending] = useState(false);
  const [broadcastResult, setBroadcastResult] = useState<any>(null);

  // Live Recipient Count fetched via PostGIS ST_DWithin preview endpoint
  const { data: preview, isFetching: isPreviewLoading } = useQuery({
    queryKey: ['broadcast-preview', lat, lng, radiusKm],
    queryFn: () => api.getBroadcastPreview(lat, lng, radiusKm),
    staleTime: 5000
  });

  const selectedTemplate = TEMPLATES.find(t => t.id === selectedTemplateId) || TEMPLATES[0];

  const handleDispatch = async () => {
    if (!confirm(`Confirm dispatching emergency alert to ${preview?.recipients_count ?? 0} registered citizens in a ${radiusKm}km radius?`)) {
      return;
    }

    setIsSending(true);
    setBroadcastResult(null);
    try {
      const res = await api.sendBroadcast({
        lat,
        lng,
        radius_km: radiusKm,
        template_id: selectedTemplateId
      });
      setBroadcastResult(res);
      alert(`✅ Emergency broadcast successfully initiated! Delivered to ${res.recipients_dispatched ?? res.recipients_count} citizens.`);
    } catch (err: any) {
      alert(`Broadcast failed: ${err.message}`);
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="space-y-4 pb-12">
      {/* Header */}
      <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-xl">
        <h1 className="text-lg font-bold text-white flex items-center gap-2">
          <span>📢</span>
          <span>Targeted Multi-Channel Emergency Broadcast</span>
        </h1>
        <p className="text-xs text-slate-400 mt-0.5">
          PostGIS geospatial perimeter calculation for SMS, WhatsApp Bot, and sirens. No manual estimates.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Left 5 Cols: Geo-Targeting Controls */}
        <div className="lg:col-span-5 bg-slate-900/90 border border-slate-800 rounded-xl p-4 space-y-4">
          <h2 className="text-xs font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-1.5">
            <span>📍</span>
            <span>1. Geospatial Incident Epicenter</span>
          </h2>

          {/* Presets */}
          <div>
            <label className="text-xs text-slate-400 mb-1.5 block">Quick Sector Presets</label>
            <div className="grid grid-cols-2 gap-2">
              {PRESET_ZONES.map((p, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                    setLat(p.lat);
                    setLng(p.lng);
                    setRadiusKm(p.radius);
                  }}
                  className="text-left bg-slate-800 hover:bg-slate-700 text-slate-300 p-2 rounded-lg text-xs border border-slate-700 transition-colors"
                >
                  <div className="font-semibold text-white">{p.name}</div>
                  <div className="text-[10px] text-slate-400 font-mono mt-0.5">{p.radius}km radius</div>
                </button>
              ))}
            </div>
          </div>

          {/* Coordinate inputs */}
          <div className="grid grid-cols-2 gap-3 pt-2">
            <div>
              <label className="text-xs text-slate-400 block mb-1">Center Latitude</label>
              <input
                type="number"
                step="0.0001"
                value={lat}
                onChange={(e) => setLat(parseFloat(e.target.value) || 0)}
                className="w-full bg-slate-800 text-white font-mono text-xs px-3 py-2 rounded-lg border border-slate-700 outline-none focus:border-cyan-500"
              />
            </div>
            <div>
              <label className="text-xs text-slate-400 block mb-1">Center Longitude</label>
              <input
                type="number"
                step="0.0001"
                value={lng}
                onChange={(e) => setLng(parseFloat(e.target.value) || 0)}
                className="w-full bg-slate-800 text-white font-mono text-xs px-3 py-2 rounded-lg border border-slate-700 outline-none focus:border-cyan-500"
              />
            </div>
          </div>

          {/* Radius Slider */}
          <div className="pt-2">
            <div className="flex items-center justify-between text-xs mb-1">
              <span className="text-slate-400">Broadcast Radius:</span>
              <span className="text-cyan-400 font-mono font-bold">{radiusKm} km</span>
            </div>
            <input
              type="range"
              min="1"
              max="50"
              value={radiusKm}
              onChange={(e) => setRadiusKm(parseInt(e.target.value))}
              className="w-full accent-cyan-400 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-500 font-mono mt-1">
              <span>1 km (Local)</span>
              <span>25 km (District)</span>
              <span>50 km (Regional)</span>
            </div>
          </div>

          {/* PostGIS ST_DWithin live calculation card */}
          <div className="bg-slate-950 border border-slate-800 rounded-xl p-3.5 space-y-2">
            <div className="text-[11px] text-slate-400 flex items-center justify-between">
              <span>PostGIS Spatial Calculation:</span>
              <span className="text-[10px] font-mono text-slate-500">ST_DWithin (geography)</span>
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-bold font-mono text-emerald-400">
                {isPreviewLoading ? '...' : (preview?.recipients_count ?? 0)}
              </span>
              <span className="text-xs text-slate-300">Registered Citizens In Zone</span>
            </div>
            <div className="text-[10px] text-slate-500">
              Targeted across 12 mobile cells with zero spam to unaffected downstream regions.
            </div>
          </div>
        </div>

        {/* Right 7 Cols: Template and Live Bilingual CAP Preview */}
        <div className="lg:col-span-7 bg-slate-900/90 border border-slate-800 rounded-xl p-4 space-y-4">
          <h2 className="text-xs font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-1.5">
            <span>📝</span>
            <span>2. Standard Bilingual CAP Template</span>
          </h2>

          {/* Template Selection Pills */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {TEMPLATES.map((tmpl) => (
              <button
                key={tmpl.id}
                onClick={() => setSelectedTemplateId(tmpl.id)}
                className={`text-left p-2.5 rounded-lg border text-xs transition-all ${
                  selectedTemplateId === tmpl.id
                    ? 'bg-cyan-950/70 border-cyan-500 text-white shadow'
                    : 'bg-slate-800/60 hover:bg-slate-800 border-slate-700 text-slate-300'
                }`}
              >
                <div className="font-semibold flex items-center gap-1.5">
                  <span className={`w-2 h-2 rounded-full ${tmpl.severity === 'CRITICAL' ? 'bg-rose-500' : tmpl.severity === 'WARNING' ? 'bg-amber-500' : 'bg-emerald-500'}`}></span>
                  <span>{tmpl.title}</span>
                </div>
                <div className="text-[10px] text-slate-400 font-mono mt-1">{tmpl.id}</div>
              </button>
            ))}
          </div>

          {/* Dual Language Phone Broadcast Preview */}
          <div className="space-y-3 pt-2">
            {/* English Preview */}
            <div className="bg-slate-950 border border-slate-800 rounded-lg p-3 space-y-1">
              <div className="flex items-center justify-between text-[11px] text-slate-400 border-b border-slate-800 pb-1 font-mono">
                <span>ENGLISH (Cell Broadcast / SMS)</span>
                <span>{selectedTemplate.en.length} characters</span>
              </div>
              <p className="text-xs text-slate-200 leading-relaxed font-sans pt-1">
                {selectedTemplate.en}
              </p>
            </div>

            {/* Hindi Preview */}
            <div className="bg-slate-950 border border-slate-800 rounded-lg p-3 space-y-1">
              <div className="flex items-center justify-between text-[11px] text-slate-400 border-b border-slate-800 pb-1 font-mono">
                <span>HINDI (हिंदी प्रसारण)</span>
                <span>{selectedTemplate.hi.length} characters</span>
              </div>
              <p className="text-xs text-slate-200 leading-relaxed font-sans pt-1">
                {selectedTemplate.hi}
              </p>
            </div>
          </div>

          {/* Dispatch Action */}
          <div className="pt-3 border-t border-slate-800 flex items-center justify-between">
            <div className="text-xs text-slate-400">
              Targeted Audience: <strong className="text-white font-mono">{preview?.recipients_count ?? 0} Citizens</strong>
            </div>

            <button
              onClick={handleDispatch}
              disabled={isSending || (preview?.recipients_count ?? 0) === 0}
              className="bg-rose-600 hover:bg-rose-500 active:bg-rose-700 disabled:opacity-50 text-white font-bold text-xs px-5 py-2.5 rounded-lg shadow-lg flex items-center gap-2 transition-colors uppercase tracking-wider"
            >
              <span>{isSending ? 'Transmitting...' : '🚨 Authorize & Dispatch Broadcast'}</span>
            </button>
          </div>

          {broadcastResult && (
            <div className="bg-emerald-950 border border-emerald-600 text-emerald-200 p-3 rounded-lg text-xs font-mono">
              ✅ Broadcast record #{broadcastResult.broadcast_id} created. Status: {broadcastResult.status}. Delivered via PostGIS geographic routing.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
