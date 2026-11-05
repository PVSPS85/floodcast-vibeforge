import { Station, DischargePoint, ModelMetrics, Alert } from '@/types';

export const INITIAL_STATIONS: Station[] = [
  {
    station_id: '01646500',
    name: 'Potomac River near Washington, DC',
    river: 'Potomac River',
    state: 'DC',
    lat: 38.9498,
    lon: -77.1276,
    drainage_area_sqmi: 11560.0,
    mean_elevation_ft: 1200.0,
    slope_pct: 5.5,
    forest_cover_pct: 65.0,
    flood_stage_cfs: 35000.0,
    action_stage_cfs: 20000.0,
    current_discharge_cfs: 8450.0,
    predicted_peak_cfs: 23400.0,
    status: 'advisory',
  },
  {
    station_id: '07010000',
    name: 'Mississippi River at St. Louis, MO',
    river: 'Mississippi River',
    state: 'MO',
    lat: 38.6292,
    lon: -90.1798,
    drainage_area_sqmi: 697000.0,
    mean_elevation_ft: 1100.0,
    slope_pct: 3.2,
    forest_cover_pct: 35.0,
    flood_stage_cfs: 450000.0,
    action_stage_cfs: 320000.0,
    current_discharge_cfs: 385000.0,
    predicted_peak_cfs: 462000.0,
    status: 'flood',
  },
  {
    station_id: '08158000',
    name: 'Colorado River at Austin, TX',
    river: 'Colorado River',
    state: 'TX',
    lat: 30.2467,
    lon: -97.7181,
    drainage_area_sqmi: 38230.0,
    mean_elevation_ft: 1450.0,
    slope_pct: 4.1,
    forest_cover_pct: 28.0,
    flood_stage_cfs: 28000.0,
    action_stage_cfs: 15000.0,
    current_discharge_cfs: 4200.0,
    predicted_peak_cfs: 7100.0,
    status: 'normal',
  },
  {
    station_id: '02087500',
    name: 'Neuse River near Clayton, NC',
    river: 'Neuse River',
    state: 'NC',
    lat: 35.6481,
    lon: -78.4117,
    drainage_area_sqmi: 1140.0,
    mean_elevation_ft: 280.0,
    slope_pct: 2.9,
    forest_cover_pct: 52.0,
    flood_stage_cfs: 14000.0,
    action_stage_cfs: 8500.0,
    current_discharge_cfs: 9200.0,
    predicted_peak_cfs: 12800.0,
    status: 'warning',
  },
  {
    station_id: '11447650',
    name: 'Sacramento River at Freeport, CA',
    river: 'Sacramento River',
    state: 'CA',
    lat: 38.4553,
    lon: -121.5008,
    drainage_area_sqmi: 23500.0,
    mean_elevation_ft: 2100.0,
    slope_pct: 7.8,
    forest_cover_pct: 45.0,
    flood_stage_cfs: 85000.0,
    action_stage_cfs: 55000.0,
    current_discharge_cfs: 31200.0,
    predicted_peak_cfs: 44000.0,
    status: 'normal',
  },
  {
    station_id: '01434000',
    name: 'Delaware River at Montague, NJ',
    river: 'Delaware River',
    state: 'NJ',
    lat: 41.3106,
    lon: -74.7978,
    drainage_area_sqmi: 3480.0,
    mean_elevation_ft: 1420.0,
    slope_pct: 8.4,
    forest_cover_pct: 74.5,
    flood_stage_cfs: 32000.0,
    action_stage_cfs: 18000.0,
    current_discharge_cfs: 6400.0,
    predicted_peak_cfs: 9100.0,
    status: 'normal',
  },
];

export const INITIAL_METRICS: ModelMetrics = {
  overall_rmse: 493.54,
  extreme_rmse: 747.94,
  overall_mae: 279.34,
  overall_r2: 0.916,
  composite_score: 522.61,
  training_samples: 219150,
  test_samples: 36500,
  peak_weight: 2.5,
  algorithm: 'CatBoost Regressor (RMSE Objective)',
};

export const INITIAL_ALERTS: Alert[] = [
  {
    id: 'alt-01',
    station_id: '07010000',
    station_name: 'Mississippi River at St. Louis',
    river: 'Mississippi River',
    severity: 'extreme',
    timestamp: '18 min ago',
    message: 'CatBoost predicts flood stage exceedance within 36 hours due to upstream snowmelt pulse.',
    predicted_discharge: 462000,
    threshold_cfs: 450000,
    hours_to_peak: 34,
  },
  {
    id: 'alt-02',
    station_id: '02087500',
    station_name: 'Neuse River near Clayton',
    river: 'Neuse River',
    severity: 'severe',
    timestamp: '42 min ago',
    message: 'Rapid quickflow accumulation following 68mm convective precipitation cell.',
    predicted_discharge: 12800,
    threshold_cfs: 8500,
    hours_to_peak: 14,
  },
  {
    id: 'alt-03',
    station_id: '01646500',
    station_name: 'Potomac River near Washington',
    river: 'Potomac River',
    severity: 'moderate',
    timestamp: '1 hour ago',
    message: 'Approaching Action Stage threshold with sustained basin-wide soil saturation.',
    predicted_discharge: 23400,
    threshold_cfs: 20000,
    hours_to_peak: 48,
  },
];

export function generateTimeseries(station: Station, days: number = 30): DischargePoint[] {
  const points: DischargePoint[] = [];
  const now = new Date();
  const baseQ = station.current_discharge_cfs;
  const isFloodProne = station.status === 'flood' || station.status === 'warning';

  for (let i = days - 1; i >= 0; i--) {
    const d = new Date(now);
    d.setDate(d.getDate() - i);
    const dateStr = d.toISOString().split('T')[0];

    // Simulate realistic storm surge event around day 18-24
    const stormPeak = Math.exp(-Math.pow((days - i - 21) / 3.5, 2));
    const rain = (isFloodProne ? 35 : 12) * stormPeak + (Math.sin(i * 1.5) > 0.6 ? 8 : 0);
    const soilMoisture = Math.min(0.78, 0.28 + stormPeak * 0.42 + Math.sin(i * 0.2) * 0.05);

    const actualQ = Math.max(
      baseQ * 0.4,
      baseQ * (0.8 + 1.8 * stormPeak + Math.sin(i * 0.4) * 0.15)
    );
    // CatBoost prediction with slight variance and hydrological tracking
    const predQ = Math.max(0, actualQ * (1 + (Math.sin(i * 3.2) * 0.04) + (stormPeak > 0.5 ? 0.02 : -0.01)));

    points.push({
      date: dateStr,
      discharge_cfs: Math.round(actualQ),
      pred_discharge_cfs: Math.round(predQ),
      precipitation_mm: Number(rain.toFixed(1)),
      temp_max_c: Number((18 + Math.sin(i * 0.15) * 6).toFixed(1)),
      temp_min_c: Number((8 + Math.sin(i * 0.15) * 5).toFixed(1)),
      soil_moisture: Number(soilMoisture.toFixed(3)),
    });
  }

  return points;
}

export async function fetchStations(): Promise<Station[]> {
  return Promise.resolve(INITIAL_STATIONS);
}

export async function fetchStationTimeseries(stationId: string, days: number = 30): Promise<DischargePoint[]> {
  const station = INITIAL_STATIONS.find((s) => s.station_id === stationId) || INITIAL_STATIONS[0];
  return Promise.resolve(generateTimeseries(station, days));
}

export async function fetchModelHealth(): Promise<ModelMetrics> {
  return Promise.resolve(INITIAL_METRICS);
}

export async function fetchExtremeAlerts(): Promise<Alert[]> {
  return Promise.resolve(INITIAL_ALERTS);
}

