'use client';

import React from 'react';
import { TelemetryFrame } from '../../lib/types';

interface LiveDrillingPanelProps {
  telemetry: TelemetryFrame | null;
}

export default function LiveDrillingPanel({ telemetry }: LiveDrillingPanelProps) {
  const t = telemetry || {
    timestamp: new Date().toISOString(),
    well_id: "NHK-421",
    measured_depth: 2845.5,
    bit_depth: 2845.3,
    rop: 14.2,
    wob: 12.0,
    surface_torque: 14.8,
    rotary_rpm: 110,
    standpipe_pressure: 3150.0,
    flow_in: 2400.0,
    flow_out_pct: 74.2,
    pit_volume: 42.1,
    mud_weight_in: 1.28,
    ecd: 1.34,
    gamma_ray: 86.5,
    gas_total: 18.2
  };

  return (
    <div className="glass-panel" style={{ padding: '18px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
        <div>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 600 }}>Live Drilling Telemetry</h3>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
            WELL: {t.well_id} | BIT DEPTH: {t.bit_depth?.toFixed(1)} m | 10 Hz STREAM
          </span>
        </div>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <span style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: '#10b981', display: 'inline-block' }} />
          <span style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', color: '#10b981' }}>WITSML ACTIVE</span>
        </div>
      </div>

      <div className="telemetry-grid">
        <div className="telemetry-card">
          <div className="telemetry-label">Rate of Pen (ROP)</div>
          <div className="telemetry-value">
            {t.rop?.toFixed(1)}
            <span className="telemetry-unit">m/hr</span>
          </div>
        </div>

        <div className="telemetry-card">
          <div className="telemetry-label">Weight on Bit</div>
          <div className="telemetry-value">
            {t.wob?.toFixed(1)}
            <span className="telemetry-unit">tons</span>
          </div>
        </div>

        <div className="telemetry-card">
          <div className="telemetry-label">Surface Torque</div>
          <div className="telemetry-value" style={{ color: t.surface_torque > 18 ? '#f59e0b' : 'inherit' }}>
            {t.surface_torque?.toFixed(1)}
            <span className="telemetry-unit">kN.m</span>
          </div>
        </div>

        <div className="telemetry-card">
          <div className="telemetry-label">Rotary Speed</div>
          <div className="telemetry-value">
            {t.rotary_rpm}
            <span className="telemetry-unit">RPM</span>
          </div>
        </div>

        <div className="telemetry-card">
          <div className="telemetry-label">Standpipe (SPP)</div>
          <div className="telemetry-value" style={{ color: t.standpipe_pressure > 3300 ? '#ff0055' : 'inherit' }}>
            {t.standpipe_pressure?.toFixed(0)}
            <span className="telemetry-unit">psi</span>
          </div>
        </div>

        <div className="telemetry-card">
          <div className="telemetry-label">Flow Rate In</div>
          <div className="telemetry-value">
            {t.flow_in?.toFixed(0)}
            <span className="telemetry-unit">LPM</span>
          </div>
        </div>

        <div className="telemetry-card">
          <div className="telemetry-label">Flow Out Paddle</div>
          <div className="telemetry-value">
            {t.flow_out_pct?.toFixed(1)}
            <span className="telemetry-unit">%</span>
          </div>
        </div>

        <div className="telemetry-card">
          <div className="telemetry-label">Pit Volume</div>
          <div className="telemetry-value">
            {t.pit_volume?.toFixed(1)}
            <span className="telemetry-unit">m³</span>
          </div>
        </div>

        <div className="telemetry-card">
          <div className="telemetry-label">Dynamic ECD</div>
          <div className="telemetry-value" style={{ color: '#00f0ff' }}>
            {t.ecd?.toFixed(3)}
            <span className="telemetry-unit">SG</span>
          </div>
        </div>

        <div className="telemetry-card">
          <div className="telemetry-label">MWD Gamma Ray</div>
          <div className="telemetry-value">
            {t.gamma_ray?.toFixed(1)}
            <span className="telemetry-unit">API</span>
          </div>
        </div>
      </div>
    </div>
  );
}
