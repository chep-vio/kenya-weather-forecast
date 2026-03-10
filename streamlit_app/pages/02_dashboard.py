import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import date, timedelta, datetime

# Page configuration
st.set_page_config(
    page_title="Kenya Weather Dashboard",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .kpi-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        text-align: center;
        transition: transform 0.3s ease;
    }
    .kpi-card:hover {
        transform: translateY(-5px);
    }
    .kpi-value {
        font-size: 2.2rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .kpi-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    .chart-container {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    .metric-highlight {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        border-left: 4px solid #1E88E5;
        margin: 0.5rem 0;
        transition: transform 0.2s ease;
    }
    .metric-highlight:hover {
        transform: translateX(5px);
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .date-filter {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        border: 1px solid rgba(255,255,255,0.3);
    }
    .info-box {
        background-color: #e3f2fd;
        border-left: 5px solid #2196F3;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 4px 4px 0px 0px;
        padding: 10px 20px;
        background-color: #f0f2f6;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1E88E5;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# City coordinates and portfolios
CITY_DATA = {
    "Nairobi": {"lat": -1.286389, "lon": 36.817223, "portfolio": "Urban_Microloans"},
    "Kisumu": {"lat": -0.091702, "lon": 34.767956, "portfolio": "Lake_Region_Agri"},
    "Nakuru": {"lat": -0.303099, "lon": 36.080025, "portfolio": "High_Potential_Farming"},
    "Mombasa": {"lat": -4.043477, "lon": 39.668206, "portfolio": "Coastal_Trade"}
}

# API Base URL
API_BASE_URL = "http://127.0.0.1:8000"

# Function to fetch weather data using your exact code
def fetch_weather_data_direct(city):
    """Fetch weather data directly using the provided function"""
    try:
        city_info = CITY_DATA[city]
        lat = city_info["lat"]
        lon = city_info["lon"]
        
        # Using your exact fetch function logic
        today = date.today()
        start = today - timedelta(days=730)
        
        url = "https://archive-api.open-meteo.com/v1/archive"
        
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start.strftime("%Y-%m-%d"),
            "end_date": today.strftime("%Y-%m-%d"),
            "hourly": "temperature_2m,precipitation,windspeed_10m",
            "timezone": "Africa/Nairobi"
        }
        
        with st.spinner(f"Fetching live weather data for {city}..."):
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
        # Process the data
        rows = []
        hourly = data["hourly"]
        
        for i in range(len(hourly["time"])):
            rows.append({
                "city": city,
                "portfolio": city_info["portfolio"],
                "latitude": lat,
                "longitude": lon,
                "timestamp": hourly["time"][i],
                "temperature": hourly["temperature_2m"][i],
                "precipitation": hourly["precipitation"][i],
                "windspeed": hourly["windspeed_10m"][i]
            })
        
        df = pd.DataFrame(rows)
        
        # Process timestamps
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["date"] = df["timestamp"].dt.date
        df["hour"] = df["timestamp"].dt.hour
        
        # Aggregate to daily
        daily_df = df.groupby(["city", "portfolio", "date"]).agg({
            "temperature": ["mean", "max", "min"],
            "precipitation": "sum",
            "windspeed": "mean"
        }).reset_index()
        
        daily_df.columns = [
            "city", "portfolio", "date",
            "avg_temp", "max_temp", "min_temp",
            "total_precipitation", "avg_windspeed"
        ]
        
        daily_df["date"] = pd.to_datetime(daily_df["date"])
        daily_df = daily_df.sort_values("date")
        
        return daily_df
        
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return None

# Function to fetch from API (fallback)
@st.cache_data(ttl=300)
def fetch_weather_data_api(city):
    """Fetch weather data from FastAPI"""
    try:
        url = f"{API_BASE_URL}/weather/{city}"
        resp = requests.get(url)
        if resp.status_code == 200:
            data = pd.DataFrame(resp.json())
            data['date'] = pd.to_datetime(data['date'])
            return data
        else:
            return None
    except:
        return None

# Header
st.markdown('<h1 class="main-header">🌦️ Kenya Weather Dashboard</h1>', unsafe_allow_html=True)

# Sidebar for controls
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/weather.png", width=80)
    st.markdown("## 🎛️ Dashboard Controls")
    
    # City selection
    city = st.selectbox(
        "📍 Select City",
        list(CITY_DATA.keys()),
        index=0,
        help="Select a city to view weather data"
    )
    
    st.markdown("---")
    
    # Data source selection
    st.markdown("### 🔌 Data Source")
    data_source = st.radio(
        "Choose data source:",
        ["Live API (Open-Meteo)", "FastAPI Backend"],
        index=0,
        help="Live API fetches directly from Open-Meteo. FastAPI uses your backend."
    )
    
    st.markdown("---")
    
    # Fetch data based on selection
    if data_source == "Live API (Open-Meteo)":
        with st.spinner(f"Fetching live data for {city}..."):
            data = fetch_weather_data_direct(city)
    else:
        data = fetch_weather_data_api(city)
    
    if data is not None and len(data) > 0:
        # Get actual data date range
        min_date = data['date'].min().date()
        max_date = data['date'].max().date()
        today = date.today()
        
        st.markdown("### 📅 Date Range Filter")
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.1); padding: 0.5rem; border-radius: 5px; margin-bottom: 1rem;">
            <small>📊 Data available: <br>
            <strong>{min_date.strftime('%b %d, %Y')} to {max_date.strftime('%b %d, %Y')}</strong></small>
        </div>
        """, unsafe_allow_html=True)
        
        # Date range selection
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=min_date,
                min_value=min_date,
                max_value=max_date
            )
        with col2:
            end_date = st.date_input(
                "End Date",
                value=max_date,
                min_value=min_date,
                max_value=max_date
            )
        
        # Validate date range
        if start_date > end_date:
            st.error("❌ End date must be after start date")
            st.stop()
        
        st.markdown("---")
        
        # Quick filters
        st.markdown("### ⚡ Quick Filters")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📅 Last 30 Days"):
                start_date = max_date - timedelta(days=30)
                if start_date < min_date:
                    start_date = min_date
                st.rerun()
        
        with col2:
            if st.button("📅 Last 90 Days"):
                start_date = max_date - timedelta(days=90)
                if start_date < min_date:
                    start_date = min_date
                st.rerun()
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📅 This Year"):
                start_date = date(max_date.year, 1, 1)
                if start_date < min_date:
                    start_date = min_date
                st.rerun()
        
        with col2:
            if st.button("📅 All Data"):
                start_date = min_date
                end_date = max_date
                st.rerun()
        
        st.markdown("---")
        
        # Chart preferences
        st.markdown("### 📊 Chart Preferences")
        
        chart_theme = st.selectbox(
            "Color Theme",
            ["plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn"],
            index=0
        )
        
        show_grid = st.checkbox("Show Grid", value=True)
        
        st.markdown("---")
        
        # Quick stats
        total_days = (end_date - start_date).days + 1
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea20 0%, #764ba220 100%); padding: 1rem; border-radius: 10px;">
            <h4 style="margin:0 0 0.5rem 0;">ℹ️ Selection Summary</h4>
            <p style="margin:0; font-size:0.9rem;">
            <strong>City:</strong> {city}<br>
            <strong>Portfolio:</strong> {CITY_DATA[city]['portfolio']}<br>
            <strong>Period:</strong> {total_days} days<br>
            <strong>Range:</strong> {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Refresh button
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()
    else:
        st.error("❌ Unable to load data. Please check your connection.")
        st.stop()

# Main content area
if data is not None and len(data) > 0:
    # Filter data based on date range
    mask = (data['date'].dt.date >= start_date) & (data['date'].dt.date <= end_date)
    filtered_data = data.loc[mask].copy()
    
    if len(filtered_data) > 0:
        # Create tabs for better organization
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🌡️ Temperature", "💧 Precipitation & Wind", "📈 Analysis"])
        
        with tab1:  # Overview Tab
            # Date filter summary
            st.markdown(f"""
            <div class="date-filter">
                <h4 style="margin:0; color:#1E88E5;">📊 Dashboard Overview - {city}</h4>
                <p style="margin:0.5rem 0 0 0; color:#666;">
                    <strong>Portfolio:</strong> {CITY_DATA[city]['portfolio']} | 
                    <strong>Coordinates:</strong> {CITY_DATA[city]['lat']:.4f}, {CITY_DATA[city]['lon']:.4f} | 
                    <strong>Period:</strong> {start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')} ({len(filtered_data)} days)
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # KPIs Section
            st.markdown("## 📊 Key Performance Indicators")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                avg_temp = filtered_data['avg_temp'].mean()
                min_temp = filtered_data['min_temp'].min()
                max_temp = filtered_data['max_temp'].max()
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">🌡️ Average Temperature</div>
                    <div class="kpi-value">{avg_temp:.1f}°C</div>
                    <div class="kpi-label">Range: {min_temp:.1f}°C - {max_temp:.1f}°C</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                total_precip = filtered_data['total_precipitation'].sum()
                avg_daily_precip = total_precip / len(filtered_data) if len(filtered_data) > 0 else 0
                max_precip = filtered_data['total_precipitation'].max()
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">💧 Total Precipitation</div>
                    <div class="kpi-value">{total_precip:.1f} mm</div>
                    <div class="kpi-label">Avg: {avg_daily_precip:.2f} mm | Max: {max_precip:.1f} mm</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                avg_wind = filtered_data['avg_windspeed'].mean()
                max_wind = filtered_data['avg_windspeed'].max()
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">🌬️ Average Windspeed</div>
                    <div class="kpi-value">{avg_wind:.1f} km/h</div>
                    <div class="kpi-label">Max: {max_wind:.1f} km/h</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                temp_volatility = filtered_data['avg_temp'].std()
                temp_range = filtered_data['max_temp'].max() - filtered_data['min_temp'].min()
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">📊 Temperature Variation</div>
                    <div class="kpi-value">±{temp_volatility:.2f}°C</div>
                    <div class="kpi-label">Range: {temp_range:.1f}°C</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Quick stats cards
            st.markdown("## ⚡ Extreme Events")
            col1, col2 = st.columns(2)
            
            with col1:
                # Hottest day
                hottest = filtered_data.loc[filtered_data['max_temp'].idxmax()]
                st.markdown(f"""
                <div class="metric-highlight">
                    <strong>🔥 Hottest Day:</strong> {hottest['date'].strftime('%B %d, %Y')}<br>
                    <strong>Max Temperature:</strong> {hottest['max_temp']:.1f}°C
                </div>
                """, unsafe_allow_html=True)
                
                # Coldest day
                coldest = filtered_data.loc[filtered_data['min_temp'].idxmin()]
                st.markdown(f"""
                <div class="metric-highlight">
                    <strong>❄️ Coldest Day:</strong> {coldest['date'].strftime('%B %d, %Y')}<br>
                    <strong>Min Temperature:</strong> {coldest['min_temp']:.1f}°C
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Wettest day
                wettest = filtered_data.loc[filtered_data['total_precipitation'].idxmax()]
                st.markdown(f"""
                <div class="metric-highlight">
                    <strong>🌧️ Wettest Day:</strong> {wettest['date'].strftime('%B %d, %Y')}<br>
                    <strong>Precipitation:</strong> {wettest['total_precipitation']:.1f} mm
                </div>
                """, unsafe_allow_html=True)
                
                # Windiest day
                windiest = filtered_data.loc[filtered_data['avg_windspeed'].idxmax()]
                st.markdown(f"""
                <div class="metric-highlight">
                    <strong>💨 Windiest Day:</strong> {windiest['date'].strftime('%B %d, %Y')}<br>
                    <strong>Wind Speed:</strong> {windiest['avg_windspeed']:.1f} km/h
                </div>
                """, unsafe_allow_html=True)
            
            # Multi-panel overview chart
            st.markdown("## 📈 Weather Variables Overview")
            
            fig_overview = make_subplots(
                rows=3, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.08,
                subplot_titles=('Temperature (°C)', 'Precipitation (mm)', 'Wind Speed (km/h)')
            )
            
            # Temperature subplot
            fig_overview.add_trace(
                go.Scatter(x=filtered_data['date'], y=filtered_data['avg_temp'],
                          mode='lines', name='Temperature', line=dict(color='#FF5722', width=2)),
                row=1, col=1
            )
            
            # Precipitation subplot
            fig_overview.add_trace(
                go.Bar(x=filtered_data['date'], y=filtered_data['total_precipitation'],
                      name='Precipitation', marker_color='#4CAF50', opacity=0.7),
                row=2, col=1
            )
            
            # Wind speed subplot
            fig_overview.add_trace(
                go.Scatter(x=filtered_data['date'], y=filtered_data['avg_windspeed'],
                          mode='lines', name='Wind Speed', line=dict(color='#2196F3', width=2)),
                row=3, col=1
            )
            
            fig_overview.update_layout(
                height=600,
                showlegend=False,
                template=chart_theme,
                title_text=f"Weather Overview - {city}"
            )
            
            fig_overview.update_yaxes(title_text="°C", row=1, col=1)
            fig_overview.update_yaxes(title_text="mm", row=2, col=1)
            fig_overview.update_yaxes(title_text="km/h", row=3, col=1)
            
            if show_grid:
                fig_overview.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
                fig_overview.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
            
            st.plotly_chart(fig_overview, use_container_width=True)
        
        with tab2:  # Temperature Tab
            st.markdown(f"## 🌡️ Temperature Analysis - {city}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Temperature line chart
                fig_temp = go.Figure()
                
                fig_temp.add_trace(go.Scatter(
                    x=filtered_data['date'],
                    y=filtered_data['avg_temp'],
                    mode='lines',
                    name='Average Temperature',
                    line=dict(color='#1E88E5', width=2),
                    hovertemplate='Date: %{x|%Y-%m-%d}<br>Avg Temp: %{y:.1f}°C<extra></extra>'
                ))
                
                fig_temp.add_trace(go.Scatter(
                    x=filtered_data['date'],
                    y=filtered_data['max_temp'],
                    mode='lines',
                    name='Max Temperature',
                    line=dict(color='#FF5722', width=1.5, dash='dash'),
                    hovertemplate='Date: %{x|%Y-%m-%d}<br>Max Temp: %{y:.1f}°C<extra></extra>'
                ))
                
                fig_temp.add_trace(go.Scatter(
                    x=filtered_data['date'],
                    y=filtered_data['min_temp'],
                    mode='lines',
                    name='Min Temperature',
                    line=dict(color='#2196F3', width=1.5, dash='dash'),
                    hovertemplate='Date: %{x|%Y-%m-%d}<br>Min Temp: %{y:.1f}°C<extra></extra>'
                ))
                
                fig_temp.update_layout(
                    title=f'Temperature Trends',
                    xaxis_title='Date',
                    yaxis_title='Temperature (°C)',
                    hovermode='x unified',
                    template=chart_theme,
                    showlegend=True,
                    height=400
                )
                
                if show_grid:
                    fig_temp.update_xaxes(showgrid=True, gridcolor='LightGray')
                    fig_temp.update_yaxes(showgrid=True, gridcolor='LightGray')
                
                st.plotly_chart(fig_temp, use_container_width=True)
            
            with col2:
                # Temperature distribution
                fig_hist = go.Figure()
                
                fig_hist.add_trace(go.Histogram(
                    x=filtered_data['avg_temp'],
                    nbinsx=20,
                    name='Temperature Distribution',
                    marker_color='#1E88E5',
                    opacity=0.7,
                    hovertemplate='Temp: %{x:.1f}°C<br>Frequency: %{y} days<extra></extra>'
                ))
                
                fig_hist.update_layout(
                    title=f'Temperature Distribution',
                    xaxis_title='Temperature (°C)',
                    yaxis_title='Frequency (Days)',
                    template=chart_theme,
                    height=400,
                    showlegend=False,
                    bargap=0.1
                )
                
                # Add mean line
                fig_hist.add_vline(x=avg_temp, line_dash="dash", line_color="red",
                                  annotation_text=f"Mean: {avg_temp:.1f}°C")
                
                st.plotly_chart(fig_hist, use_container_width=True)
            
            # Temperature range chart
            fig_range = go.Figure()
            
            fig_range.add_trace(go.Scatter(
                x=filtered_data['date'],
                y=filtered_data['max_temp'],
                mode='lines',
                name='Max Temperature',
                line=dict(color='#FF5722', width=1),
                showlegend=True
            ))
            
            fig_range.add_trace(go.Scatter(
                x=filtered_data['date'],
                y=filtered_data['min_temp'],
                mode='lines',
                name='Min Temperature',
                line=dict(color='#2196F3', width=1),
                fill='tonexty',
                fillcolor='rgba(33, 150, 243, 0.2)',
                showlegend=True
            ))
            
            fig_range.update_layout(
                title='Temperature Range (Max-Min)',
                xaxis_title='Date',
                yaxis_title='Temperature (°C)',
                template=chart_theme,
                height=400
            )
            
            st.plotly_chart(fig_range, use_container_width=True)
        
        with tab3:  # Precipitation & Wind Tab
            st.markdown(f"## 💧 Precipitation & Wind Analysis - {city}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Precipitation chart
                fig_precip = go.Figure()
                
                fig_precip.add_trace(go.Bar(
                    x=filtered_data['date'],
                    y=filtered_data['total_precipitation'],
                    name='Precipitation',
                    marker_color='#4CAF50',
                    opacity=0.7,
                    hovertemplate='Date: %{x|%Y-%m-%d}<br>Precipitation: %{y:.1f} mm<extra></extra>'
                ))
                
                # Add moving average if enough data
                if len(filtered_data) >= 7:
                    filtered_data['precip_ma7'] = filtered_data['total_precipitation'].rolling(7, min_periods=1).mean()
                    fig_precip.add_trace(go.Scatter(
                        x=filtered_data['date'],
                        y=filtered_data['precip_ma7'],
                        mode='lines',
                        name='7-Day Moving Avg',
                        line=dict(color='#FF9800', width=2),
                        hovertemplate='Date: %{x|%Y-%m-%d}<br>7-Day Avg: %{y:.1f} mm<extra></extra>'
                    ))
                
                fig_precip.update_layout(
                    title=f'Daily Precipitation',
                    xaxis_title='Date',
                    yaxis_title='Precipitation (mm)',
                    hovermode='x unified',
                    template=chart_theme,
                    height=400,
                    showlegend=True
                )
                
                st.plotly_chart(fig_precip, use_container_width=True)
            
            with col2:
                # Wind speed chart
                fig_wind = go.Figure()
                
                fig_wind.add_trace(go.Scatter(
                    x=filtered_data['date'],
                    y=filtered_data['avg_windspeed'],
                    mode='lines+markers',
                    name='Wind Speed',
                    line=dict(color='#9C27B0', width=2),
                    marker=dict(size=4),
                    hovertemplate='Date: %{x|%Y-%m-%d}<br>Wind Speed: %{y:.1f} km/h<extra></extra>'
                ))
                
                # Add reference line for average
                fig_wind.add_hline(y=avg_wind, line_dash="dash", line_color="gray",
                                  annotation_text=f"Avg: {avg_wind:.1f} km/h")
                
                fig_wind.update_layout(
                    title=f'Wind Speed Patterns',
                    xaxis_title='Date',
                    yaxis_title='Wind Speed (km/h)',
                    hovermode='x unified',
                    template=chart_theme,
                    height=400
                )
                
                st.plotly_chart(fig_wind, use_container_width=True)
            
            # Precipitation accumulation chart
            filtered_data['cumulative_precip'] = filtered_data['total_precipitation'].cumsum()
            
            fig_cumulative = go.Figure()
            
            fig_cumulative.add_trace(go.Scatter(
                x=filtered_data['date'],
                y=filtered_data['cumulative_precip'],
                mode='lines',
                name='Cumulative Precipitation',
                line=dict(color='#4CAF50', width=3),
                fill='tozeroy',
                fillcolor='rgba(76, 175, 80, 0.2)'
            ))
            
            fig_cumulative.update_layout(
                title='Cumulative Precipitation Over Time',
                xaxis_title='Date',
                yaxis_title='Cumulative Precipitation (mm)',
                template=chart_theme,
                height=400
            )
            
            st.plotly_chart(fig_cumulative, use_container_width=True)
        
        with tab4:  # Analysis Tab
            st.markdown(f"## 📈 Statistical Analysis - {city}")
            
            # Summary statistics
            st.markdown("### 📊 Summary Statistics")
            
            stats_df = pd.DataFrame({
                'Metric': ['Mean', 'Median', 'Std Dev', 'Min', 'Max', 'Range'],
                'Temperature (°C)': [
                    f"{filtered_data['avg_temp'].mean():.2f}",
                    f"{filtered_data['avg_temp'].median():.2f}",
                    f"{filtered_data['avg_temp'].std():.2f}",
                    f"{filtered_data['avg_temp'].min():.2f}",
                    f"{filtered_data['avg_temp'].max():.2f}",
                    f"{filtered_data['avg_temp'].max() - filtered_data['avg_temp'].min():.2f}"
                ],
                'Precipitation (mm)': [
                    f"{filtered_data['total_precipitation'].mean():.2f}",
                    f"{filtered_data['total_precipitation'].median():.2f}",
                    f"{filtered_data['total_precipitation'].std():.2f}",
                    f"{filtered_data['total_precipitation'].min():.2f}",
                    f"{filtered_data['total_precipitation'].max():.2f}",
                    f"{filtered_data['total_precipitation'].max() - filtered_data['total_precipitation'].min():.2f}"
                ],
                'Wind Speed (km/h)': [
                    f"{filtered_data['avg_windspeed'].mean():.2f}",
                    f"{filtered_data['avg_windspeed'].median():.2f}",
                    f"{filtered_data['avg_windspeed'].std():.2f}",
                    f"{filtered_data['avg_windspeed'].min():.2f}",
                    f"{filtered_data['avg_windspeed'].max():.2f}",
                    f"{filtered_data['avg_windspeed'].max() - filtered_data['avg_windspeed'].min():.2f}"
                ]
            })
            
            st.dataframe(stats_df, use_container_width=True, hide_index=True)
            
            # Correlation heatmap
            st.markdown("### 🔗 Correlation Matrix")
            
            corr_data = filtered_data[['avg_temp', 'total_precipitation', 'avg_windspeed']].corr()
            
            fig_corr = px.imshow(
                corr_data,
                text_auto=True,
                color_continuous_scale='RdBu_r',
                title='Correlation between Weather Variables',
                aspect='auto'
            )
            
            fig_corr.update_layout(height=400)
            st.plotly_chart(fig_corr, use_container_width=True)
            
            # Monthly patterns (if enough data)
            if len(filtered_data) >= 30:
                st.markdown("### 📅 Monthly Patterns")
                
                filtered_data['month'] = filtered_data['date'].dt.month
                filtered_data['month_name'] = filtered_data['date'].dt.strftime('%B')
                
                monthly_avg = filtered_data.groupby('month_name').agg({
                    'avg_temp': 'mean',
                    'total_precipitation': 'mean',
                    'avg_windspeed': 'mean'
                }).round(2)
                
                # Sort by month
                month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                              'July', 'August', 'September', 'October', 'November', 'December']
                monthly_avg = monthly_avg.reindex(month_order)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_monthly_temp = px.line(
                        x=monthly_avg.index,
                        y=monthly_avg['avg_temp'],
                        title='Monthly Average Temperature',
                        labels={'x': 'Month', 'y': 'Temperature (°C)'},
                        template=chart_theme
                    )
                    fig_monthly_temp.update_traces(line=dict(color='#1E88E5', width=3))
                    st.plotly_chart(fig_monthly_temp, use_container_width=True)
                
                with col2:
                    fig_monthly_precip = px.bar(
                        x=monthly_avg.index,
                        y=monthly_avg['total_precipitation'],
                        title='Monthly Average Precipitation',
                        labels={'x': 'Month', 'y': 'Precipitation (mm)'},
                        template=chart_theme,
                        color_discrete_sequence=['#4CAF50']
                    )
                    st.plotly_chart(fig_monthly_precip, use_container_width=True)
        
        # Raw data section at the bottom
        with st.expander("📋 View Raw Data"):
            st.dataframe(filtered_data, use_container_width=True)
            
            # Download button
            csv = filtered_data.to_csv(index=False)
            st.download_button(
                label="📥 Download Data as CSV",
                data=csv,
                file_name=f"{city}_weather_data_{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    else:
        st.warning(f"""
        ⚠️ No data available for the selected date range ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}).
        
        Available data ranges from {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}.
        Please adjust your date selection.
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📅 Use Available Date Range"):
                start_date = min_date
                end_date = max_date
                st.rerun()
        with col2:
            if st.button("📊 Show All Data"):
                start_date = min_date
                end_date = max_date
                st.rerun()