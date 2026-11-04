'use client';

import React from 'react';
import { Topbar } from './Topbar';

interface MainLayoutProps {
  children: React.ReactNode;
}

export const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-cyan-500/30 selection:text-cyan-200">
      <Topbar />
      <main className="flex-1 w-full max-w-[1720px] mx-auto p-4 sm:p-6 lg:p-8 space-y-6">
        {children}
      </main>
      <footer className="border-t border-slate-900 bg-slate-950/60 py-4 text-center text-xs text-slate-500">
        Floodcast ML Dashboard &bull; Powered by USGS NWIS, Open-Meteo &amp; CatBoost Regressor &bull; Hackathon Benchmark
      </footer>
    </div>
  );
};

