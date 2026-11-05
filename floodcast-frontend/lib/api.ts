import { Station, DischargePoint, ModelMetrics, Alert } from '@/types';
import realStationsData from './data/stations.json';
import realMetricsData from './data/metrics.json';
import realAlertsData from './data/alerts.json';

// Real USGS Gauge Stations (50 stations across the US)
export const INITIAL_STATIONS: Station[] = realStationsData as Station[];

// Real CatBoost Regressor Model Validation Metrics
export const INITIAL_METRICS: ModelMetrics = realMetricsData as ModelMetrics;

// Real CatBoost Predictive Flood & Stage Exceedance Alerts
export const INITIAL_ALERTS: Alert[] = realAlertsData as Alert[];

/**
 * Real API client function: Fetches combined historical telemetry and
 * CatBoost ML forecasts for a given station from the local API route.
 *
 * @param stationId The USGS station ID (e.g., '01646500')
 * @returns Promise<DischargePoint[]> The ordered timeseries array
 */
export async function fetchStationData(stationId: string): Promise<DischargePoint[]> {
  try {
    const res = await fetch(`/api/stations/${encodeURIComponent(stationId)}`);

    if (!res.ok) {
      let errorMessage = `HTTP error ${res.status}: ${res.statusText}`;
      try {
        const errorJson = await res.json();
        if (errorJson && errorJson.error) {
          errorMessage = errorJson.error;
        }
      } catch {
        // Fallback to HTTP error text
      }
      throw new Error(errorMessage);
    }

    const data: DischargePoint[] = await res.json();
    return data;
  } catch (error: any) {
    console.error(`[API] Failed to fetch data for station '${stationId}':`, error);
    throw error;
  }
}

export async function fetchStations(): Promise<Station[]> {
  return Promise.resolve(INITIAL_STATIONS);
}

export async function fetchModelHealth(): Promise<ModelMetrics> {
  return Promise.resolve(INITIAL_METRICS);
}

export async function fetchExtremeAlerts(): Promise<Alert[]> {
  return Promise.resolve(INITIAL_ALERTS);
}
