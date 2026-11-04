'use client';

import React from 'react';
import { MainLayout } from '@/components/layout/MainLayout';
import { DynamicMap } from '@/components/map/DynamicMap';
import { CauseEffectChart } from '@/components/charts/CauseEffectChart';
import { CatchmentProfile } from '@/components/dashboard/CatchmentProfile';
import { ExtremeAlerts } from '@/components/dashboard/ExtremeAlerts';
import { ModelHealth } from '@/components/dashboard/ModelHealth';
import { useStationStore } from '@/store/useStationStore';
import { formatCFS, getStatusColor } from '@/lib/utils';
import { Activity, ShieldAlert, Waves, Compass, Droplet } from 'lucide-react';

export default function DashboardPage() {
  const { selectedStation } = useStationStore();
  const statusStyle = getStatusColor(selectedStation.status);

  return (
    <MainLayout>
      {/* Top Hero Station Summary Banner */}
      <div className="rounded-2xl border border-slate-800/90 bg-gradient-to-r from-slate-900/90 via-slate-900/60 to-slate-950 p-5 shadow-xl backdrop-blur-md">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center space-x-2.5">
              <span className="font-mono text-xs font-bold text-cyan-400 bg-cyan-950/80 px-2 py-0.5 rounded border border-cyan-800/40">
                USGS #{selectedStation.station_id}
              </span>
              <h1 className="text-xl sm:text-2xl font-extrabold text-white tracking-tight">
                {selectedStation.name}
              </h1>
            </div>
            <p className="text-xs text-slate-400 flex items-center space-x-2">
              <span>{selectedStation.river}</span>
              <span>&bull;</span>
              <span>State: {selectedStation.state}</span>
              <span>&bull;</span>
              <span>Drainage Area: {selectedStation.drainage_area_sqmi.toLocaleString()} sq mi</span>
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <div className="rounded-xl border border-slate-800 bg-slate-950/70 px-4 py-2 text-right">
              <span className="block text-[10px] text-slate-400 font-medium">Real-Time Discharge</span>
              <span className="text-lg font-extrabold text-emerald-400">
                {formatCFS(selectedStation.current_discharge_cfs)}
              </span>
            </div>

            <div className="rounded-xl border border-slate-800 bg-slate-950/70 px-4 py-2 text-right">
              <span className="block text-[10px] text-slate-400 font-medium">Predicted Peak Flow</span>
              <span className="text-lg font-extrabold text-cyan-400">
                {formatCFS(selectedStation.predicted_peak_cfs)}
              </span>
            </div>

            <div
              className={`rounded-xl border px-4 py-2 text-right ${statusStyle.bg} ${statusStyle.border}`}
            >
              <span className="block text-[10px] text-slate-400 font-medium">Hydrologic Stage</span>
              <span className={`text-lg font-extrabold capitalize ${statusStyle.text}`}>
                {selectedStation.status}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Primary Dashboard Grid: Map + Hydrograph */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
        {/* Left Column: Leaflet Map */}
        <div className="lg:col-span-5 h-[480px]">
          <DynamicMap />
        </div>

        {/* Right Column: Hydrograph Cause-Effect Chart */}
        <div className="lg:col-span-7 h-[480px]">
          <CauseEffectChart />
        </div>
      </div>

      {/* Secondary Dashboard Grid: Catchment Profile + Extreme Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
        <div className="lg:col-span-6">
          <CatchmentProfile />
        </div>
        <div className="lg:col-span-6">
          <ExtremeAlerts />
        </div>
      </div>

      {/* Model Health Benchmarks Banner */}
      <div className="w-full">
        <ModelHealth />
      </div>
    </MainLayout>
  );
}

