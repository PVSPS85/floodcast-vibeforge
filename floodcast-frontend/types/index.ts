export type FloodStatus = 'normal' | 'advisory' | 'warning' | 'flood';

export type AlertSeverity = 'info' | 'moderate' | 'severe' | 'extreme';

export interface Station {
  station_id: string;
  name: string;
  river: string;
  state: string;
  lat: number;
  lon: number;
  drainage_area_sqmi: number;
  mean_elevation_ft: number;
  slope_pct: number;
  forest_cover_pct: number;
  flood_stage_cfs: number;
  action_stage_cfs: number;
  current_discharge_cfs: number;
  predicted_peak_cfs: number;
  status: FloodStatus;
}

export interface DischargePoint {
  date: string;
  discharge_cfs: number;
  pred_discharge_cfs: number;
  precipitation_mm: number;
  temp_max_c: number;
  temp_min_c: number;
  soil_moisture: number;
}

export interface ModelMetrics {
  overall_rmse: number;
  extreme_rmse: number;
  overall_mae: number;
  overall_r2: number;
  composite_score?: number;
  training_samples: number;
  test_samples: number;
  peak_weight: number;
  algorithm: string;
}

export interface Alert {
  id: string;
  station_id: string;
  station_name: string;
  river: string;
  severity: AlertSeverity;
  timestamp: string;
  message: string;
  predicted_discharge: number;
  threshold_cfs: number;
  hours_to_peak: number;
}

