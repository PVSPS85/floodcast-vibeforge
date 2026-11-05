'use client';

import React, { useMemo } from 'react';
import { useStationStore } from '@/store/useStationStore';
import { ShieldAlert, AlertTriangle, Clock, ArrowUpRight, CheckCircle2, Waves } from 'lucide-react';
import { formatCFS, getSeverityBadge } from '@/lib/utils';
import { motion, AnimatePresence } from 'framer-motion';

export const ExtremeAlerts: React.FC = () => {
  const { stationData, alerts, setSelectedStationById, selectedStation } = useStationStore();

  // Scan the active stationData array for the top 10% extreme discharge values
  const { top10Threshold, peakExtremePoint, extremeCount } = useMemo(() => {
    if (!stationData || stationData.length === 0) {
      return { top10Threshold: 0, peakExtremePoint: null, extremeCount: 0 };
    }

    const sortedDischarges = [...stationData]
      .map((d) => d.discharge_cfs)
      .sort((a, b) => a - b);

    // 90th percentile threshold
    const p90Index = Math.floor(sortedDischarges.length * 0.9);
    const threshold = sortedDischarges[p90Index] || 0;

    // Filter points in the top 10% extreme threshold
    const extremes = stationData.filter((d) => d.discharge_cfs >= threshold && d.discharge_cfs > 0);

    // Find the absolute highest peak among the extreme events
    const peak = extremes.reduce<typeof stationData[0] | null>((max, current) => {
      if (!max || current.discharge_cfs > max.discharge_cfs) {
        return current;
      }
      return max;
    }, null);

    return {
      top10Threshold: threshold,
      peakExtremePoint: peak,
      extremeCount: extremes.length,
    };
  }, [stationData]);

  const hasExtreme = peakExtremePoint !== null && peakExtremePoint.discharge_cfs > 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.15 }}
      className="rounded-2xl border border-slate-800/80 bg-slate-900/70 p-5 backdrop-blur-md shadow-xl flex flex-col justify-between h-full"
    >
      <div>
        {/* Header */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <div className={`p-1 rounded-md ${hasExtreme ? 'bg-rose-500/20 text-rose-400' : 'bg-emerald-500/20 text-emerald-400'}`}>
              <ShieldAlert className="h-5 w-5" />
            </div>
            <h3 className="text-base font-bold text-slate-100">Active Extreme Flood Alerts</h3>
          </div>

          <span
            className={`flex items-center space-x-1.5 rounded-full px-2.5 py-0.5 text-[10px] font-bold border ${
              hasExtreme
                ? 'bg-rose-950/80 border-rose-800/60 text-rose-300'
                : 'bg-emerald-950/80 border-emerald-800/60 text-emerald-300'
            }`}
          >
            <span
              className={`h-1.5 w-1.5 rounded-full ${
                hasExtreme ? 'bg-rose-500 animate-ping' : 'bg-emerald-400'
              }`}
            />
            <span>{hasExtreme ? 'Extreme Surge Detected' : 'Nominal Basin Stage'}</span>
          </span>
        </div>

        {/* Dynamic Framer Motion Top-10% Extreme Warning Alert for Active Station */}
        <AnimatePresence mode="wait">
          {hasExtreme ? (
            <motion.div
              key="active-extreme-alert"
              initial={{ opacity: 0, scale: 0.96 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.96 }}
              transition={{ duration: 0.3 }}
              className="mb-3.5 rounded-xl border border-rose-500/70 bg-gradient-to-r from-rose-950/70 via-slate-900/90 to-rose-950/40 p-3.5 shadow-lg shadow-rose-950/30"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-2">
                  <span className="flex h-6 w-6 items-center justify-center rounded-lg bg-rose-500/20 text-rose-400">
                    <AlertTriangle className="h-4 w-4 animate-bounce" />
                  </span>
                  <div>
                    <h4 className="text-xs font-bold text-rose-200">
                      Top 10% Extreme Peak Discharge Exceedance
                    </h4>
                    <p className="text-[10px] text-slate-400">
                      Gauge #{selectedStation.station_id} &bull; {selectedStation.name}
                    </p>
                  </div>
                </div>

                <div className="text-right">
                  <span className="block font-mono text-xs font-extrabold text-rose-400">
                    {formatCFS(peakExtremePoint.discharge_cfs)}
                  </span>
                  <span className="text-[9px] text-slate-400">90th-pct Peak</span>
                </div>
              </div>

              <div className="mt-2.5 flex items-center justify-between rounded-lg bg-slate-950/80 px-2.5 py-1.5 text-[10px] text-slate-300 border border-rose-900/30">
                <span className="flex items-center space-x-1">
                  <Clock className="h-3 w-3 text-cyan-400" />
                  <span>Surge Event Date: <strong className="text-white">{peakExtremePoint.date}</strong></span>
                </span>
                <span>
                  Extreme Threshold: <strong className="text-rose-300">{formatCFS(top10Threshold)}</strong>
                </span>
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="nominal-status"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="mb-3.5 flex items-center space-x-2 rounded-xl border border-emerald-900/40 bg-emerald-950/20 p-3 text-xs text-emerald-300"
            >
              <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-400" />
              <span>No 90th-percentile flood surges currently forecasted for {selectedStation.name}.</span>
            </motion.div>
          )}
        </AnimatePresence>

        <p className="text-xs text-slate-400 mb-2">
          Network-wide stations exceeding regional flood thresholds:
        </p>

        {/* Network Alerts Feed */}
        <div className="space-y-2 max-h-[190px] overflow-y-auto pr-1">
          {alerts.map((alert) => {
            const isCurrent = alert.station_id === selectedStation.station_id;
            return (
              <div
                key={alert.id}
                onClick={() => setSelectedStationById(alert.station_id)}
                className={`group cursor-pointer rounded-xl border p-2.5 transition ${
                  isCurrent
                    ? 'border-cyan-500/60 bg-cyan-950/30 shadow-md shadow-cyan-950/40'
                    : 'border-slate-800 bg-slate-950/60 hover:border-slate-700 hover:bg-slate-900/60'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center space-x-1.5">
                    <span
                      className={`rounded px-1.5 py-0.2 text-[9px] font-bold uppercase tracking-wider ${getSeverityBadge(
                        alert.severity
                      )}`}
                    >
                      {alert.severity}
                    </span>
                    <span className="text-xs font-semibold text-slate-200 group-hover:text-cyan-400 transition flex items-center">
                      {alert.station_name}
                      <ArrowUpRight className="h-3 w-3 ml-0.5 opacity-0 group-hover:opacity-100 transition" />
                    </span>
                  </div>
                  <span className="flex items-center text-[10px] text-slate-500 space-x-1">
                    <Clock className="h-3 w-3" />
                    <span>{alert.timestamp}</span>
                  </span>
                </div>

                <div className="flex items-center justify-between text-[10px] bg-slate-900/80 rounded px-2 py-1 border border-slate-800/80">
                  <span className="text-slate-400">
                    Forecast: <strong className="text-rose-400">{formatCFS(alert.predicted_discharge)}</strong>
                  </span>
                  <span className="text-slate-400">
                    Threshold: <strong className="text-slate-200">{formatCFS(alert.threshold_cfs)}</strong>
                  </span>
                  <span className="font-semibold text-amber-400">
                    &Delta;T: {alert.hours_to_peak}h
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="mt-3 pt-2.5 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400">
        <span className="flex items-center space-x-1">
          <Waves className="h-3.5 w-3.5 text-cyan-400" />
          <span>Continuous USGS telemetry monitoring</span>
        </span>
        <span className="text-[10px] font-mono text-cyan-400">90th-pct Extreme Weighted</span>
      </div>
    </motion.div>
  );
};
