'use client';

import React from 'react';
import { RiskAlert } from '../../lib/types';

interface RiskAlertFeedProps {
  alert: RiskAlert | null;
}

export default function RiskAlertFeed({ alert }: RiskAlertFeedProps) {
  if (!alert) {
    return (
      <div className="glass-panel" style={{ padding: '18px' }}>
        <h3 style={{ fontSize: '1rem', fontWeight: 600 }}>Real-Time Hazard Alert Feed</h3>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: 10 }}>Listening for multi-modal hazard early warnings...</p>
      </div>
    );
  }

  const getBadgeClass = (severity: string) => {
    switch (severity) {
      case 'CRITICAL': return 'badge-critical';
      case 'WARNING': return 'badge-warning';
      case 'WATCH': return 'badge-watch';
      default: return 'badge-info';
    }
  };

  return (
    <div className="glass-panel" style={{ padding: '18px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 600 }}>Hazard Early Warning</h3>
          <span className={`brand-badge ${getBadgeClass(alert.severity)}`} style={{ fontWeight: 700 }}>
            {alert.severity}
          </span>
        </div>
        <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: '#ff0055' }}>
          LEAD TIME: {Math.floor(alert.lead_time_seconds / 60)}m {alert.lead_time_seconds % 60}s
        </div>
      </div>

      <div style={{ background: 'rgba(13, 21, 34, 0.7)', borderRadius: 8, padding: 14, marginBottom: 14, borderLeft: '3px solid #ff0055' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: 6 }}>
          <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>DIAGNOSED HAZARD: {alert.alert_type}</span>
          <span style={{ color: '#00f0ff', fontFamily: 'var(--font-mono)' }}>CONFIDENCE: {(alert.confidence_score * 100).toFixed(0)}%</span>
        </div>
        <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: 8 }}>
          <strong>Mechanism:</strong> {alert.primary_mechanism}
        </div>
        <div style={{ fontSize: '0.88rem', color: '#f8fafc', fontWeight: 500, background: 'rgba(255, 0, 85, 0.08)', padding: '8px 12px', borderRadius: 6 }}>
          ⚠️ {alert.driller_action_summary}
        </div>
      </div>

      <h4 style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
        Standard Operating Procedure (SOP) Checklist
      </h4>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
        {alert.detailed_sop && alert.detailed_sop.map((step, idx) => (
          <div key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: 8, fontSize: '0.82rem', color: 'var(--text-main)' }}>
            <span style={{ color: '#00f0ff', fontFamily: 'var(--font-mono)' }}>[{idx + 1}]</span>
            <span>{step}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
