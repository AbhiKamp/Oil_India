import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'StrataSentry-NWIS | Tactical Drilling Operations HUD',
  description: 'National Well Intelligence System & Real-Time Drilling Hazard Mitigation Platform',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
