'use client';

import React from 'react';
import { useStationStore } from '@/store/useStationStore';
import { Waves, Cpu, Search, Activity, ShieldAlert } from 'lucide-react';
import { getStatusColor } from '@/lib/utils';

export const Topbar: React.FC = () => {
  const { stations, selectedStation, setSelectedStationById, searchQuery, setSearchQuery } =
    useStationStore();

  const filteredStations = stations.filter(
    (s) =>
      s.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.station_id.includes(searchQuery) ||
      s.river.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const statusStyle = getStatusColor(selectedStation.status);

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md">
      <div className="flex h-16 items-center justify-between px-4 sm:px-6">
        {/* Brand */}
        <div className="flex items-center space-x-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-cyan-600 via-blue-600 to-indigo-600 text-white shadow-lg shadow-cyan-500/20">
            <Waves className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-lg font-bold tracking-tight text-white">
                Flood<span className="text-cyan-400">cast</span>
              </span>
              <span className="rounded-full bg-cyan-950/80 px-2 py-0.5 text-[10px] font-semibold text-cyan-400 border border-cyan-800/50">
                USGS Real-Time
              </span>
            </div>
            <p className="text-xs text-slate-400 hidden sm:block">
              Machine Learning River Discharge Forecasting
            </p>
          </div>
        </div>

        {/* Station Search & Selector */}
        <div className="flex items-center space-x-3">
          <div className="relative hidden md:block w-72">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <select
              value={selectedStation.station_id}
              onChange={(e) => setSelectedStationById(e.target.value)}
              className="w-full appearance-none rounded-lg border border-slate-800 bg-slate-900/90 py-1.5 pl-9 pr-8 text-xs font-medium text-slate-200 outline-none transition focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
            >
              {filteredStations.map((station) => (
                <option key={station.station_id} value={station.station_id} className="bg-slate-900 text-slate-100">
                  {station.station_id} - {station.name}
                </option>
              ))}
            </select>
          </div>

          {/* Current Status Pill */}
          <div
            className={`flex items-center space-x-2 rounded-full border px-3 py-1 text-xs font-medium ${statusStyle.bg} ${statusStyle.text} ${statusStyle.border}`}
          >
            <span className={`h-2 w-2 rounded-full ${statusStyle.dot} animate-pulse`} />
            <span className="capitalize">{selectedStation.status} Stage</span>
          </div>

          {/* Model Status Pill */}
          <div className="hidden lg:flex items-center space-x-2 rounded-lg border border-slate-800 bg-slate-900/70 px-3 py-1.5 text-xs text-slate-300">
            <Cpu className="h-3.5 w-3.5 text-purple-400" />
            <span>CatBoost Regressor</span>
            <span className="rounded bg-purple-950/80 px-1.5 py-0.2 text-[10px] font-semibold text-purple-300 border border-purple-800/40">
              R² 0.916
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};

