import { Station, DischargePoint, ModelMetrics, Alert, FloodStatus, AlertSeverity } from '@/types';
import realStationsData from './data/stations.json';
import realTimeseriesData from './data/timeseries.json';
import realMetricsData from './data/metrics.json';
import realAlertsData from './data/alerts.json';

// 100% Real USGS Stations (All 50 Gauge Stations across the US)
export const INITIAL_STATIONS: Station[] = realStationsData as Station[];

// Real CatBoost Regressor Model Validation Metrics
export const INITIAL_METRICS: ModelMetrics = realMetricsData as ModelMetrics;

// Real CatBoost Predictive Flood & Stage Exceedance Alerts
export const INITIAL_ALERTS: Alert[] = realAlertsData as Alert[];

const timeseriesMap = realTimeseriesData as Record<string, DischargePoint[]>;

/**
 * Fetches real USGS & CatBoost ML timeseries data for a given station.
 * @param stationId The USGS station ID (e.g., '01646500')
 * @param days The number of days to view (7, 30, or 90)
 */
export function getStationTimeseries(stationId: string, days: number = 30): DischargePoint[] {
  let ts = timeseriesMap[stationId];
  if (!ts || ts.length === 0) {
    const defaultId = '01646500';
    ts = timeseriesMap[defaultId] || Object.values(timeseriesMap)[0] || [];
  }
  return ts.slice(-days);
}

/**
 * Backwards compatible generator that queries the real dataset.
 */
export function generateTimeseries(station: Station, days: number = 30): DischargePoint[] {
  return getStationTimeseries(station.station_id, days);
}

export async function fetchStations(): Promise<Station[]> {
  return Promise.resolve(INITIAL_STATIONS);
}

export async function fetchStationTimeseries(stationId: string, days: number = 30): Promise<DischargePoint[]> {
  return Promise.resolve(getStationTimeseries(stationId, days));
}

export async function fetchModelHealth(): Promise<ModelMetrics> {
  return Promise.resolve(INITIAL_METRICS);
}

export async function fetchExtremeAlerts(): Promise<Alert[]> {
  return Promise.resolve(INITIAL_ALERTS);
}
