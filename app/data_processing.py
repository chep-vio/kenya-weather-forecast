import pandas as pd
import requests
from datetime import datetime

city_portfolio = {
    "Nairobi": {"portfolio": "Urban_Microloans", "lat": -1.286389, "lon": 36.817223},
    "Kisumu": {"portfolio": "Lake_Region_Agri", "lat": -0.091702, "lon": 34.767956},
    "Nakuru": {"portfolio": "High_Potential_Farming", "lat": -0.303099, "lon": 36.080025},
    "Mombasa": {"portfolio": "Coastal_Trade", "lat": -4.043477, "lon": 39.668206}
}

def fetch_weather(lat, lon):
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": "2023-01-01",
        "end_date": "2024-12-31",
        "hourly": "temperature_2m,precipitation,windspeed_10m",
        "timezone": "Africa/Nairobi"
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json()

def get_daily_weather(city):
    meta = city_portfolio[city]
    data = fetch_weather(meta["lat"], meta["lon"])
    rows = []
    hourly = data["hourly"]
    for i in range(len(hourly["time"])):
        rows.append({
            "city": city,
            "portfolio": meta["portfolio"],
            "timestamp": hourly["time"][i],
            "temperature": hourly["temperature_2m"][i],
            "precipitation": hourly["precipitation"][i],
            "windspeed": hourly["windspeed_10m"][i]
        })
    df = pd.DataFrame(rows)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["date"] = df["timestamp"].dt.date
    daily_df = df.groupby(["city","date"]).agg({
        "temperature":"mean",
        "precipitation":"sum",
        "windspeed":"mean"
    }).reset_index()
    daily_df.rename(columns={"temperature":"avg_temp"}, inplace=True)
    return daily_df
if __name__ == "__main__":
    df = get_daily_weather("Nairobi")
    print(df.head())