import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import readline from 'readline';

export interface TimeseriesPoint {
  date: string;
  discharge_cfs: number;
  pred_discharge_cfs: number;
  precipitation_mm: number;
  temp_max_c: number;
  temp_min_c: number;
  soil_moisture: number;
  is_forecast: boolean;
}

/**
 * Resolves path to datasets regardless of whether Next.js
 * is launched from the workspace root or from floodcast-frontend.
 */
function resolveFilePath(...segments: string[]): string {
  const directPath = path.resolve(process.cwd(), ...segments);
  if (fs.existsSync(directPath)) return directPath;

  const parentPath = path.resolve(process.cwd(), '..', ...segments);
  if (fs.existsSync(parentPath)) return parentPath;

  return directPath;
}

/**
 * GET /api/stations/[station_id]
 *
 * Reads real historical USGS telemetry from data/train.csv and
 * ML discharge forecasts from predictions.csv, filters for the
 * requested station_id, and combines them into an ordered time-series.
 */
export async function GET(
  request: NextRequest,
  context: { params: Promise<{ station_id: string }> }
) {
  try {
    const { station_id } = await context.params;

    if (!station_id || typeof station_id !== 'string') {
      return NextResponse.json(
        { error: 'station_id parameter is required' },
        { status: 400 }
      );
    }

    const cleanStationId = decodeURIComponent(station_id).trim();

    const trainPath = resolveFilePath('data', 'train.csv');
    const predPath = resolveFilePath('predictions.csv');
    const testPath = resolveFilePath('data', 'test.csv');

    if (!fs.existsSync(trainPath) || !fs.existsSync(predPath)) {
      return NextResponse.json(
        {
          error: 'Required dataset files not found',
          checkedTrainPath: trainPath,
          checkedPredPath: predPath,
        },
        { status: 500 }
      );
    }

    // Optional: Load test weather to enrich forecast points with precipitation & temperature
    const testWeatherMap = new Map<
      string,
      { precip: number; tmax: number; tmin: number; soil: number }
    >();

    if (fs.existsSync(testPath)) {
      const rlTest = readline.createInterface({
        input: fs.createReadStream(testPath, { encoding: 'utf-8' }),
        crlfDelay: Infinity,
      });

      let isHeader = true;
      for await (const line of rlTest) {
        if (isHeader) {
          isHeader = false;
          continue;
        }
        if (line.startsWith(cleanStationId + ',')) {
          const p = line.split(',');
          // station_id(0), date(1), precipitation_mm(2), temp_max_c(3), temp_min_c(4), soil_moisture(5)
          testWeatherMap.set(p[1], {
            precip: parseFloat(p[2]) || 0,
            tmax: parseFloat(p[3]) || 0,
            tmin: parseFloat(p[4]) || 0,
            soil: parseFloat(p[5]) || 0,
          });
        }
      }
    }

    const timeseries: TimeseriesPoint[] = [];

    // 1. Stream & filter historical data from data/train.csv
    const rlTrain = readline.createInterface({
      input: fs.createReadStream(trainPath, { encoding: 'utf-8' }),
      crlfDelay: Infinity,
    });

    let isTrainHeader = true;
    for await (const line of rlTrain) {
      if (isTrainHeader) {
        isTrainHeader = false;
        continue;
      }

      if (line.startsWith(cleanStationId + ',')) {
        const parts = line.split(',');
        // station_id(0), date(1), precipitation_mm(2), temp_max_c(3), temp_min_c(4),
        // soil_moisture(5), drainage_area(6), elevation(7), slope(8), forest(9), discharge_cfs(10)
        const date = parts[1];
        const actualQ = Math.max(0, parseFloat(parts[10]) || 0);

        timeseries.push({
          date,
          discharge_cfs: actualQ,
          pred_discharge_cfs: actualQ,
          precipitation_mm: parseFloat(parts[2]) || 0,
          temp_max_c: parseFloat(parts[3]) || 0,
          temp_min_c: parseFloat(parts[4]) || 0,
          soil_moisture: parseFloat(parts[5]) || 0,
          is_forecast: false,
        });
      }
    }

    // 2. Stream & filter CatBoost model predictions from predictions.csv
    const rlPred = readline.createInterface({
      input: fs.createReadStream(predPath, { encoding: 'utf-8' }),
      crlfDelay: Infinity,
    });

    let isPredHeader = true;
    for await (const line of rlPred) {
      if (isPredHeader) {
        isPredHeader = false;
        continue;
      }

      if (line.startsWith(cleanStationId + ',')) {
        const parts = line.split(',');
        // station_id(0), date(1), discharge_cfs(2)
        const date = parts[1];
        const predQ = Math.max(0, parseFloat(parts[2]) || 0);
        const weather = testWeatherMap.get(date) || {
          precip: 0,
          tmax: 0,
          tmin: 0,
          soil: 0,
        };

        timeseries.push({
          date,
          discharge_cfs: predQ,
          pred_discharge_cfs: predQ,
          precipitation_mm: weather.precip,
          temp_max_c: weather.tmax,
          temp_min_c: weather.tmin,
          soil_moisture: weather.soil,
          is_forecast: true,
        });
      }
    }

    if (timeseries.length === 0) {
      return NextResponse.json(
        {
          error: `No records found for station_id '${cleanStationId}'`,
          station_id: cleanStationId,
        },
        { status: 404 }
      );
    }

    // Sort chronologically by date
    timeseries.sort((a, b) => a.date.localeCompare(b.date));

    // Support optional limit/days query param (e.g., ?days=90)
    const url = new URL(request.url);
    const daysParam = url.searchParams.get('days');
    const result = daysParam ? timeseries.slice(-parseInt(daysParam, 10)) : timeseries;

    return NextResponse.json(result, { status: 200 });
  } catch (error: any) {
    console.error('Error serving station timeseries API:', error);
    return NextResponse.json(
      { error: 'Internal server error processing station data', details: error.message },
      { status: 500 }
    );
  }
}

