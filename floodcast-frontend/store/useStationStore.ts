import { create } from 'zustand';
import { Station, DischargePoint, ModelMetrics, Alert } from '@/types';
import {
  INITIAL_STATIONS,
  INITIAL_METRICS,
  INITIAL_ALERTS,
  fetchStationData,
} from '@/lib/api';

export type TimeRange = '7d' | '30d' | '90d';

export interface StationState {
  stations: Station[];
  selectedStation: Station;
  stationData: DischargePoint[];
  timeseries: DischargePoint[]; // Synchronized alias for chart compatibility
  isLoading: boolean;
  isLoadingTimeseries: boolean; // Synchronized alias for chart compatibility
  error: string | null;
  modelMetrics: ModelMetrics;
  alerts: Alert[];
  timeRange: TimeRange;
  searchQuery: string;

  // Actions
  setSelectedStation: (station: Station) => Promise<void>;
  setSelectedStationById: (id: string) => Promise<void>;
  setTimeRange: (range: TimeRange) => void;
  setSearchQuery: (query: string) => void;
  refetchCurrentStation: () => Promise<void>;
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

  return {
    stations: INITIAL_STATIONS,
    selectedStation: defaultStation,
    stationData: [],
    timeseries: [],
    isLoading: false,
    isLoadingTimeseries: false,
    error: null,
    modelMetrics: INITIAL_METRICS,
    alerts: INITIAL_ALERTS,
    timeRange: '30d',
    searchQuery: '',

    /**
     * Updates selected station and fetches real time-series data
     * from the local /api/stations/[station_id] route.
     */
    setSelectedStation: async (station: Station) => {
      set({
        selectedStation: station,
        isLoading: true,
        isLoadingTimeseries: true,
        error: null,
      });

      try {
        const rawTimeseries = await fetchStationData(station.station_id);
        const days = getDaysFromRange(get().timeRange);
        const displayData = rawTimeseries.slice(-days);

        set({
          stationData: rawTimeseries,
          timeseries: displayData,
          isLoading: false,
          isLoadingTimeseries: false,
          error: null,
        });
      } catch (err: any) {
        const errorMessage = err?.message || `Failed to fetch data for station ${station.station_id}`;
        set({
          stationData: [],
          timeseries: [],
          isLoading: false,
          isLoadingTimeseries: false,
          error: errorMessage,
        });
      }
    },

    setSelectedStationById: async (id: string) => {
      const found = get().stations.find((s) => s.station_id === id);
      if (found) {
        await get().setSelectedStation(found);
      } else {
        // If station ID not yet in the list, create a placeholder and fetch
        const placeholder: Station = {
          station_id: id,
          name: `USGS Gauge #${id}`,
          river: 'Unknown River',
          state: 'US',
          lat: 38.0,
          lon: -95.0,
          drainage_area_sqmi: 0,
          mean_elevation_ft: 0,
          slope_pct: 0,
          forest_cover_pct: 0,
          flood_stage_cfs: 0,
          action_stage_cfs: 0,
          current_discharge_cfs: 0,
          predicted_peak_cfs: 0,
          status: 'normal',
        };
        await get().setSelectedStation(placeholder);
      }
    },

    setTimeRange: (range: TimeRange) => {
      const days = getDaysFromRange(range);
      const allData = get().stationData;
      set({
        timeRange: range,
        timeseries: allData.length > 0 ? allData.slice(-days) : [],
      });
    },

    setSearchQuery: (query: string) => {
      set({ searchQuery: query });
    },

    refetchCurrentStation: async () => {
      const current = get().selectedStation;
      if (current) {
        await get().setSelectedStation(current);
      }
    },
  };
});

// Auto-fetch data on initial client load
if (typeof window !== 'undefined') {
  setTimeout(() => {
    const state = useStationStore.getState();
    if (state.stationData.length === 0 && !state.isLoading) {
      state.setSelectedStation(state.selectedStation);
    }
  }, 0);
}
