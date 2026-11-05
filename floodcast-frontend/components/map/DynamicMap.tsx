'use client';

import React from 'react';
import dynamic from 'next/dynamic';
import { Loader2 } from 'lucide-react';

const StationMapDynamic = dynamic(() => import('./StationMap'), {
  ssr: false,
  loading: () => (
    <div className="flex h-full min-h-[500px] w-full flex-col items-center justify-center rounded-2xl border border-slate-800 bg-slate-900/50 p-8 text-center">
      <Loader2 className="h-8 w-8 animate-spin text-cyan-400 mb-2" />
      <p className="text-sm font-semibold text-slate-300">Loading Leaflet Gauge Map...</p>
      <p className="text-xs text-slate-500">Connecting to USGS Geodetic Coordinates</p>
    </div>
  ),
});

export const DynamicMap: React.FC = () => {
  return (
    <div className="h-full w-full flex-1 flex flex-col">
      <StationMapDynamic />
    </div>
  );
};
