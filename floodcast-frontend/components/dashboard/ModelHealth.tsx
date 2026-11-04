'use client';

import React from 'react';
import { useStationStore } from '@/store/useStationStore';
import { Cpu, CheckCircle, BarChart3, Target, Award, Layers } from 'lucide-react';
import { motion } from 'framer-motion';

export const ModelHealth: React.FC = () => {
  const { modelMetrics } = useStationStore();

  const metrics = [
    {
      title: 'Overall RMSE',
      weight: '40% weight',
      value: `${modelMetrics.overall_rmse.toFixed(1)} cfs`,
      sub: 'All samples evaluated',
      color: 'text-cyan-400',
      bgColor: 'bg-cyan-500/10',
      borderColor: 'border-cyan-500/30',
    },
    {
      title: 'Extreme Event RMSE',
      weight: '30% weight',
      value: `${modelMetrics.extreme_rmse.toFixed(1)} cfs`,
      sub: 'Top 10% peak days / station',
      color: 'text-amber-400',
      bgColor: 'bg-amber-500/10',
      borderColor: 'border-amber-500/30',
    },
    {
      title: 'Overall MAE',
      weight: '20% weight',
      value: `${modelMetrics.overall_mae.toFixed(1)} cfs`,
      sub: 'Mean absolute error',
      color: 'text-indigo-400',
      bgColor: 'bg-indigo-500/10',
      borderColor: 'border-indigo-500/30',
    },
    {
      title: 'Coefficient R²',
      weight: '10% weight',
      value: `${modelMetrics.overall_r2.toFixed(3)}`,
      sub: 'Variance explained',
      color: 'text-emerald-400',
      bgColor: 'bg-emerald-500/10',
      borderColor: 'border-emerald-500/30',
    },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.2 }}
      className="rounded-2xl border border-slate-800/80 bg-slate-900/70 p-5 backdrop-blur-md shadow-xl flex flex-col justify-between"
    >
      <div>
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <Cpu className="h-5 w-5 text-purple-400" />
            <h3 className="text-base font-bold text-slate-100">CatBoost Model Health &amp; Benchmarks</h3>
          </div>
          <span className="flex items-center space-x-1.5 rounded-full bg-emerald-950/80 border border-emerald-800/40 px-2.5 py-0.5 text-[10px] font-bold text-emerald-400">
            <CheckCircle className="h-3 w-3" />
            <span>Optimal Convergence</span>
          </span>
        </div>

        <p className="text-xs text-slate-400 mb-4">
          Strict chronological out-of-time evaluation across 50 benchmark river basins using competition scoring weights:
        </p>

        {/* 4 Official Hackathon Metrics Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
          {metrics.map((m) => (
            <div
              key={m.title}
              className={`rounded-xl border ${m.borderColor} ${m.bgColor} p-3 space-y-1`}
            >
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-semibold text-slate-300 truncate">{m.title}</span>
                <span className="text-[9px] font-mono text-slate-400 uppercase tracking-wider">{m.weight}</span>
              </div>
              <div className={`text-xl font-extrabold tracking-tight ${m.color}`}>{m.value}</div>
              <p className="text-[10px] text-slate-400 truncate">{m.sub}</p>
            </div>
          ))}
        </div>

        {/* Model Architecture Specifications */}
        <div className="rounded-xl border border-slate-800 bg-slate-950/70 p-3 text-xs space-y-2">
          <div className="flex items-center justify-between font-semibold text-slate-300">
            <span className="flex items-center space-x-1.5">
              <Layers className="h-3.5 w-3.5 text-cyan-400" />
              <span>Training Hyperparameters &amp; Bounds</span>
            </span>
            <span className="text-[11px] font-mono text-purple-400">{modelMetrics.algorithm}</span>
          </div>

          <div className="grid grid-cols-3 gap-2 text-[11px] pt-1">
            <div className="bg-slate-900/80 p-2 rounded border border-slate-800">
              <span className="text-slate-500 block text-[10px]">Peak Event Weight</span>
              <span className="font-bold text-slate-200">{modelMetrics.peak_weight}x (Top 15%)</span>
            </div>
            <div className="bg-slate-900/80 p-2 rounded border border-slate-800">
              <span className="text-slate-500 block text-[10px]">Non-Negative Clip</span>
              <span className="font-bold text-slate-200">np.clip(&ge; 0) Active</span>
            </div>
            <div className="bg-slate-900/80 p-2 rounded border border-slate-800">
              <span className="text-slate-500 block text-[10px]">Dataset Samples</span>
              <span className="font-bold text-slate-200">{modelMetrics.training_samples.toLocaleString()} rows</span>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-500">
        <span>Validation: Out-of-time chronological 20% holdout</span>
        <span className="font-mono text-emerald-400 font-semibold">Leaderboard Ready</span>
      </div>
    </motion.div>
  );
};

