'use client';

import React from 'react';
import { useStationStore } from '@/store/useStationStore';
import { AlertTriangle, Clock, ShieldAlert, ArrowUpRight, CheckCircle2 } from 'lucide-react';
import { formatCFS, getSeverityBadge } from '@/lib/utils';
import { motion } from 'framer-motion';

export const ExtremeAlerts: React.FC = () => {
  const { alerts, setSelectedStationById, selectedStation } = useStationStore();

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.15 }}
      className="rounded-2xl border border-slate-800/80 bg-slate-900/70 p-5 backdrop-blur-md shadow-xl flex flex-col justify-between"
    >
      <div>
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <div className="p-1 rounded-md bg-rose-500/10 text-rose-400">
              <ShieldAlert className="h-5 w-5" />
            </div>
            <h3 className="text-base font-bold text-slate-100">Active Extreme Flood Alerts</h3>
          </div>
          <span className="flex items-center space-x-1.5 rounded-full bg-rose-950/80 border border-rose-800/40 px-2 py-0.5 text-[10px] font-bold text-rose-400">
            <span className="h-1.5 w-1.5 rounded-full bg-rose-500 animate-ping" />
            <span>{alerts.length} Warnings Active</span>
          </span>
        </div>

        <p className="text-xs text-slate-400 mb-3">
          Stations where CatBoost ML inference forecasts peak flow exceeding the 90th percentile extreme event threshold:
        </p>

        <div className="space-y-2.5 max-h-[300px] overflow-y-auto pr-1">
          {alerts.map((alert) => {
            const isCurrent = alert.station_id === selectedStation.station_id;
            return (
              <div
                key={alert.id}
                onClick={() => setSelectedStationById(alert.station_id)}
                className={`group cursor-pointer rounded-xl border p-3 transition ${
                  isCurrent
                    ? 'border-cyan-500/60 bg-cyan-950/20 shadow-md shadow-cyan-950/40'
                    : 'border-slate-800 bg-slate-950/60 hover:border-slate-700 hover:bg-slate-900/60'
                }`}
              >
                <div className="flex items-center justify-between mb-1.5">
                  <div className="flex items-center space-x-2">
                    <span
                      className={`rounded-md border px-1.5 py-0.5 text-[10px] font-bold uppercase tracking-wider ${getSeverityBadge(
                        alert.severity
                      )}`}
                    >
                      {alert.severity}
                    </span>
                    <span className="text-xs font-bold text-slate-200 group-hover:text-cyan-400 transition flex items-center">
                      {alert.station_name}
                      <ArrowUpRight className="h-3 w-3 ml-0.5 opacity-0 group-hover:opacity-100 transition" />
                    </span>
                  </div>
                  <span className="flex items-center text-[10px] text-slate-500 space-x-1">
                    <Clock className="h-3 w-3" />
                    <span>{alert.timestamp}</span>
                  </span>
                </div>

                <p className="text-[11px] text-slate-300 mb-2 leading-relaxed">{alert.message}</p>

                <div className="flex items-center justify-between text-[10px] bg-slate-900/90 rounded-lg px-2.5 py-1.5 border border-slate-800/80">
                  <div className="flex items-center space-x-1 text-slate-400">
                    <span>Forecast Peak:</span>
                    <span className="font-bold text-rose-400">{formatCFS(alert.predicted_discharge)}</span>
                  </div>
                  <div className="text-slate-400">
                    Threshold: <span className="text-slate-200 font-semibold">{formatCFS(alert.threshold_cfs)}</span>
                  </div>
                  <div className="font-semibold text-amber-400">
                    &Delta; T - {alert.hours_to_peak}h
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400">
        <span className="flex items-center space-x-1">
          <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
          <span>Continuous USGS telemetry check</span>
        </span>
        <span className="text-[10px] font-mono text-cyan-400">90th-pct sample weighted</span>
      </div>
    </motion.div>
  );
};

