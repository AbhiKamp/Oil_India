'use client';

import React, { useState } from 'react';
import { queryAssistant } from '../../lib/api';

interface AiAssistantModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentDepth: number;
}

export default function AiAssistantModal({ isOpen, onClose, currentDepth }: AiAssistantModalProps) {
  const [messages, setMessages] = useState<Array<{ role: 'user' | 'assistant'; text: string; citations?: any[] }>>([
    {
      role: 'assistant',
      text: 'StrataSentry Drilling Copilot online. I am grounded in Assam-Arakan Basin offset well completion reports (MOR-118, NHK-412, BGH-07). How can I assist your drilling operation?'
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSend = async () => {
    if (!input.trim()) return;
    const userMsg = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
    setLoading(true);

    try {
      const res = await queryAssistant(userMsg, "NHK-421", currentDepth, "Barail Coal-Shale");
      setMessages(prev => [...prev, {
        role: 'assistant',
        text: res.answer,
        citations: res.citations
      }]);
    } catch (e) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        text: 'Error contacting RAG Copilot service. Please verify local gateway status.'
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      position: 'fixed', inset: 0, zIndex: 1000,
      backgroundColor: 'rgba(2, 6, 23, 0.75)', backdropFilter: 'blur(8px)',
      display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20
    }}>
      <div className="glass-panel" style={{ width: '100%', maxWidth: '720px', height: '620px', display: 'flex', flexDirection: 'column' }}>
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '16px 20px', borderBottom: '1px solid var(--border-subtle)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span style={{ fontSize: '1.1rem', fontWeight: 600 }}>StrataSentry Drilling Copilot</span>
            <span className="brand-badge">Mistral RAG</span>
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', fontSize: '1.2rem', cursor: 'pointer' }}>✕</button>
        </div>

        {/* Message Log */}
        <div style={{ flex: 1, padding: 20, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 14 }}>
          {messages.map((m, idx) => (
            <div key={idx} style={{
              alignSelf: m.role === 'user' ? 'flex-end' : 'flex-start',
              maxWidth: '85%',
              background: m.role === 'user' ? 'rgba(0, 240, 255, 0.15)' : 'rgba(16, 24, 39, 0.85)',
              border: `1px solid ${m.role === 'user' ? 'rgba(0, 240, 255, 0.4)' : 'var(--border-subtle)'}`,
              borderRadius: 8, padding: '12px 16px'
            }}>
              <p style={{ fontSize: '0.88rem', lineHeight: 1.5, whiteSpace: 'pre-wrap' }}>{m.text}</p>
              {m.citations && m.citations.length > 0 && (
                <div style={{ marginTop: 10, borderTop: '1px solid rgba(255, 255, 255, 0.1)', paddingTop: 8 }}>
                  <span style={{ fontSize: '0.72rem', color: '#00f0ff', fontWeight: 600 }}>GROUNDED CITATIONS:</span>
                  {m.citations.map((c, cIdx) => (
                    <div key={cIdx} style={{ fontSize: '0.74rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)', marginTop: 4 }}>
                      • Well {c.well_name} ({c.depth_interval_md}) - WCR Page {c.page_reference}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
          {loading && (
            <div style={{ color: 'var(--color-cyan)', fontSize: '0.85rem', fontFamily: 'var(--font-mono)' }}>
              Synthesizing offset well evidence...
            </div>
          )}
        </div>

        {/* Input Bar */}
        <div style={{ padding: '14px 20px', borderTop: '1px solid var(--border-subtle)', display: 'flex', gap: 10 }}>
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSend()}
            placeholder="Ask about offset stuck pipe, kick procedures, or formation tops..."
            style={{
              flex: 1, background: 'rgba(13, 21, 34, 0.8)', border: '1px solid var(--border-subtle)',
              borderRadius: 6, padding: '10px 14px', color: '#ffffff', outline: 'none', fontFamily: 'var(--font-sans)', fontSize: '0.88rem'
            }}
          />
          <button className="btn-primary" onClick={handleSend} disabled={loading}>
            Ask Copilot
          </button>
        </div>
      </div>
    </div>
  );
}
