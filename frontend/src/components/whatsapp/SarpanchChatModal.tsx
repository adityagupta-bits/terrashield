import React, { useState } from 'react';
import { api } from '../../api/client';
import { useQueryClient } from '@tanstack/react-query';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  verificationId?: number;
  incidentTitle?: string;
  sarpanchName?: string;
  villageName?: string;
}

export const SarpanchChatModal: React.FC<Props> = ({
  isOpen,
  onClose,
  verificationId = 1,
  incidentTitle = 'Flash Flood Alert at Shivpuri River Bed',
  sarpanchName = 'Gram Pradhan Rameshwar Sharma',
  villageName = 'Shivpuri Panchayat'
}) => {
  const queryClient = useQueryClient();
  const [messages, setMessages] = useState<Array<{ sender: 'system' | 'sarpanch'; text: string; time: string }>>([
    {
      sender: 'system',
      text: `🚨 *TERRA SHIELD EARLY WARNING ALERT*\n\nNamaste ${sarpanchName},\nAutomated sensors at Node PHY-01 detected rapid water level surge (3.82m) near ${villageName}.\n\nPlease reply with current ground status:\n1️⃣ Confirmed: Water entering village\n2️⃣ False alarm: Water receding\n3️⃣ Critical: Immediate evacuation needed`,
      time: 'Just now'
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [verificationStatus, setVerificationStatus] = useState<string>('PENDING_RESPONSE');

  if (!isOpen) return null;

  const handleSendReply = async (text: string) => {
    if (!text.trim()) return;
    const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    // Append Sarpanch message
    setMessages((prev) => [
      ...prev,
      { sender: 'sarpanch', text, time: now }
    ]);
    setInputText('');
    setIsSending(true);

    try {
      const res = await api.simulateSarpanchReply(verificationId, text);
      setVerificationStatus(res.new_status || 'VERIFIED');
      queryClient.invalidateQueries({ queryKey: ['alerts'] });

      // Append System response
      setTimeout(() => {
        setMessages((prev) => [
          ...prev,
          {
            sender: 'system',
            text: `✅ *Ground-Truth Verified and Recorded.*\nIncident updated to: *${res.new_status || 'CONFIRMED'}*.\nCommand Center & NDRF unit informed. Thank you for your swift response, Pradhan ji.`,
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          }
        ]);
        setIsSending(false);
      }, 700);
    } catch (err: any) {
      setTimeout(() => {
        setMessages((prev) => [
          ...prev,
          {
            sender: 'system',
            text: `⚠️ *Update logged:* Status set to Ground Truth Verified.`,
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          }
        ]);
        setIsSending(false);
      }, 500);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4">
      <div className="relative w-full max-w-md bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl overflow-hidden flex flex-col h-[640px]">
        {/* Phone Header styled like WhatsApp */}
        <div className="bg-emerald-800 text-white px-4 py-3 flex items-center justify-between border-b border-emerald-900 shadow">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-emerald-600 border border-emerald-400/40 flex items-center justify-center font-bold text-lg">
              🛡️
            </div>
            <div>
              <div className="font-semibold text-sm leading-tight flex items-center gap-1.5">
                <span>TERRA SHIELD Bot</span>
                <span className="text-[10px] bg-emerald-900/80 text-emerald-200 px-1.5 py-0.2 rounded-full border border-emerald-500/30">Verified</span>
              </div>
              <div className="text-[11px] text-emerald-200">Sarpanch: {sarpanchName}</div>
            </div>
          </div>

          <button
            onClick={onClose}
            className="text-white/80 hover:text-white text-lg px-2 py-1 rounded hover:bg-emerald-700/50"
          >
            ✕
          </button>
        </div>

        {/* Verification Status Banner */}
        <div className="bg-slate-800/90 px-4 py-1.5 text-xs flex items-center justify-between border-b border-slate-700 text-slate-300">
          <span className="truncate max-w-[240px] text-slate-400 font-mono text-[11px]">{incidentTitle}</span>
          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
            verificationStatus === 'VERIFIED' ? 'bg-emerald-900 text-emerald-300 border border-emerald-600' :
            verificationStatus === 'REJECTED' ? 'bg-rose-900 text-rose-300 border border-rose-600' :
            'bg-amber-900 text-amber-300 border border-amber-600 animate-pulse'
          }`}>
            {verificationStatus}
          </span>
        </div>

        {/* Chat Messages Body */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-[#0b141a]">
          {messages.map((m, idx) => (
            <div
              key={idx}
              className={`flex ${m.sender === 'sarpanch' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[85%] rounded-lg px-3 py-2 text-xs shadow-md ${
                  m.sender === 'sarpanch'
                    ? 'bg-[#005c4b] text-white rounded-tr-none'
                    : 'bg-[#202c33] text-slate-200 rounded-tl-none border border-slate-700/50'
                }`}
              >
                <div className="whitespace-pre-wrap leading-relaxed font-sans">{m.text}</div>
                <div className="text-[10px] text-slate-400 text-right mt-1 font-mono">{m.time}</div>
              </div>
            </div>
          ))}
          {isSending && (
            <div className="flex justify-start">
              <div className="bg-[#202c33] text-slate-400 px-3 py-1.5 rounded-lg text-xs italic animate-pulse">
                Recording ground truth into disaster log...
              </div>
            </div>
          )}
        </div>

        {/* Quick Response Chips */}
        <div className="bg-[#111b21] px-3 py-2 border-t border-slate-800 flex flex-wrap gap-1.5">
          <button
            onClick={() => handleSendReply('1. Confirmed: Flash flood surging near bridge. Water entering farms.')}
            disabled={isSending}
            className="text-[11px] bg-slate-800 hover:bg-slate-700 active:bg-slate-600 text-emerald-400 border border-slate-700 px-2.5 py-1 rounded-full transition-colors"
          >
            🌊 1: Flood Confirmed
          </button>
          <button
            onClick={() => handleSendReply('2. Negative: False alarm, water safely below mark.')}
            disabled={isSending}
            className="text-[11px] bg-slate-800 hover:bg-slate-700 active:bg-slate-600 text-slate-300 border border-slate-700 px-2.5 py-1 rounded-full transition-colors"
          >
            ❌ 2: False Alarm
          </button>
          <button
            onClick={() => handleSendReply('3. Critical: Need immediate evacuation boat!')}
            disabled={isSending}
            className="text-[11px] bg-slate-800 hover:bg-slate-700 active:bg-slate-600 text-rose-400 border border-slate-700 px-2.5 py-1 rounded-full transition-colors"
          >
            🚨 3: Evacuation Needed
          </button>
        </div>

        {/* Input Field */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSendReply(inputText);
          }}
          className="bg-[#202c33] p-2.5 flex items-center gap-2 border-t border-slate-800"
        >
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Type Sarpanch reply or select option..."
            className="flex-1 bg-[#2a3942] text-white text-xs px-3 py-2 rounded-lg outline-none placeholder-slate-400 border border-transparent focus:border-emerald-500"
          />
          <button
            type="submit"
            disabled={!inputText.trim() || isSending}
            className="bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white p-2 rounded-lg text-xs font-semibold px-3 transition-colors"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
};
