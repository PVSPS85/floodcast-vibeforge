import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { FloodStatus, AlertSeverity } from '@/types';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCFS(val: number): string {
  if (val >= 1_000_000) {
    return `${(val / 1_000_000).toFixed(2)}M cfs`;
  }
  if (val >= 1_000) {
    return `${(val / 1_000).toFixed(1)}k cfs`;
  }
  return `${Math.round(val)} cfs`;
}

export function formatDate(dateStr: string): string {
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

export function getStatusColor(status: FloodStatus) {
  switch (status) {
    case 'flood':
      return {
        bg: 'bg-rose-500/10',
        text: 'text-rose-400',
        border: 'border-rose-500/30',
        dot: 'bg-rose-500',
        hex: '#f43f5e',
      };
    case 'warning':
      return {
        bg: 'bg-amber-500/10',
        text: 'text-amber-400',
        border: 'border-amber-500/30',
        dot: 'bg-amber-500',
        hex: '#f59e0b',
      };
    case 'advisory':
      return {
        bg: 'bg-cyan-500/10',
        text: 'text-cyan-400',
        border: 'border-cyan-500/30',
        dot: 'bg-cyan-500',
        hex: '#06b6d4',
      };
    case 'normal':
    default:
      return {
        bg: 'bg-emerald-500/10',
        text: 'text-emerald-400',
        border: 'border-emerald-500/30',
        dot: 'bg-emerald-500',
        hex: '#10b981',
      };
  }
}

export function getSeverityBadge(severity: AlertSeverity) {
  switch (severity) {
    case 'extreme':
      return 'bg-rose-500/20 text-rose-300 border-rose-500/40 animate-pulse';
    case 'severe':
      return 'bg-orange-500/20 text-orange-300 border-orange-500/40';
    case 'moderate':
      return 'bg-amber-500/20 text-amber-300 border-amber-500/40';
    case 'info':
    default:
      return 'bg-blue-500/20 text-blue-300 border-blue-500/40';
  }
}

