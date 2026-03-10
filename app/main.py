from fastapi import FastAPI, Query
from app.data_processing import get_daily_weather
from app.models import predict_temperature

app = FastAPI(title="Kenya Weather Forecast API")

@app.get("/")
def home():
    return {"message": "Welcome to Kenya Weather Forecast API"}

@app.get("/weather/{city}")
def weather(city: str):
    """Fetch daily aggregated weather for a city"""
    df = get_daily_weather(city)
    return df.to_dict(orient="records")

@app.get("/forecast/{city}")
def forecast(
    city: str, 
    model_type: str = Query("lstm", description="Model type: lstm, prophet, arima, sarima, random_forest"),
    days: int = Query(7, description="Number of days to forecast", ge=1, le=30)
):
    """Return temperature forecast for a city using selected model"""
    forecast_data = predict_temperature(city, model_type, days)
    return forecast_data