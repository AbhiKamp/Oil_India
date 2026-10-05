'use client';

import React, { useState, useEffect } from 'react';

interface EvidenceChunk {
  chunk_id: string;
  well_name: string;
  formation_name: string;
  md_top: number;
  md_bottom: number;
  page_number: number;
  text: string;
  score: number;
}

export default function HistoricalEvidenceDrawer() {
  const [evidence, setEvidence] = useState<EvidenceChunk[]>([
    {
      chunk_id: "MOR-118_c1",
      well_name: "MOR-118",
      formation_name: "Barail Coal-Shale",
      md_top: 2848.0,
      md_bottom: 2865.0,
      page_number: 19,
      text: "While drilling ahead at 2,848.0 m MD with an 8-1/2\" PDC bit, string motion became tight on connection. Standpipe pressure surged to 3,650 psi. Spotted 45-bbl polymer pill, applied 85 klbs overpull jarring up. Pipe freed after 14 hours.",
      score: 0.94
    },
    {
      chunk_id: "NHK-412_c1",
      well_name: "NHK-412",
      formation_name: "Barail Coal-Shale",
      md_top: 2912.0,
      md_bottom: 2930.0,
      page_number: 24,
      text: "Gas kick encountered at 2,912.0 m MD. Pit volume gained 18 bbls. Shut in on Annular BOP. SIDPP = 320 psi, SICP = 410 psi. Weighted mud to 1.34 SG.",
      score: 0.88
    }
  ]);

  return (
    <div className="glass-panel" style={{ padding: '18px', height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
        <div>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 600 }}>Historical Offset Precedents</h3>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Assam Basin Legacy Well Completion Reports</span>
        </div>
        <span className="brand-badge" style={{ color: '#00f0ff' }}>Qdrant RAG</span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 12, overflowY: 'auto' }}>
        {evidence.map((item, idx) => (
          <div key={idx} style={{ background: 'rgba(13, 21, 34, 0.7)', border: '1px solid var(--border-subtle)', borderRadius: 8, padding: 12 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
              <span style={{ fontWeight: 600, color: '#00f0ff', fontSize: '0.88rem' }}>Well: {item.well_name}</span>
              <span style={{ fontSize: '0.72rem', fontFamily: 'var(--font-mono)', background: 'rgba(0, 240, 255, 0.1)', color: '#00f0ff', padding: '2px 6px', borderRadius: 4 }}>
                Page {item.page_number}
              </span>
            </div>

            <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginBottom: 8, fontFamily: 'var(--font-mono)' }}>
              DEPTH: {item.md_top}m - {item.md_bottom}m MD | {item.formation_name}
            </div>

            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: 1.45 }}>
              "{item.text}"
            </p>

            <div style={{ marginTop: 8, display: 'flex', justifyContent: 'flex-end' }}>
              <span style={{ fontSize: '0.72rem', color: '#10b981', fontFamily: 'var(--font-mono)' }}>
                Relevance: {(item.score * 100).toFixed(0)}%
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
