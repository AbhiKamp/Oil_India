'use client';

import React, { useEffect, useRef } from 'react';
import { TrajectoryStation, FormationTop } from '../../lib/types';

interface WellViewer3DProps {
  stations: TrajectoryStation[];
  currentDepth: number;
  formations: FormationTop[];
}

export default function WellViewer3D({ stations, currentDepth, formations }: WellViewer3DProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;
    let angle = 0.45;
    let isDragging = false;
    let lastX = 0;

    const handleMouseDown = (e: MouseEvent) => {
      isDragging = true;
      lastX = e.clientX;
    };
    const handleMouseMove = (e: MouseEvent) => {
      if (isDragging) {
        const delta = e.clientX - lastX;
        angle += delta * 0.005;
        lastX = e.clientX;
      }
    };
    const handleMouseUp = () => { isDragging = false; };

    canvas.addEventListener('mousedown', handleMouseDown);
    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseup', handleMouseUp);

    const render = () => {
      const width = canvas.width = canvas.parentElement?.clientWidth || 800;
      const height = canvas.height = canvas.parentElement?.clientHeight || 380;

      // Dark background with gradient
      const bgGrad = ctx.createLinearGradient(0, 0, 0, height);
      bgGrad.addColorStop(0, '#04070d');
      bgGrad.addColorStop(1, '#09101d');
      ctx.fillStyle = bgGrad;
      ctx.fillRect(0, 0, width, height);

      // Grid Lines & Compass
      ctx.strokeStyle = 'rgba(56, 189, 248, 0.08)';
      ctx.lineWidth = 1;
      for (let y = 40; y < height; y += 40) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
      }

      const centerX = width / 2;
      const scaleY = (height - 60) / 4000; // 0 to 4000m TVD
      const scaleX = 0.28;

      // Draw Formation Horizons (Horizontal Planes)
      formations.forEach((f, idx) => {
        const yPos = 30 + f.tvd_top * scaleY;
        ctx.fillStyle = idx % 2 === 0 ? 'rgba(56, 189, 248, 0.05)' : 'rgba(245, 158, 11, 0.04)';
        const nextTop = (idx + 1 < formations.length) ? formations[idx + 1].tvd_top : 4000;
        const sliceHeight = (nextTop - f.tvd_top) * scaleY;
        ctx.fillRect(40, yPos, width - 80, sliceHeight);

        // Boundary line
        ctx.strokeStyle = 'rgba(56, 189, 248, 0.2)';
        ctx.beginPath();
        ctx.moveTo(40, yPos);
        ctx.lineTo(width - 80, yPos);
        ctx.stroke();

        // Label
        ctx.fillStyle = 'rgba(148, 163, 184, 0.6)';
        ctx.font = '10px "JetBrains Mono", monospace';
        ctx.fillText(`${f.formation_name} (${f.tvd_top}m TVD)`, 50, yPos + 14);
      });

      // Draw Offset Well MOR-118 Trajectory (Faint Blue Dotted)
      ctx.beginPath();
      ctx.setLineDash([4, 4]);
      ctx.strokeStyle = 'rgba(56, 189, 248, 0.35)';
      ctx.lineWidth = 1.5;
      for (let i = 0; i <= 3900; i += 300) {
        const offX = centerX - 60 + Math.sin(angle + 0.3) * (i * 0.12 * scaleX);
        const offY = 30 + i * scaleY;
        if (i === 0) ctx.moveTo(offX, offY);
        else ctx.lineTo(offX, offY);
      }
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.fillText("Offset MOR-118", centerX - 120, 30 + 3800 * scaleY);

      // Draw Active Well NHK-421 Trajectory
      if (stations && stations.length > 0) {
        ctx.beginPath();
        ctx.strokeStyle = '#00f0ff';
        ctx.lineWidth = 3;
        ctx.shadowColor = 'rgba(0, 240, 255, 0.8)';
        ctx.shadowBlur = 10;

        stations.forEach((s, idx) => {
          // 3D projection rotation around center
          const projectedX = centerX + Math.cos(angle) * (s.easting_delta * scaleX) - Math.sin(angle) * (s.northing_delta * scaleX * 0.5);
          const projectedY = 30 + s.true_vertical_depth * scaleY;

          if (idx === 0) ctx.moveTo(projectedX, projectedY);
          else ctx.lineTo(projectedX, projectedY);
        });
        ctx.stroke();
        ctx.shadowBlur = 0; // Reset shadow

        // Active Bit Position Indicator
        const lastStation = stations.find(s => s.measured_depth >= currentDepth) || stations[stations.length - 1];
        if (lastStation) {
          const bitX = centerX + Math.cos(angle) * (lastStation.easting_delta * scaleX) - Math.sin(angle) * (lastStation.northing_delta * scaleX * 0.5);
          const bitY = 30 + lastStation.true_vertical_depth * scaleY;

          // Glowing Bit Pulsar
          ctx.beginPath();
          ctx.arc(bitX, bitY, 7, 0, Math.PI * 2);
          ctx.fillStyle = '#ff0055';
          ctx.shadowColor = '#ff0055';
          ctx.shadowBlur = 16;
          ctx.fill();
          ctx.shadowBlur = 0;

          // Bit Label Callout
          ctx.fillStyle = '#ffffff';
          ctx.font = 'bold 11px "Outfit", sans-serif';
          ctx.fillText(`BIT: ${currentDepth.toFixed(1)}m MD`, bitX + 12, bitY + 4);
        }
      }

      // HUD Overlay watermark
      ctx.fillStyle = 'rgba(255, 255, 255, 0.4)';
      ctx.font = '10px "JetBrains Mono", monospace';
      ctx.fillText("3D MINIMUM CURVATURE VIEW | DRAG TO ROTATE | AZIMUTH: 45°", 16, height - 16);

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      cancelAnimationFrame(animationFrameId);
      canvas.removeEventListener('mousedown', handleMouseDown);
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [stations, currentDepth, formations]);

  return (
    <div className="viewer-3d-box glass-panel">
      <div style={{ position: 'absolute', top: 12, left: 16, zIndex: 10, display: 'flex', gap: 10, alignItems: 'center' }}>
        <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)' }}>3D Wellbore Spatial Profile</span>
        <span className="brand-badge">Real-Time MWD</span>
      </div>
      <canvas ref={canvasRef} style={{ width: '100%', height: '100%', display: 'block', cursor: 'grab' }} />
    </div>
  );
}
