import type { Metadata } from 'next';
import 'leaflet/dist/leaflet.css';
import './globals.css';

export const metadata: Metadata = {
  title: 'Floodcast | AI River Discharge & Flood Forecasting',
  description:
    'Real-time hydrological forecasting dashboard powered by USGS NWIS telemetry and CatBoost Machine Learning.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-slate-950 text-slate-100 font-sans antialiased selection:bg-cyan-500/20 selection:text-cyan-200">
        {children}
      </body>
    </html>
  );
}
