import { create } from 'zustand';
import { Station, DischargePoint, ModelMetrics, Alert } from '@/types';
import {
  INITIAL_STATIONS,
  INITIAL_METRICS,
  INITIAL_ALERTS,
  generateTimeseries,
} from '@/lib/api';

export type TimeRange = '7d' | '30d' | '90d';

interface StationState {
  stations: Station[];
  selectedStation: Station;
  timeseries: DischargePoint[];
  modelMetrics: ModelMetrics;
  alerts: Alert[];
  timeRange: TimeRange;
  searchQuery: string;
  isLoadingTimeseries: boolean;

  // Actions
  setSelectedStation: (station: Station) => void;
  setSelectedStationById: (id: string) => void;
  setTimeRange: (range: TimeRange) => void;
  setSearchQuery: (query: string) => void;
}

const getDaysFromRange = (range: TimeRange): number => {
  switch (range) {
    case '7d':
      return 7;
    case '90d':
      return 90;
    case '30d':
    default:
      return 30;
  }
};

export const useStationStore = create<StationState>((set, get) => {
  const defaultStation = INITIAL_STATIONS[0];
  const initialTimeseries = generateTimeseries(defaultStation, 30);

  return {
    stations: INITIAL_STATIONS,
    selectedStation: defaultStation,
    timeseries: initialTimeseries,
    modelMetrics: INITIAL_METRICS,
    alerts: INITIAL_ALERTS,
    timeRange: '30d',
    searchQuery: '',
    isLoadingTimeseries: false,

    setSelectedStation: (station: Station) => {
      const days = getDaysFromRange(get().timeRange);
      set({ isLoadingTimeseries: true, selectedStation: station });
      const newTimeseries = generateTimeseries(station, days);
      set({ timeseries: newTimeseries, isLoadingTimeseries: false });
    },

    setSelectedStationById: (id: string) => {
      const found = get().stations.find((s) => s.station_id === id);
      if (found) {
        get().setSelectedStation(found);
      }
    },

    setTimeRange: (range: TimeRange) => {
      set({ timeRange: range, isLoadingTimeseries: true });
      const days = getDaysFromRange(range);
      const newTimeseries = generateTimeseries(get().selectedStation, days);
      set({ timeseries: newTimeseries, isLoadingTimeseries: false });
    },

    setSearchQuery: (query: string) => {
      set({ searchQuery: query });
    },
  };
});

