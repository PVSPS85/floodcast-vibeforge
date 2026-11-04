'use client';

import React from 'react';
import { useStationStore } from '@/store/useStationStore';
import { Compass, Mountain, Trees, Maximize2, Droplets } from 'lucide-react';
import { motion } from 'framer-motion';

export const CatchmentProfile: React.FC = () => {
  const { selectedStation } = useStationStore();

  const attributes = [
    {
      label: 'Drainage Catchment Area',
      value: `${selectedStation.drainage_area_sqmi.toLocaleString()}`,
      unit: 'sq mi',
      icon: Maximize2,
      color: 'text-cyan-400',
      bgColor: 'bg-cyan-500/10',
      description: 'Total watershed area contributing runoff to this gauge',
    },
    {
      label: 'Mean Basin Elevation',
      value: `${selectedStation.mean_elevation_ft.toLocaleString()}`,
      unit: 'ft above sea',
      icon: Mountain,
      color: 'text-indigo-400',
      bgColor: 'bg-indigo-500/10',
      description: 'Controls orographic precipitation and snowmelt timing',
    },
    {
      label: 'Catchment Mean Slope',
      value: `${selectedStation.slope_pct}`,
      unit: '% grade',
      icon: Compass,
      color: 'text-amber-400',
      bgColor: 'bg-amber-500/10',
      description: 'Steeper slopes accelerate runoff response and time-to-peak',
    },
    {
      label: 'Forest Canopy Cover',
      value: `${selectedStation.forest_cover_pct}`,
      unit: '% forested',
      icon: Trees,
      color: 'text-emerald-400',
      bgColor: 'bg-emerald-500/10',
      description: 'Increases rainfall interception and attenuates flash surges',
    },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.1 }}
      className="rounded-2xl border border-slate-800/80 bg-slate-900/70 p-5 backdrop-blur-md shadow-xl flex flex-col justify-between"
    >
      <div>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Droplets className="h-5 w-5 text-cyan-400" />
            <h3 className="text-base font-bold text-slate-100">Basin Physiographic Drivers</h3>
          </div>
          <span className="text-[10px] font-mono text-slate-400 bg-slate-800/80 px-2 py-0.5 rounded border border-slate-700">
            USGS StreamStats
          </span>
        </div>

        <p className="text-xs text-slate-400 mb-4">
          Static hydrological catchment characteristics fed directly into the CatBoost regressor for station{' '}
          <span className="text-slate-200 font-semibold">{selectedStation.station_id}</span>.
        </p>

        <div className="grid grid-cols-2 gap-3">
          {attributes.map((attr) => {
            const Icon = attr.icon;
            return (
              <div
                key={attr.label}
                className="rounded-xl border border-slate-800 bg-slate-950/60 p-3.5 space-y-1.5 transition hover:border-slate-700"
              >
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-medium text-slate-400 truncate">{attr.label}</span>
                  <div className={`p-1.5 rounded-lg ${attr.bgColor} ${attr.color}`}>
                    <Icon className="h-3.5 w-3.5" />
                  </div>
                </div>
                <div className="flex items-baseline space-x-1">
                  <span className="text-lg font-extrabold text-white tracking-tight">{attr.value}</span>
                  <span className="text-[10px] font-semibold text-slate-400">{attr.unit}</span>
                </div>
                <p className="text-[10px] text-slate-500 leading-tight line-clamp-2">{attr.description}</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Hydraulic Capacity Bar */}
      <div className="mt-4 pt-3 border-t border-slate-800/80">
        <div className="flex justify-between items-center text-xs mb-1.5">
          <span className="text-slate-400">Current / Flood Capacity</span>
          <span className="font-bold text-slate-200">
            {((selectedStation.current_discharge_cfs / selectedStation.flood_stage_cfs) * 100).toFixed(1)}%
          </span>
        </div>
        <div className="h-2 w-full rounded-full bg-slate-800 overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 ${
              selectedStation.status === 'flood'
                ? 'bg-rose-500'
                : selectedStation.status === 'warning'
                ? 'bg-amber-500'
                : 'bg-cyan-500'
            }`}
            style={{
              width: `${Math.min(
                100,
                (selectedStation.current_discharge_cfs / selectedStation.flood_stage_cfs) * 100
              )}%`,
            }}
          />
        </div>
      </div>
    </motion.div>
  );
};

