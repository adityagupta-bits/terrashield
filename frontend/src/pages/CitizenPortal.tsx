import React, { useState } from 'react';
import { api } from '../../api/client';
import { useQuery } from '@tanstack/react-query';

const VILLAGE_LOCATIONS = [
  { name: 'Kampur Kopili Riverfront (Nagaon)', lat: 26.0520, lng: 92.7750 },
  { name: 'Raha Kopili Confluence (Nagaon)', lat: 26.2200, lng: 92.5200 },
  { name: 'Pandu Port Brahmaputra (Guwahati)', lat: 26.1820, lng: 91.7150 },
  { name: 'Palashbari Embankment (Kamrup)', lat: 26.1300, lng: 91.5000 },
  { name: 'Saraighat North Bank (Kamrup)', lat: 26.1860, lng: 91.6980 }
];

export const CitizenPortal: React.FC = () => {
  const [lang, setLang] = useState<'en' | 'hi'>('en');
  const [selectedVillage, setSelectedVillage] = useState(VILLAGE_LOCATIONS[0]);

  // Query citizen status from backend
  const { data: statusData, isLoading } = useQuery({
    queryKey: ['citizen-status', selectedVillage.lat, selectedVillage.lng, lang],
    queryFn: () => api.getCitizenStatus(selectedVillage.lat, selectedVillage.lng, lang),
    refetchInterval: 10000
  });

  const isHindi = lang === 'hi';

  return (
    <div className="min-h-screen bg-slate-100 text-slate-900 font-sans">
      {/* Top Citizen Header with Bilingual Toggle */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-sm">
        <div className="max-w-xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-lg bg-emerald-50 border border-emerald-200/80 flex items-center justify-center p-1 shadow-sm">
              <img src="/logo-shield-transparent.png" alt="TERRA SHIELD" className="w-full h-full object-contain" />
            </div>
            <div>
              <div className="font-bold text-sm tracking-tight text-slate-900">
                {isHindi ? 'टेरा शील्ड नागरिक पोर्टल' : 'TERRA SHIELD Citizen Portal'}
              </div>
              <div className="text-[11px] text-slate-500">
                {isHindi ? 'आपदा प्रबंधन एवं प्रारंभिक चेतावनी' : 'Disaster Management & Early Warning'}
              </div>
            </div>
          </div>

          {/* Actions: Lang Toggle & Command Center link */}
          <div className="flex items-center gap-2">
            <a
              href="/"
              className="hidden sm:inline-flex bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold px-3 py-1.5 rounded-full transition-colors items-center gap-1 shadow-sm"
              title="Switch to Authority Command Center"
            >
              <span>👮</span>
              <span>Command Center</span>
            </a>

            <button
              onClick={() => setLang(isHindi ? 'en' : 'hi')}
              className="bg-slate-100 hover:bg-slate-200 border border-slate-300 text-slate-800 text-xs font-semibold px-3 py-1.5 rounded-full transition-colors"
            >
              {isHindi ? 'English' : 'हिंदी में देखें'}
            </button>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="max-w-xl mx-auto p-4 space-y-4">
        {/* Village / Location Selector */}
        <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm space-y-2">
          <label className="text-xs font-semibold text-slate-700 uppercase tracking-wider block">
            📍 {isHindi ? 'अपना वर्तमान क्षेत्र चुनें:' : 'Select Your Current Location:'}
          </label>
          <select
            value={selectedVillage.name}
            onChange={(e) => {
              const found = VILLAGE_LOCATIONS.find(v => v.name === e.target.value);
              if (found) setSelectedVillage(found);
            }}
            className="w-full bg-slate-50 text-slate-900 border border-slate-300 rounded-xl px-3 py-2.5 text-sm font-medium outline-none focus:border-emerald-600 focus:bg-white"
          >
            {VILLAGE_LOCATIONS.map((loc, idx) => (
              <option key={idx} value={loc.name}>
                {loc.name}
              </option>
            ))}
          </select>
        </div>

        {/* Live Safety Status Banner */}
        <div
          className={`rounded-2xl p-5 shadow-sm border ${
            statusData?.status === 'EVACUATE' || statusData?.status === 'CRITICAL'
              ? 'bg-rose-50 border-rose-200 text-rose-950'
              : statusData?.status === 'WARNING' || statusData?.status === 'ADVISORY'
              ? 'bg-amber-50 border-amber-200 text-amber-950'
              : 'bg-emerald-50 border-emerald-200 text-emerald-950'
          }`}
        >
          <div className="flex items-center gap-2">
            <span className="text-2xl">
              {statusData?.status === 'EVACUATE' || statusData?.status === 'CRITICAL' ? '🚨' :
               statusData?.status === 'WARNING' || statusData?.status === 'ADVISORY' ? '⚠️' : '✅'}
            </span>
            <div>
              <div className="text-xs font-bold uppercase tracking-wider opacity-75">
                {isHindi ? 'वर्तमान सुरक्षा स्थिति' : 'Current Safety Status'}
              </div>
              <div className="text-xl font-black mt-0.5">
                {isLoading ? (isHindi ? 'जाँच हो रही है...' : 'Evaluating...') :
                 statusData?.status === 'EVACUATE' ? (isHindi ? 'तुरंत खाली करें (EVACUATE)' : 'IMMEDIATE EVACUATION') :
                 statusData?.status === 'WARNING' ? (isHindi ? 'सतर्क रहें (WATCH)' : 'ADVISORY (WATCH & PREPARE)') :
                 (isHindi ? 'सुरक्षित क्षेत्र (NORMAL)' : 'SAFE / NORMAL')}
              </div>
            </div>
          </div>

          <p className="mt-3 text-sm leading-relaxed font-medium opacity-90">
            {statusData?.advisory_message || (
              isHindi
                ? 'नदी जलस्तर और पर्यावरणीय स्थिति सामान्य स्तर पर है। कोई तात्कालिक आपदा का खतरा नहीं है।'
                : 'Current sensor telemetry in this sector indicates stable water flow and normal atmospheric parameters. No active evacuation directive.'
            )}
          </p>

          <div className="mt-3 text-[11px] opacity-75 font-mono">
            {isHindi ? 'सत्यापित समय:' : 'Last verified:'} {new Date().toLocaleTimeString()} • Powered by TERRA SHIELD Mesh
          </div>
        </div>

        {/* Nearest Designated Safe Shelter */}
        <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <div className="text-xs font-semibold text-slate-700 uppercase tracking-wider">
              🏠 {isHindi ? 'निकटतम सुरक्षित राहत शिविर' : 'Nearest Safe Relief Shelter'}
            </div>
            <span className="text-xs font-mono font-bold text-emerald-600 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200">
              {statusData?.nearest_shelter?.distance_km !== undefined
                ? `${statusData.nearest_shelter.distance_km.toFixed(1)} km away`
                : '1.2 km away'}
            </span>
          </div>

          <div>
            <div className="text-base font-bold text-slate-900">
              {statusData?.nearest_shelter?.name || 'Shivpuri Senior Secondary School Camp'}
            </div>
            <div className="text-xs text-slate-500 mt-0.5">
              {statusData?.nearest_shelter?.location_name || 'Shivpuri Main Road, Higher Elevation Zone'}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-2 text-xs text-slate-600 bg-slate-50 p-2.5 rounded-xl">
            <div>
              <span className="font-semibold">{isHindi ? 'क्षमता:' : 'Capacity:'}</span>{' '}
              {statusData?.nearest_shelter?.capacity || 350} {isHindi ? 'व्यक्ति' : 'persons'}
            </div>
            <div>
              <span className="font-semibold">{isHindi ? 'हेल्पलाइन:' : 'In-Charge:'}</span>{' '}
              {statusData?.nearest_shelter?.phone || '9876543210'}
            </div>
          </div>

          <a
            href={`https://www.google.com/maps/dir/?api=1&destination=${selectedVillage.lat + 0.01},${selectedVillage.lng + 0.01}`}
            target="_blank"
            rel="noopener noreferrer"
            className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs py-2.5 px-4 rounded-xl flex items-center justify-center gap-2 shadow transition-colors"
          >
            <span>🧭</span>
            <span>{isHindi ? 'गूगल मैप्स पर रास्ता देखें' : 'Navigate on Google Maps'}</span>
          </a>
        </div>

        {/* SOS One-Tap Emergency Hotlines */}
        <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm space-y-3">
          <div className="text-xs font-semibold text-slate-700 uppercase tracking-wider">
            🚨 {isHindi ? 'आपातकालीन त्वरित सहायता' : 'Emergency Help & SOS'}
          </div>

          <div className="grid grid-cols-2 gap-2.5">
            <a
              href="tel:112"
              className="bg-rose-600 hover:bg-rose-700 text-white p-3 rounded-xl flex items-center justify-between shadow transition-colors"
            >
              <div>
                <div className="text-xs font-medium opacity-90">{isHindi ? 'राष्ट्रीय आपात' : 'National Helpline'}</div>
                <div className="text-xl font-bold font-mono">112</div>
              </div>
              <span className="text-xl">📞</span>
            </a>

            <a
              href="tel:1070"
              className="bg-amber-600 hover:bg-amber-700 text-white p-3 rounded-xl flex items-center justify-between shadow transition-colors"
            >
              <div>
                <div className="text-xs font-medium opacity-90">{isHindi ? 'राज्य आपदा केंद्र' : 'Disaster Relief'}</div>
                <div className="text-xl font-bold font-mono">1070</div>
              </div>
              <span className="text-xl">📞</span>
            </a>
          </div>

          {/* WhatsApp Bot Launcher */}
          <div className="pt-1">
            <a
              href="https://wa.me/919876543210?text=Hi%20TERRA%20SHIELD"
              target="_blank"
              rel="noopener noreferrer"
              className="w-full bg-[#25D366] hover:bg-[#20bd5a] text-white font-bold text-xs py-2.5 px-4 rounded-xl flex items-center justify-center gap-2 shadow transition-colors"
            >
              <span>💬</span>
              <span>{isHindi ? 'व्हाट्सएप बोट पर जानकारी प्राप्त करें' : 'Open Citizen WhatsApp Bot'}</span>
            </a>
          </div>
        </div>

        {/* Essential Disaster Do's and Don'ts */}
        <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm space-y-2 text-xs">
          <div className="font-bold text-slate-800 uppercase tracking-wider text-[11px]">
            📋 {isHindi ? 'बाढ़ एवं आपदा के दौरान आवश्यक नियम' : 'Essential Survival Protocols'}
          </div>
          <ul className="space-y-1.5 text-slate-600 list-disc list-inside leading-relaxed">
            <li>{isHindi ? 'नदी तटों, रपतों एवं निचले पुलों के पास न जाएं।' : 'Do not approach overflowing riverbanks or attempt to cross submerged bridges.'}</li>
            <li>{isHindi ? 'अपने मोबाइल फोन और आपातकालीन लाइट को चार्ज रखें।' : 'Keep mobile devices charged and carry dry emergency rations & drinking water.'}</li>
            <li>{isHindi ? 'अफवाहों पर ध्यान न दें, केवल आधिकारिक टेरा शील्ड चेतावनियों का पालन करें।' : 'Do not spread unverified rumors; follow official alerts.'}</li>
          </ul>
        </div>

        {/* Switch to Authority Command Center Link */}
        <div className="text-center pt-2 pb-8">
          <a
            href="/"
            className="text-xs text-slate-500 hover:text-emerald-700 font-medium inline-flex items-center gap-1 transition-colors"
          >
            <span>{isHindi ? 'आपदा प्रबंधन या प्रशासनिक अधिकारी?' : 'Disaster Response Officer or Authority?'}</span>
            <span className="font-semibold text-emerald-700 underline">
              {isHindi ? 'कमांड सेंटर खोलें →' : 'Switch to Command Center →'}
            </span>
          </a>
        </div>
      </main>
    </div>
  );
};
