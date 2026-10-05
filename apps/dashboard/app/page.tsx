'use client';

import React, { useState, useEffect } from 'react';
import { Well, TrajectoryStation, FormationTop, TelemetryFrame, RiskAlert } from '../lib/types';
import { fetchWells, fetchTrajectory, fetchFormations, fetchLatestTelemetry, fetchCurrentRisk } from '../lib/api';
import WellViewer3D from '../components/3d-well-viewer/WellViewer3D';
import LiveDrillingPanel from '../components/live-drilling/LiveDrillingPanel';
import RiskAlertFeed from '../components/alerts/RiskAlertFeed';
import HistoricalEvidenceDrawer from '../components/historical-evidence/HistoricalEvidenceDrawer';
import AiAssistantModal from '../components/ai-assistant/AiAssistantModal';

export default function DashboardPage() {
  const [wells, setWells] = useState<Well[]>([]);
  const [selectedWell, setSelectedWell] = useState<string>('NHK-421');
  const [stations, setStations] = useState<TrajectoryStation[]>([]);
  const [formations, setFormations] = useState<FormationTop[]>([]);
  const [telemetry, setTelemetry] = useState<TelemetryFrame | null>(null);
  const [currentRisk, setCurrentRisk] = useState<RiskAlert | null>(null);
  const [isCopilotOpen, setIsCopilotOpen] = useState(false);

  useEffect(() => {
    // Initial data fetch
    fetchWells().then(data => {
      setWells(data);
      if (data.length > 0) setSelectedWell(data[0].well_id);
    });
  }, []);

  useEffect(() => {
    if (!selectedWell) return;
    fetchTrajectory(selectedWell).then(setStations);
    fetchFormations(selectedWell).then(setFormations);
    fetchLatestTelemetry(selectedWell).then(setTelemetry);
    fetchCurrentRisk(selectedWell).then(setCurrentRisk);

    // Setup live polling / WebSocket connection
    const interval = setInterval(async () => {
      const t = await fetchLatestTelemetry(selectedWell);
      if (t) setTelemetry(t);
      const r = await fetchCurrentRisk(selectedWell);
      if (r) setCurrentRisk(r);
    }, 2000);

    return () => clearInterval(interval);
  }, [selectedWell]);

  const currentDepth = telemetry?.measured_depth || 2845.5;

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Tactical Top Bar */}
      <header className="header-container">
        <div className="brand-wrapper">
          <div style={{ width: 12, height: 12, backgroundColor: '#00f0ff', borderRadius: '50%', boxShadow: '0 0 10px #00f0ff' }} />
          <h1 className="brand-title">STRATASENTRY-NWIS</h1>
          <span className="brand-badge">Upper Assam Basin</span>
        </div>

        {/* Operational Status Center */}
        <div style={{ display: 'flex', gap: 24, alignItems: 'center' }}>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <span style={{ fontSize: '0.68rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>ACTIVE WELL</span>
            <select
              value={selectedWell}
              onChange={e => setSelectedWell(e.target.value)}
              style={{
                background: 'rgba(13, 21, 34, 0.9)', color: '#00f0ff', border: '1px solid var(--border-subtle)',
                borderRadius: 4, padding: '3px 8px', fontFamily: 'var(--font-mono)', fontSize: '0.85rem', fontWeight: 600
              }}
            >
              {wells.map(w => (
                <option key={w.well_id} value={w.well_id}>{w.well_name} ({w.field})</option>
              ))}
            </select>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <span style={{ fontSize: '0.68rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>MEASURED DEPTH</span>
            <span style={{ fontSize: '1rem', fontWeight: 700, fontFamily: 'var(--font-mono)', color: '#ffffff' }}>
              {currentDepth.toFixed(1)} <span style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>m</span>
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <span style={{ fontSize: '0.68rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>RIG NETWORK</span>
            <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#10b981', display: 'flex', alignItems: 'center', gap: 6 }}>
              <span style={{ width: 6, height: 6, borderRadius: '50%', backgroundColor: '#10b981' }} />
              AIR-GAP STANDALONE
            </span>
          </div>
        </div>

        {/* Right Action buttons */}
        <div style={{ display: 'flex', gap: 12 }}>
          <button className="btn-primary" onClick={() => setIsCopilotOpen(true)}>
            💬 AI Drilling Copilot
          </button>
        </div>
      </header>

      {/* Main Tactical Operational Dashboard Grid */}
      <main className="dashboard-grid">
        {/* Left Primary Column: 3D Visualization & Live Gauges */}
        <section className="main-column">
          <WellViewer3D
            stations={stations}
            currentDepth={currentDepth}
            formations={formations}
          />

          <LiveDrillingPanel telemetry={telemetry} />
        </section>

        {/* Right Secondary Column: Multi-modal Hazard Alert Feed & Historical RAG Precedents */}
        <aside className="side-column">
          <RiskAlertFeed alert={currentRisk} />

          <div style={{ flex: 1, minHeight: 0 }}>
            <HistoricalEvidenceDrawer />
          </div>
        </aside>
      </main>

      {/* RAG Drilling Copilot Chat Modal */}
      <AiAssistantModal
        isOpen={isCopilotOpen}
        onClose={() => setIsCopilotOpen(false)}
        currentDepth={currentDepth}
      />
    </div>
  );
}
