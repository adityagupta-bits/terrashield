import React, { useState, useEffect } from 'react';
import { X, Send, MessageSquare, CheckCheck, Bot, User } from 'lucide-react';
import { fetchWhatsAppVerifications, simulateSarpanchReply } from '../services/api';

export default function WhatsAppBotModal({
  isOpen,
  onClose,
  incidentId,
  onVerificationUpdated
}) {
  const [verifications, setVerifications] = useState([]);
  const [activeVerif, setActiveVerif] = useState(null);
  const [inputText, setInputText] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadVerifications();
    }
  }, [isOpen, incidentId]);

  const loadVerifications = async () => {
    try {
      const data = await fetchWhatsAppVerifications(incidentId);
      setVerifications(data);
      if (data.length > 0) {
        setActiveVerif(data[0]);
      }
    } catch (e) {
      console.error('Failed to load verifications', e);
    }
  };

  const handleSendReply = async (textToSend) => {
    const text = textToSend || inputText;
    if (!text.trim() || !activeVerif) return;

    setIsSubmitting(true);
    try {
      const res = await simulateSarpanchReply(activeVerif.id, text);
      setInputText('');
      await loadVerifications();
      if (onVerificationUpdated) onVerificationUpdated(res);
    } catch (e) {
      console.error('Failed to simulate reply', e);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content" style={{ maxWidth: '620px', borderRadius: '16px' }}>
        {/* Modal Header (Authentic WhatsApp Green) */}
        <div style={{
          background: '#008069',
          color: '#ffffff',
          padding: '14px 20px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{
              width: 32, height: 32, borderRadius: '50%',
              background: '#ffffff', display: 'flex', alignItems: 'center', justifyContent: 'center'
            }}>
              <MessageSquare size={17} color="#008069" />
            </div>
            <div>
              <div style={{ fontWeight: 700, fontSize: '0.92rem' }}>
                Human-as-a-Sensor: Vernacular WhatsApp Verification
              </div>
              <div style={{ fontSize: '0.72rem', color: '#e0f2fe', opacity: 0.9 }}>
                AI-Powered Ground Truth Confirmation for Sarpanches & Ward Chiefs
              </div>
            </div>
          </div>
          <button
            onClick={onClose}
            style={{ background: 'transparent', border: 'none', color: '#ffffff', cursor: 'pointer' }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Modal Body: WhatsApp Chat Simulator */}
        <div style={{ padding: '0', background: '#ffffff' }}>
          {activeVerif ? (
            <div className="chat-window">
              {/* Chat Sub-header */}
              <div style={{
                background: '#f0f2f5',
                padding: '10px 16px',
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                borderBottom: '1px solid #e2e8f0'
              }}>
                <div style={{
                  width: 32, height: 32, borderRadius: '50%',
                  background: '#cbd5e1', display: 'flex', alignItems: 'center', justifyContent: 'center'
                }}>
                  <User size={18} color="#475569" />
                </div>
                <div>
                  <div style={{ fontWeight: 600, fontSize: '0.85rem', color: '#0f172a' }}>
                    {activeVerif.sarpanch_name}
                  </div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                    {activeVerif.phone_number} • Gram Panchayat Chief
                  </div>
                </div>
                <div style={{ marginLeft: 'auto' }}>
                  <span style={{
                    fontSize: '0.7rem',
                    fontWeight: 700,
                    padding: '2px 8px',
                    borderRadius: '4px',
                    background: activeVerif.verification_status === 'CONFIRMED'
                      ? '#dcfce7'
                      : (activeVerif.verification_status === 'FALSE_ALARM' ? '#fee2e2' : '#fef3c7'),
                    color: activeVerif.verification_status === 'CONFIRMED'
                      ? '#15803d'
                      : (activeVerif.verification_status === 'FALSE_ALARM' ? '#dc2626' : '#b45309'),
                    border: '1px solid currentColor'
                  }}>
                    {activeVerif.verification_status} ({Math.round(activeVerif.nlp_confidence * 100)}% NLP)
                  </span>
                </div>
              </div>

              {/* Chat Messages */}
              <div className="chat-messages">
                {/* 1. Bot Automated Query in Hindi */}
                <div className="chat-bubble sent">
                  <div style={{ display: 'flex', alignItems: 'center', gap: 4, marginBottom: 4, color: '#008069', fontSize: '0.72rem', fontWeight: 700 }}>
                    <Bot size={13} /> TERRA SHIELD BOT (Automated Dispatch)
                  </div>
                  <div style={{ whiteSpace: 'pre-line' }}>{activeVerif.query_sent}</div>
                  <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', textAlign: 'right', marginTop: 4 }}>
                    {new Date(activeVerif.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} • <CheckCheck size={12} color="#0284c7" style={{ verticalAlign: 'middle' }} />
                  </div>
                </div>

                {/* 2. Sarpanch Reply (if received) */}
                {activeVerif.response_received && (
                  <div className="chat-bubble received">
                    <div style={{ whiteSpace: 'pre-line' }}>{activeVerif.response_received}</div>
                    <div style={{ fontSize: '0.65rem', color: '#64748b', textAlign: 'right', marginTop: 4 }}>
                      Verified via Vernacular NLP • <CheckCheck size={12} color="#0284c7" style={{ verticalAlign: 'middle' }} />
                    </div>
                  </div>
                )}
              </div>

              {/* Chat Input & Quick Response Buttons for Presentation */}
              <div style={{ background: '#f8fafc', padding: '10px 14px', borderTop: '1px solid #e2e8f0' }}>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: '6px', fontWeight: 600 }}>
                  Quick Demonstration Replies for Judges:
                </div>
                <div style={{ display: 'flex', gap: '6px', marginBottom: '8px', flexWrap: 'wrap' }}>
                  <button
                    onClick={() => handleSendReply("हाँ, नदी का पानी बांध से बाहर आ रहा है, तुरंत NDRF सहायता भेजो!")}
                    style={{
                      background: '#dcfce7',
                      border: '1px solid #86efac',
                      color: '#15803d',
                      borderRadius: '14px',
                      padding: '4px 10px',
                      fontSize: '0.72rem',
                      fontWeight: 600,
                      cursor: 'pointer'
                    }}
                  >
                    🌊 "हाँ, नदी का पानी आ रहा है" (Confirm Hazard)
                  </button>
                  <button
                    onClick={() => handleSendReply("नहीं, यहाँ सब सामान्य है, कोई खतरा नहीं है, गलत अलार्म है")}
                    style={{
                      background: '#fee2e2',
                      border: '1px solid #fca5a5',
                      color: '#dc2626',
                      borderRadius: '14px',
                      padding: '4px 10px',
                      fontSize: '0.72rem',
                      fontWeight: 600,
                      cursor: 'pointer'
                    }}
                  >
                    🟢 "नहीं, सब सामान्य है" (Prevent False Alarm)
                  </button>
                </div>

                <div className="chat-input-row">
                  <input
                    type="text"
                    className="chat-input"
                    placeholder="Type custom vernacular reply (Hindi/English/Telugu)..."
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSendReply()}
                  />
                  <button
                    onClick={() => handleSendReply()}
                    disabled={isSubmitting || !inputText.trim()}
                    style={{
                      background: '#008069',
                      border: 'none',
                      borderRadius: '50%',
                      width: 34,
                      height: 34,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      cursor: 'pointer',
                      color: '#fff'
                    }}
                  >
                    <Send size={15} />
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '36px 20px', color: 'var(--text-muted)' }}>
              No active verification queries currently queued. Trigger a simulated disaster from the "Simulate Scenarios" menu above to watch the bot dispatch an automated vernacular message to the village Sarpanch!
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
