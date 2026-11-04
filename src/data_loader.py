import os
import pandas as pd
import requests

def fetch_usgs_discharge(site_id="01646500", start_date="2018-01-01", end_date="2023-12-31"):
    url = f"https://waterservices.usgs.gov/nwis/dv/?format=json&sites={site_id}&startDT={start_date}&endDT={end_date}&parameterCd=00060"
    print(f"📥 Querying USGS API for Station {site_id}...")
    response = requests.get(url)
    if response.status_code != 200:
        print(f"⚠️ Warning: USGS API failed for site {site_id}")
        return pd.DataFrame()
    try:
        data = response.json()
        time_series = data['value']['timeSeries'][0]['values'][0]['value']
        df = pd.DataFrame(time_series)
        df['discharge_cfs'] = pd.to_numeric(df['value'], errors='coerce')
        df['date'] = pd.to_datetime(df['dateTime']).dt.strftime('%Y-%m-%d')
        df['station_id'] = f"STN_{site_id}"
        return df[['station_id', 'date', 'discharge_cfs']].dropna()
    except Exception as e:
        print(f"❌ Error parsing USGS JSON: {e}")
        return pd.DataFrame()

def fetch_open_meteo_weather(lat=38.8951, lon=-77.0364, start_date="2018-01-01", end_date="2023-12-31"):
    url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&daily=precipitation_sum,temperature_2m_max,temperature_2m_min,soil_moisture_0_to_7cm&timezone=America/New_York"
    print("☁️ Querying Open-Meteo Weather API...")
    response = requests.get(url)
    if response.status_code != 200:
        print("⚠️ Warning: Open-Meteo API failed")
        return pd.DataFrame()
    try:
        data = response.json()
        daily = data.get('daily', {})
        df = pd.DataFrame({
            'date': daily.get('time'),
            'precipitation_sum': daily.get('precipitation_sum'),
            'temperature_2m_max': daily.get('temperature_2m_max'),
            'temperature_2m_min': daily.get('temperature_2m_min'),
            'soil_moisture_0_to_7cm': daily.get('soil_moisture_0_to_7cm')
        })
        return df
    except Exception as e:
        print(f"❌ Error parsing Open-Meteo JSON: {e}")
        return pd.DataFrame()

def build_pipeline():
    os.makedirs("data", exist_ok=True)
    usgs_df = fetch_usgs_discharge()
    weather_df = fetch_open_meteo_weather()
    if usgs_df.empty or weather_df.empty:
        print("❌ Error: Failed to fetch API data.")
        return
    master_df = pd.merge(usgs_df, weather_df, on="date", how="inner").sort_values("date").reset_index(drop=True)
    split_idx = int(len(master_df) * 0.8)
    master_df.iloc[:split_idx].to_csv("data/train.csv", index=False)
    master_df.iloc[split_idx:].to_csv("data/test.csv", index=False)
    print("🎉 Data pipeline executed successfully! train.csv and test.csv populated.")

if __name__ == "__main__":
    build_pipeline()
