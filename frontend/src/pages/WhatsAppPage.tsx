import React, { useState } from 'react';
import { SarpanchChatModal } from '../../components/whatsapp/SarpanchChatModal';

export const WhatsAppPage: React.FC = () => {
  const [sarpanchModalOpen, setSarpanchModalOpen] = useState(false);
  const [selectedIncident, setSelectedIncident] = useState({
    id: 1,
    title: 'Shivpuri Riverbed Flash Flood Inflow',
    sarpanch: 'Gram Pradhan Rameshwar Sharma',
    village: 'Shivpuri Panchayat'
  });

  // Citizen Bot State
  const [citizenMessages, setCitizenMessages] = useState<Array<{ sender: 'bot' | 'user'; text: string; time: string }>>([
    {
      sender: 'bot',
      text: `🛡️ *TERRA SHIELD CITIZEN EMERGENCY BOT*\n\nWelcome to District Disaster Early Warning System.\n\nReply with a number:\n1️⃣ Current Safety Advisory for your location\n2️⃣ Nearest Safe Shelter & Evacuation Map\n3️⃣ Report Hazard / Water Logging\n4️⃣ Emergency Helpline Contacts\n5️⃣ भाषा बदलें (Switch to Hindi)`,
      time: '10:00 AM'
    }
  ]);
  const [citizenInput, setCitizenInput] = useState('');
  const [lang, setLang] = useState<'en' | 'hi'>('en');

  const handleCitizenSend = (text: string) => {
    if (!text.trim()) return;
    const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    setCitizenMessages(prev => [...prev, { sender: 'user', text, time: now }]);
    setCitizenInput('');

    setTimeout(() => {
      let reply = '';
      const choice = text.trim();

      if (choice === '1') {
        reply = lang === 'en'
          ? `⚠️ *SAFETY ADVISORY: RISHIKESH / SHIVPURI*\n• River Ganga water level: 3.42m (Alert Mark 3.50m)\n• Rain intensity: 12 mm/h\n• Status: *WATCH & PREPARE*\nAvoid riverbanks and low ghats.`
          : `⚠️ *सुरक्षा परामर्श: ऋषिकेश / शिवपुरी*\n• गंगा जलस्तर: 3.42 मीटर (चेतावनी स्तर 3.50m)\n• वर्षा दर: 12 मिमी/घंटा\n• स्थिति: *सतर्क रहें*\nनदी किनारे जाने से बचें।`;
      } else if (choice === '2') {
        reply = lang === 'en'
          ? `🏠 *NEAREST SAFE SHELTER*\n*Shivpuri Senior Secondary School Relief Camp*\n• Distance: 1.4 km from your coordinates\n• Capacity: 350 persons\n• Camp Officer: Shri R. Negi (9876543210)\n📍 Google Maps: https://maps.google.com/?q=30.135,78.388`
          : `🏠 *निकटतम सुरक्षित राहत शिविर*\n*शिवपुरी राजकीय इंटर कॉलेज राहत शिविर*\n• दूरी: 1.4 किमी\n• क्षमता: 350 व्यक्ति\n• शिविर प्रभारी: श्री आर. नेगी (9876543210)`;
      } else if (choice === '3') {
        reply = lang === 'en'
          ? `📸 *REPORT HAZARD*\nPlease send the location name or description of the hazard. A field rapid response team will be tagged immediately.`
          : `📸 *आपदा की सूचना दें*\nकृपया स्थान का नाम या आपदा का विवरण भेजें। आपदा प्रतिक्रिया दल को तुरंत सूचित किया जाएगा।`;
      } else if (choice === '4') {
        reply = `📞 *EMERGENCY HELPLINES*\n• National Emergency: 112\n• State Disaster Control Room: 1070\n• District Disaster Desk: 1077\n• Free Ambulance Service: 108`;
      } else if (choice === '5') {
        const nextLang = lang === 'en' ? 'hi' : 'en';
        setLang(nextLang);
        reply = nextLang === 'hi'
          ? `✅ भाषा बदलकर हिंदी कर दी गई है।\n1️⃣ वर्तमान सुरक्षा परामर्श\n2️⃣ निकटतम राहत शिविर\n3️⃣ आपदा की सूचना\n4️⃣ आपातकालीन नंबर`
          : `✅ Language switched to English.\n1️⃣ Safety Advisory\n2️⃣ Nearest Shelter\n3️⃣ Report Hazard\n4️⃣ Helplines`;
      } else {
        reply = `To use TERRA SHIELD Bot, reply with numbers 1, 2, 3, 4, or 5.`;
      }

      setCitizenMessages(prev => [...prev, {
        sender: 'bot',
        text: reply,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }]);
    }, 500);
  };

  return (
    <div className="space-y-4 pb-12">
      {/* Header */}
      <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-xl">
        <h1 className="text-lg font-bold text-white flex items-center gap-2">
          <span>💬</span>
          <span>WhatsApp Multi-Channel Disaster Communication System</span>
        </h1>
        <p className="text-xs text-slate-400 mt-0.5">
          Two-way citizen advisory menu bot & Sarpanch ground-truth verification loop. Zero app installation required for villagers.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Left: Citizen Bot Simulator */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 flex flex-col items-center">
          <div className="w-full flex items-center justify-between mb-3">
            <h2 className="text-xs font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-1.5">
              <span>📱</span>
              <span>1. Citizen WhatsApp Menu Bot (Numbers 1-5)</span>
            </h2>
            <span className="text-[10px] font-mono bg-emerald-950 text-emerald-300 border border-emerald-800 px-2 py-0.5 rounded-full">
              Citizen Portal Companion
            </span>
          </div>

          {/* Phone Frame */}
          <div className="w-full max-w-sm bg-[#0b141a] border border-slate-700 rounded-2xl overflow-hidden shadow-2xl flex flex-col h-[520px]">
            {/* Phone Header */}
            <div className="bg-[#1f2c34] text-white px-3 py-2.5 flex items-center gap-2 border-b border-slate-700">
              <div className="w-8 h-8 rounded-full bg-emerald-600 flex items-center justify-center font-bold text-sm">
                🛡️
              </div>
              <div className="flex-1 min-w-0">
                <div className="font-semibold text-xs leading-tight truncate">TERRA SHIELD Citizen Bot</div>
                <div className="text-[10px] text-slate-400 truncate">Official Disaster Assistant</div>
              </div>
            </div>

            {/* Messages Body */}
            <div className="flex-1 overflow-y-auto p-3 space-y-2 text-xs">
              {citizenMessages.map((m, idx) => (
                <div
                  key={idx}
                  className={`flex ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[85%] rounded-lg px-2.5 py-1.5 shadow ${
                      m.sender === 'user'
                        ? 'bg-[#005c4b] text-white rounded-tr-none'
                        : 'bg-[#202c33] text-slate-200 rounded-tl-none border border-slate-700/50'
                    }`}
                  >
                    <div className="whitespace-pre-wrap leading-relaxed text-[11px]">{m.text}</div>
                    <div className="text-[9px] text-slate-400 text-right mt-0.5 font-mono">{m.time}</div>
                  </div>
                </div>
              ))}
            </div>

            {/* Quick 1-5 buttons */}
            <div className="bg-[#111b21] p-1.5 border-t border-slate-800 flex justify-between gap-1">
              {['1: Advisory', '2: Shelter', '3: Report', '4: Helplines', '5: हिंदी'].map((btn, i) => (
                <button
                  key={i}
                  onClick={() => handleCitizenSend(String(i + 1))}
                  className="bg-slate-800 hover:bg-slate-700 text-slate-300 text-[10px] font-mono px-1.5 py-1 rounded border border-slate-700 transition-colors flex-1"
                >
                  {btn}
                </button>
              ))}
            </div>

            {/* Input Bar */}
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleCitizenSend(citizenInput);
              }}
              className="bg-[#202c33] p-2 flex items-center gap-1.5"
            >
              <input
                type="text"
                value={citizenInput}
                onChange={(e) => setCitizenInput(e.target.value)}
                placeholder="Reply 1, 2, 3, 4, 5..."
                className="flex-1 bg-[#2a3942] text-white text-xs px-2.5 py-1.5 rounded-lg outline-none placeholder-slate-400"
              />
              <button
                type="submit"
                className="bg-emerald-600 text-white text-xs px-2.5 py-1.5 rounded-lg font-semibold"
              >
                Send
              </button>
            </form>
          </div>
        </div>

        {/* Right: Sarpanch Ground-Truth Verification Station */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xs font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-1.5">
              <span>🏛️</span>
              <span>2. Gram Pradhan / Sarpanch Ground Truth Verification</span>
            </h2>
            <span className="text-[10px] font-mono bg-cyan-950 text-cyan-300 border border-cyan-800 px-2 py-0.5 rounded-full">
              Anti-False Alarm Loop
            </span>
          </div>

          <p className="text-xs text-slate-300 leading-relaxed">
            When hardware sensors detect high water surge, the system avoids costly false evacuations by automatically paging the registered village Sarpanch. The Pradhan’s reply instantly verifies or de-escalates the incident.
          </p>

          {/* Sample Incident Card */}
          <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 space-y-3">
            <div className="flex items-start justify-between gap-2">
              <div>
                <span className="text-[10px] bg-rose-600 text-white font-bold px-2 py-0.5 rounded font-mono">
                  ACTIVE SURGE
                </span>
                <h3 className="text-sm font-semibold text-white mt-1.5">
                  {selectedIncident.title}
                </h3>
                <div className="text-xs text-slate-400 mt-0.5 font-mono">
                  Sensor Node: <span className="text-cyan-400">PHY-01</span> (Shivpuri Ghat)
                </div>
              </div>

              <span className="text-[10px] bg-amber-950 text-amber-300 border border-amber-800 px-2 py-0.5 rounded font-mono">
                Awaiting Pradhan Verification
              </span>
            </div>

            <div className="border-t border-slate-800 pt-2 text-xs text-slate-300 space-y-1">
              <div><strong>Registered Sarpanch:</strong> {selectedIncident.sarpanch}</div>
              <div><strong>Panchayat:</strong> {selectedIncident.village}</div>
              <div><strong>Phone:</strong> +91 98765 43210</div>
            </div>

            <div className="pt-2">
              <button
                onClick={() => setSarpanchModalOpen(true)}
                className="w-full bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold py-2.5 px-4 rounded-lg flex items-center justify-center gap-2 shadow-lg transition-colors uppercase tracking-wider"
              >
                <span>💬</span>
                <span>Open Interactive Sarpanch Verification Modal</span>
              </button>
            </div>
          </div>

          {/* Verification Protocol Explainer */}
          <div className="bg-slate-800/40 border border-slate-700/60 rounded-lg p-3 space-y-1.5 text-xs text-slate-400">
            <div className="font-semibold text-slate-200">How Ground-Truth Verification Protects Resources:</div>
            <ul className="list-disc list-inside space-y-1 text-[11px] text-slate-300">
              <li>Eliminates sensor drift or debris false alarms before deploying NDRF boats.</li>
              <li>Pradhan replies with 1, 2, or 3 directly from standard WhatsApp.</li>
              <li>Recorded reply updates incident database with verifiable audit trail.</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Sarpanch Chat Modal */}
      <SarpanchChatModal
        isOpen={sarpanchModalOpen}
        onClose={() => setSarpanchModalOpen(false)}
        incidentTitle={selectedIncident.title}
        sarpanchName={selectedIncident.sarpanch}
        villageName={selectedIncident.village}
      />
    </div>
  );
};
