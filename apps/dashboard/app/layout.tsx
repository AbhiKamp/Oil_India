import type { Metadata } from 'next';
import './globals.css';
import './workbench.css';

export const metadata: Metadata = {
  title: 'StrataSentry NWIS | Nearby Wells Intelligence System',
  description: 'Read-only drilling decision support with source-linked well context.',
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
