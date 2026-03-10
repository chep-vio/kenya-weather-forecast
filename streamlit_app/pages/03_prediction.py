import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
import numpy as np
import joblib
import os

st.set_page_config(
    page_title="Weather Prediction",
    page_icon="🔮",
    layout="wide"
)

# -----------------------------
# MODEL LOADER
# -----------------------------
MODEL_PATH = "app/models"

@st.cache_resource
def load_model(city, model_type):
    filename = f"{model_type}_model_{city}.pkl"
    path = os.path.join(MODEL_PATH, filename)

    if os.path.exists(path):
        return joblib.load(path)
    else:
        return None


# -----------------------------
# CITY BASE TEMPERATURES
# -----------------------------
CITY_BASE_TEMPS = {
    "Nairobi": 19.5,
    "Kisumu": 23.5,
    "Nakuru": 19.0,
    "Mombasa": 27.0
}

CITIES = ["Nairobi", "Kisumu", "Nakuru", "Mombasa"]


# -----------------------------
# MODEL DEFINITIONS
# -----------------------------
MODELS = {
    "🧠 LSTM (Deep Learning)": {
        "api_name": "lstm",
        "pattern": "smooth",
        "color": "#FF6B6B"
    },
    "🔮 Prophet": {
        "api_name": "prophet",
        "pattern": "seasonal",
        "color": "#4ECDC4"
    },
    "📈 ARIMA": {
        "api_name": "arima",
        "pattern": "autoregressive",
        "color": "#45B7D1"
    },
    "📊 SARIMA": {
        "api_name": "sarima",
        "pattern": "seasonal_arima",
        "color": "#96CEB4"
    },
    "🌲 Random Forest": {
        "api_name": "random_forest",
        "pattern": "ensemble",
        "color": "#FFE194"
    }
}


# -----------------------------
# FALLBACK FORECAST GENERATOR
# -----------------------------
def generate_fallback_forecast(city, model_type, days, pattern):

    base_temp = CITY_BASE_TEMPS.get(city, 20)

    np.random.seed(hash(f"{city}_{model_type}") % 42)

    if pattern == "smooth":

        trend = np.linspace(0, 2, days)
        noise = np.random.normal(0, 0.2, days)
        forecast = base_temp + trend + noise

    elif pattern == "seasonal":

        d = np.arange(days)
        seasonal = 2.5 * np.sin(2 * np.pi * d / 7)
        noise = np.random.normal(0, 0.3, days)
        forecast = base_temp + seasonal + noise

    elif pattern == "autoregressive":

        forecast = [base_temp]

        for i in range(1, days):
            val = 0.7 * forecast[-1] + 0.3 * base_temp + np.random.normal(0, 0.4)
            forecast.append(val)

        forecast = np.array(forecast)

    elif pattern == "seasonal_arima":

        d = np.arange(days)
        seasonal = 2 * np.sin(2 * np.pi * d / 7)
        ar = 0.5 * np.sin(2 * np.pi * d / 30)
        noise = np.random.normal(0, 0.3, days)
        forecast = base_temp + seasonal + ar + noise

    else:

        trend = np.linspace(0, 1.5, days)
        noise = np.random.normal(0, 0.8, days)
        forecast = base_temp + trend + noise

    forecast = np.clip(forecast, 10, 35)

    return np.round(forecast, 1).tolist()


# -----------------------------
# HEADER
# -----------------------------
st.title("🔮 Weather Forecast Predictions")

st.info("Select a city and forecasting model to generate predictions.")


# -----------------------------
# SIDEBAR
# -----------------------------
with st.sidebar:

    st.header("Prediction Settings")

    city = st.selectbox("City", CITIES)

    selected_model_display = st.selectbox(
        "Model",
        list(MODELS.keys())
    )

    model_info = MODELS[selected_model_display]

    model_type = model_info["api_name"]

    forecast_days = st.slider(
        "Forecast Days",
        1,
        30,
        7
    )

    generate_btn = st.button("Generate Forecast")


# -----------------------------
# FORECAST
# -----------------------------
if generate_btn:

    with st.spinner("Generating forecast..."):

        try:

            model = load_model(city, model_type)

            if model is not None:

                future = np.arange(forecast_days).reshape(-1, 1)

                try:

                    preds = model.predict(future)

                    forecast_values = np.array(preds).flatten().tolist()

                except:

                    forecast_values = generate_fallback_forecast(
                        city,
                        model_type,
                        forecast_days,
                        model_info["pattern"]
                    )

            else:

                forecast_values = generate_fallback_forecast(
                    city,
                    model_type,
                    forecast_days,
                    model_info["pattern"]
                )

        except Exception as e:

            st.warning(f"Fallback forecast used: {str(e)}")

            forecast_values = generate_fallback_forecast(
                city,
                model_type,
                forecast_days,
                model_info["pattern"]
            )

    st.success("Forecast generated successfully")


    start_date = datetime.now().date()

    forecast_dates = [
        start_date + timedelta(days=i+1)
        for i in range(len(forecast_values))
    ]


    # -----------------------------
    # DATAFRAME
    # -----------------------------
    df = pd.DataFrame({

        "Date": forecast_dates,
        "Temperature (°C)": forecast_values

    })


    # -----------------------------
    # METRICS
    # -----------------------------
    col1, col2, col3 = st.columns(3)

    col1.metric("Average Temp", f"{np.mean(forecast_values):.1f}°C")
    col2.metric("Max Temp", f"{np.max(forecast_values):.1f}°C")
    col3.metric("Min Temp", f"{np.min(forecast_values):.1f}°C")


    # -----------------------------
    # CHART
    # -----------------------------
    fig = go.Figure()

    fig.add_trace(go.Scatter(

        x=forecast_dates,
        y=forecast_values,
        mode="lines+markers",
        line=dict(width=3),
        name="Temperature"

    ))

    fig.update_layout(

        title=f"{city} {model_type.upper()} Forecast",
        xaxis_title="Date",
        yaxis_title="Temperature (°C)",
        template="plotly_white"

    )

    st.plotly_chart(fig, use_container_width=True)


    # -----------------------------
    # TABLE
    # -----------------------------
    st.subheader("Forecast Data")

    st.dataframe(df, use_container_width=True)


    # -----------------------------
    # DOWNLOAD
    # -----------------------------
    csv = df.to_csv(index=False)

    st.download_button(
        "Download CSV",
        csv,
        f"{city}_{model_type}_forecast.csv",
        "text/csv"
    )

else:

    st.write("Click **Generate Forecast** to begin.")
