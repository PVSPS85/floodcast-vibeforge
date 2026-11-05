'use client';

import React from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Area,
  Line,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ReferenceLine,
  CartesianGrid,
} from 'recharts';
import { motion } from 'framer-motion';
import { useStationStore, TimeRange } from '@/store/useStationStore';
import { formatCFS, formatDate } from '@/lib/utils';
import { CloudRain, Waves, Sparkles, Loader2, AlertCircle, RefreshCw } from 'lucide-react';

interface CustomTooltipProps {
  active?: boolean;
  payload?: any[];
  label?: string;
}

const CustomTooltip: React.FC<CustomTooltipProps> = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="rounded-xl border border-slate-700/80 bg-slate-900/95 p-3.5 shadow-2xl backdrop-blur-md text-xs space-y-2 min-w-[210px]">
        <div className="border-b border-slate-800 pb-1.5 flex items-center justify-between">
          <span className="font-semibold text-slate-200">{data.date}</span>
          <span className="text-[10px] text-cyan-400 font-mono">
            {data.is_forecast ? '🔮 ML Forecast' : 'Observed Telemetry'}
          </span>
        </div>

        <div className="space-y-1">
          <div className="flex items-center justify-between text-blue-400 font-medium">
            <span className="flex items-center space-x-1.5">
              <CloudRain className="h-3.5 w-3.5" />
              <span>Precipitation:</span>
            </span>
            <span className="font-bold">{data.precipitation_mm} mm</span>
          </div>

          <div className="flex items-center justify-between text-cyan-300 font-medium">
            <span className="flex items-center space-x-1.5">
              <Sparkles className="h-3.5 w-3.5 text-cyan-400" />
              <span>Predicted Flow:</span>
            </span>
            <span className="font-bold">{formatCFS(data.discharge_cfs)}</span>
          </div>

          {data.soil_moisture !== undefined && (
            <div className="flex items-center justify-between text-slate-400">
              <span>Soil Moisture:</span>
              <span className="font-mono text-slate-200">{data.soil_moisture}</span>
            </div>
          )}
        </div>

        <div className="pt-1 border-t border-slate-800/80 flex justify-between text-[10px] text-slate-400">
          <span>High: {data.temp_max_c}°C</span>
          <span>Low: {data.temp_min_c}°C</span>
        </div>
      </div>
    );
  }
  return null;
};

export const CauseEffectChart: React.FC = () => {
  const {
    selectedStation,
    stationData,
    timeseries,
    timeRange,
    setTimeRange,
    isLoading,
    error,
    refetchCurrentStation,
  } = useStationStore();

  const timeRanges: TimeRange[] = ['7d', '30d', '90d'];

  // Display stationData sliced by active time range, or fallback to stationData
  const chartData = timeseries.length > 0 ? timeseries : stationData;

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="rounded-2xl border border-slate-800/80 bg-slate-900/70 p-5 backdrop-blur-md shadow-xl flex flex-col justify-between h-full"
    >
      {/* Header with Title and Range Picker */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4 shrink-0">
        <div>
          <div className="flex items-center space-x-2">
            <h2 className="text-base sm:text-lg font-bold text-slate-100 flex items-center space-x-2">
              <Waves className="h-5 w-5 text-cyan-400" />
              <span>Precipitation &bull; Discharge Hydrograph</span>
            </h2>
            <span className="rounded bg-cyan-950/80 px-2 py-0.5 text-[10px] font-semibold text-cyan-300 border border-cyan-800/40">
              Live Real Data
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            USGS NWIS Rainfall Pulse vs. CatBoost ML Discharge Inference for{' '}
            <span className="text-slate-200 font-semibold">{selectedStation.name}</span>
          </p>
        </div>

        {/* Time range selection pills */}
        <div className="flex items-center space-x-1 rounded-xl bg-slate-950 p-1 border border-slate-800">
          {timeRanges.map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`rounded-lg px-3 py-1 text-xs font-semibold uppercase tracking-wider transition ${
                timeRange === range
                  ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/20'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
              }`}
            >
              {range}
            </button>
          ))}
        </div>
      </div>

      {/* Chart Canvas Area with Skeleton / Loading State */}
      <div className="flex-1 min-h-[380px] w-full relative flex flex-col justify-center">
        {isLoading ? (
          <div className="flex h-full w-full flex-col items-center justify-center space-y-3 rounded-xl border border-slate-800/60 bg-slate-950/40 p-8 text-center backdrop-blur-sm">
            <Loader2 className="h-8 w-8 animate-spin text-cyan-400" />
            <p className="text-sm font-semibold text-slate-200">Loading Hydrograph Telemetry...</p>
            <p className="text-xs text-slate-500">
              Streaming real dataset &amp; CatBoost inference for gauge #{selectedStation.station_id}
            </p>
          </div>
        ) : error ? (
          <div className="flex h-full w-full flex-col items-center justify-center space-y-3 rounded-xl border border-rose-900/40 bg-rose-950/20 p-8 text-center">
            <AlertCircle className="h-8 w-8 text-rose-400" />
            <p className="text-sm font-semibold text-rose-300">Failed to load real telemetry</p>
            <p className="text-xs text-slate-400 max-w-md">{error}</p>
            <button
              onClick={() => refetchCurrentStation()}
              className="mt-2 flex items-center space-x-1.5 rounded-lg border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs font-medium text-slate-200 transition hover:bg-slate-700"
            >
              <RefreshCw className="h-3.5 w-3.5 text-cyan-400" />
              <span>Retry Query</span>
            </button>
          </div>
        ) : chartData.length === 0 ? (
          <div className="flex h-full w-full flex-col items-center justify-center p-8 text-center text-xs text-slate-500">
            No telemetry records found for this station.
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={chartData} margin={{ top: 10, right: 20, left: 10, bottom: 0 }}>
              <defs>
                <linearGradient id="qGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#06b6d4" stopOpacity={0.0} />
                </linearGradient>
                <linearGradient id="rainGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.7} />
                  <stop offset="100%" stopColor="#3b82f6" stopOpacity={0.15} />
                </linearGradient>
              </defs>

              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" opacity={0.7} />

              <XAxis
                dataKey="date"
                tickFormatter={formatDate}
                stroke="#64748b"
                tick={{ fontSize: 11 }}
                tickLine={false}
              />

              {/* Left Y Axis: Discharge Flow (cfs) */}
              <YAxis
                yAxisId="left"
                stroke="#64748b"
                tickFormatter={(val) => formatCFS(val).replace(' cfs', '')}
                tick={{ fontSize: 11 }}
                tickLine={false}
                axisLine={false}
              />

              {/* Right Y Axis: Inverted Precipitation (mm) */}
              <YAxis
                yAxisId="right"
                orientation="right"
                reversed={true}
                domain={[0, 80]}
                stroke="#3b82f6"
                tickFormatter={(v) => `${v}mm`}
                tick={{ fontSize: 10 }}
                tickLine={false}
                axisLine={false}
              />

              <Tooltip content={<CustomTooltip />} />

              <Legend
                verticalAlign="top"
                align="right"
                wrapperStyle={{ paddingBottom: '10px', fontSize: '11px' }}
              />

              {/* Bar: Precipitation Pulse (Cause) */}
              <Bar
                yAxisId="right"
                dataKey="precipitation_mm"
                name="Precipitation (mm)"
                fill="url(#rainGrad)"
                radius={[0, 0, 4, 4]}
                maxBarSize={14}
              />

              {/* Line: Model's Discharge Prediction (Effect) */}
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="discharge_cfs"
                name="CatBoost Predicted Discharge (cfs)"
                stroke="#22d3ee"
                strokeWidth={2.5}
                dot={{ r: 2, fill: '#06b6d4' }}
                activeDot={{ r: 5, fill: '#38bdf8' }}
              />

              {/* Action Stage Threshold Reference Line */}
              {selectedStation.action_stage_cfs ? (
                <ReferenceLine
                  yAxisId="left"
                  y={selectedStation.action_stage_cfs}
                  label={{
                    value: `Action: ${formatCFS(selectedStation.action_stage_cfs)}`,
                    fill: '#f59e0b',
                    fontSize: 10,
                    position: 'insideTopLeft',
                  }}
                  stroke="#f59e0b"
                  strokeDasharray="3 3"
                />
              ) : null}

              {/* Flood Stage Threshold Reference Line */}
              {selectedStation.flood_stage_cfs ? (
                <ReferenceLine
                  yAxisId="left"
                  y={selectedStation.flood_stage_cfs}
                  label={{
                    value: `Flood: ${formatCFS(selectedStation.flood_stage_cfs)}`,
                    fill: '#f43f5e',
                    fontSize: 10,
                    position: 'insideTopLeft',
                  }}
                  stroke="#f43f5e"
                  strokeWidth={1.5}
                />
              ) : null}
            </ComposedChart>
          </ResponsiveContainer>
        )}
      </div>
    </motion.div>
  );
};
