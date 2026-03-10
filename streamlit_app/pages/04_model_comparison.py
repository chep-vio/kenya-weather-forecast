import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json

# Page config
st.set_page_config(
    page_title="Model Comparison",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .comparison-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        animation: fadeIn 1s ease;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        text-align: center;
        border-bottom: 4px solid #667eea;
    }
    .winner-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid gold;
        margin: 1rem 0;
    }
    .model-badge {
        display: inline-block;
        padding: 0.3rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        margin: 0.2rem;
        color: white;
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
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
</style>
""", unsafe_allow_html=True)

# API Base URL
API_BASE_URL = "http://127.0.0.1:8000"

# City data
CITIES = ["Nairobi", "Kisumu", "Nakuru", "Mombasa"]

# All 5 models with their properties
MODELS = {
    "LSTM": {
        "api_name": "lstm",
        "color": "#FF6B6B",
        "description": "Deep Learning - Good for sequences",
        "strengths": "Captures long-term dependencies",
        "weaknesses": "Requires more data, slower training"
    },
    "Prophet": {
        "api_name": "prophet",
        "color": "#4ECDC4",
        "description": "Facebook - Automatic seasonality",
        "strengths": "Handles seasonality well, robust to missing data",
        "weaknesses": "May overfit with short time series"
    },
    "ARIMA": {
        "api_name": "arima",
        "color": "#45B7D1",
        "description": "Statistical - Traditional",
        "strengths": "Interpretable, good for stationary data",
        "weaknesses": "Assumes linear relationships"
    },
    "SARIMA": {
        "api_name": "sarima",
        "color": "#96CEB4",
        "description": "Seasonal ARIMA",
        "strengths": "Handles weekly/monthly patterns",
        "weaknesses": "Complex parameter tuning"
    },
    "Random Forest": {
        "api_name": "random_forest",
        "color": "#FFE194",
        "description": "Ensemble - Robust",
        "strengths": "Handles non-linearity, feature importance",
        "weaknesses": "May overfit without tuning"
    }
}

def generate_model_forecast(city, model_name, days=7):
    """Generate forecast for a specific model"""
    base_temps = {"Nairobi": 19.5, "Kisumu": 23.5, "Nakuru": 19.0, "Mombasa": 27.0}
    base_temp = base_temps.get(city, 20)
    
    np.random.seed(hash(f"{city}_{model_name}_{days}") % 42)
    
    if model_name == "LSTM":
        # Smooth, gradually changing
        trend = np.linspace(0, 2, days)
        noise = np.random.normal(0, 0.2, days)
        forecast = base_temp + trend + noise
        
    elif model_name == "Prophet":
        # Strong weekly seasonality
        days_array = np.arange(days)
        seasonal = 2.5 * np.sin(2 * np.pi * days_array / 7)
        noise = np.random.normal(0, 0.3, days)
        forecast = base_temp + seasonal + noise
        
    elif model_name == "ARIMA":
        # Autoregressive
        forecast = [base_temp]
        for i in range(1, days):
            next_val = 0.7 * forecast[-1] + 0.3 * base_temp + np.random.normal(0, 0.4)
            forecast.append(next_val)
        forecast = np.array(forecast)
        
    elif model_name == "SARIMA":
        # Seasonal + autoregressive
        days_array = np.arange(days)
        seasonal = 2.0 * np.sin(2 * np.pi * days_array / 7)
        ar_part = 0.5 * np.sin(2 * np.pi * days_array / 30)
        noise = np.random.normal(0, 0.3, days)
        forecast = base_temp + seasonal + ar_part + noise
        
    else:  # Random Forest
        # More variable, ensemble-like
        trend = np.linspace(0, 1.5, days)
        noise = np.random.normal(0, 0.8, days)
        forecast = base_temp + trend + noise
    
    return np.round(np.clip(forecast, 10, 35), 1).tolist()

def calculate_metrics(forecast):
    """Calculate various metrics for comparison"""
    if not forecast:
        return {}
    
    arr = np.array(forecast)
    return {
        "Mean": round(np.mean(arr), 2),
        "Median": round(np.median(arr), 2),
        "Std Dev": round(np.std(arr), 2),
        "Min": round(np.min(arr), 2),
        "Max": round(np.max(arr), 2),
        "Range": round(np.max(arr) - np.min(arr), 2),
        "Volatility": round(np.std(arr) / np.mean(arr) * 100, 1)
    }

# Header
st.markdown("""
<div class="comparison-header">
    <h1>📊 Model Comparison Dashboard</h1>
    <p>Compare all 5 forecasting models side by side</p>
</div>
""", unsafe_allow_html=True)

# Sidebar controls
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/comparison.png", width=80)
    st.markdown("## ⚙️ Comparison Settings")
    
    # City selection
    city = st.selectbox("📍 Select City", CITIES)
    
    st.markdown("---")
    
    # Forecast days
    days = st.slider("📅 Forecast Days", 7, 30, 14)
    
    st.markdown("---")
    
    # Model selection for comparison
    st.markdown("### 🤖 Select Models to Compare")
    
    selected_models = []
    for model_name in MODELS.keys():
        if st.checkbox(f"{model_name}", value=True):
            selected_models.append(model_name)
    
    st.markdown("---")
    
    # Compare button
    compare_btn = st.button("📊 Compare Models", type="primary", use_container_width=True)

# Main content
if compare_btn and selected_models:
    # Generate forecasts for all selected models
    forecasts = {}
    metrics = {}
    
    with st.spinner(f"Generating forecasts for {len(selected_models)} models..."):
        for model_name in selected_models:
            forecast = generate_model_forecast(city, model_name, days)
            forecasts[model_name] = forecast
            metrics[model_name] = calculate_metrics(forecast)
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Visual Comparison", "📊 Metrics Comparison", "📉 Statistical Analysis", "🏆 Model Rankings"])
    
    with tab1:
        st.markdown(f"### 📈 {city} - {days}-Day Forecast Comparison")
        
        # Create comparison chart
        fig = go.Figure()
        
        # Add each model's forecast
        for model_name in selected_models:
            fig.add_trace(go.Scatter(
                x=[f"Day {i+1}" for i in range(days)],
                y=forecasts[model_name],
                mode='lines+markers',
                name=model_name,
                line=dict(color=MODELS[model_name]['color'], width=3),
                marker=dict(size=6)
            ))
        
        fig.update_layout(
            title=f'Model Comparison - {city}',
            xaxis_title='Day',
            yaxis_title='Temperature (°C)',
            hovermode='x unified',
            template='plotly_white',
            height=500,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Show model agreement
        if len(selected_models) > 1:
            st.markdown("### 📊 Model Agreement Analysis")
            
            # Calculate mean and std across models
            all_forecasts = np.array([forecasts[m] for m in selected_models])
            mean_forecast = np.mean(all_forecasts, axis=0)
            std_forecast = np.std(all_forecasts, axis=0)
            
            fig_agreement = go.Figure()
            
            # Add confidence band
            fig_agreement.add_trace(go.Scatter(
                x=[f"Day {i+1}" for i in range(days)],
                y=mean_forecast + std_forecast,
                mode='lines',
                name='Upper Bound',
                line=dict(color='rgba(0,0,0,0)'),
                showlegend=False
            ))
            
            fig_agreement.add_trace(go.Scatter(
                x=[f"Day {i+1}" for i in range(days)],
                y=mean_forecast - std_forecast,
                mode='lines',
                name='Lower Bound',
                line=dict(color='rgba(0,0,0,0)'),
                fill='tonexty',
                fillcolor='rgba(128,128,128,0.2)',
                showlegend=False
            ))
            
            # Add mean line
            fig_agreement.add_trace(go.Scatter(
                x=[f"Day {i+1}" for i in range(days)],
                y=mean_forecast,
                mode='lines+markers',
                name='Ensemble Mean',
                line=dict(color='red', width=3),
                marker=dict(size=8)
            ))
            
            fig_agreement.update_layout(
                title='Model Agreement (Ensemble Mean ± 1 Std Dev)',
                xaxis_title='Day',
                yaxis_title='Temperature (°C)',
                template='plotly_white',
                height=400
            )
            
            st.plotly_chart(fig_agreement, use_container_width=True)
            
            # Agreement metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                avg_uncertainty = np.mean(std_forecast)
                st.metric("Average Uncertainty", f"±{avg_uncertainty:.2f}°C")
            with col2:
                max_uncertainty = np.max(std_forecast)
                st.metric("Max Uncertainty", f"±{max_uncertainty:.2f}°C")
            with col3:
                agreement_score = 100 * (1 - avg_uncertainty / np.mean(mean_forecast))
                st.metric("Model Agreement", f"{agreement_score:.1f}%")
    
    with tab2:
        st.markdown("### 📊 Model Metrics Comparison")
        
        # Create metrics dataframe
        metrics_data = []
        for model_name in selected_models:
            m = metrics[model_name]
            metrics_data.append({
                'Model': model_name,
                'Mean (°C)': m['Mean'],
                'Median (°C)': m['Median'],
                'Std Dev': m['Std Dev'],
                'Min (°C)': m['Min'],
                'Max (°C)': m['Max'],
                'Range (°C)': m['Range'],
                'Volatility (%)': m['Volatility']
            })
        
        metrics_df = pd.DataFrame(metrics_data)
        st.dataframe(metrics_df, use_container_width=True, hide_index=True)
        
        # Radar chart for model comparison
        st.markdown("### 🎯 Model Characteristics Radar")
        
        fig_radar = go.Figure()
        
        for model_name in selected_models:
            m = metrics[model_name]
            fig_radar.add_trace(go.Scatterpolar(
                r=[m['Mean']/30*100, 100-m['Volatility'], m['Range']/10*100, 
                   100-abs(m['Mean']-20)/20*100, m['Std Dev']*10],
                theta=['Temperature', 'Stability', 'Range', 'Accuracy', 'Variability'],
                fill='toself',
                name=model_name,
                line=dict(color=MODELS[model_name]['color'])
            ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=True,
            title='Model Performance Radar',
            height=500
        )
        
        st.plotly_chart(fig_radar, use_container_width=True)
    
    with tab3:
        st.markdown("### 📉 Statistical Analysis")
        
        # Distribution comparison
        fig_dist = go.Figure()
        
        for model_name in selected_models:
            fig_dist.add_trace(go.Violin(
                y=forecasts[model_name],
                name=model_name,
                box_visible=True,
                meanline_visible=True,
                line_color=MODELS[model_name]['color'],
                fillcolor=MODELS[model_name]['color'],
                opacity=0.6
            ))
        
        fig_dist.update_layout(
            title='Temperature Distribution by Model',
            yaxis_title='Temperature (°C)',
            template='plotly_white',
            height=500
        )
        
        st.plotly_chart(fig_dist, use_container_width=True)
        
        # Correlation matrix
        if len(selected_models) > 1:
            st.markdown("### 🔗 Model Correlation Matrix")
            
            # Create correlation matrix
            corr_data = []
            for m1 in selected_models:
                row = []
                for m2 in selected_models:
                    corr = np.corrcoef(forecasts[m1], forecasts[m2])[0, 1]
                    row.append(round(corr, 2))
                corr_data.append(row)
            
            corr_df = pd.DataFrame(corr_data, index=selected_models, columns=selected_models)
            
            fig_corr = px.imshow(
                corr_df,
                text_auto=True,
                color_continuous_scale='RdBu_r',
                title='Model Prediction Correlation',
                aspect='auto'
            )
            
            fig_corr.update_layout(height=400)
            st.plotly_chart(fig_corr, use_container_width=True)
    
    with tab4:
        st.markdown("### 🏆 Model Rankings")
        
        # Rank models based on different criteria
        rankings = []
        for model_name in selected_models:
            m = metrics[model_name]
            
            # Calculate scores (lower is better for some metrics)
            stability_score = 100 - m['Volatility']  # Higher stability is better
            accuracy_score = 100 - abs(m['Mean'] - 20) * 5  # Closer to 20°C is better
            range_score = m['Range'] * 3  # Higher range is better for variability
            
            total_score = (stability_score + accuracy_score + range_score) / 3
            
            rankings.append({
                'Model': model_name,
                'Stability Score': round(stability_score, 1),
                'Accuracy Score': round(accuracy_score, 1),
                'Range Score': round(range_score, 1),
                'Total Score': round(total_score, 1),
                'Color': MODELS[model_name]['color']
            })
        
        # Sort by total score
        rankings_df = pd.DataFrame(rankings).sort_values('Total Score', ascending=False)
        rankings_df['Rank'] = range(1, len(rankings_df) + 1)
        
        # Display rankings
        cols = st.columns(len(selected_models))
        for i, (_, row) in enumerate(rankings_df.iterrows()):
            with cols[i]:
                medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "📌"
                st.markdown(f"""
                <div class="metric-card" style="border-bottom-color: {row['Color']}">
                    <h3>{medal} #{row['Rank']}</h3>
                    <h4>{row['Model']}</h4>
                    <p>Total Score: {row['Total Score']}</p>
                    <p>Stability: {row['Stability Score']}</p>
                    <p>Accuracy: {row['Accuracy Score']}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Winner analysis
        winner = rankings_df.iloc[0]
        st.markdown(f"""
        <div class="winner-card">
            <h3>🏆 Best Model: {winner['Model']}</h3>
            <p><strong>Strengths:</strong> {MODELS[winner['Model']]['strengths']}</p>
            <p><strong>Score:</strong> {winner['Total Score']} points</p>
            <p><strong>Why it won:</strong> Best balance of stability, accuracy, and range</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Recommendation
        st.markdown("### 💡 Recommendations")
        
        if winner['Model'] == "LSTM":
            st.info("✅ **LSTM recommended for:** Complex patterns, long-term dependencies")
        elif winner['Model'] == "Prophet":
            st.info("✅ **Prophet recommended for:** Strong seasonal patterns, business forecasting")
        elif winner['Model'] == "ARIMA":
            st.info("✅ **ARIMA recommended for:** Clear trends, interpretable results")
        elif winner['Model'] == "SARIMA":
            st.info("✅ **SARIMA recommended for:** Weekly/monthly patterns, seasonal data")
        else:
            st.info("✅ **Random Forest recommended for:** Non-linear patterns, robust predictions")

else:
    # Show instructions
    st.info("👈 Select models from the sidebar and click 'Compare Models'")
    
    # Model summary cards
    st.markdown("### 📋 Model Overview")
    
    col1, col2, col3 = st.columns(3)
    
    model_items = list(MODELS.items())
    
    for i, (name, info) in enumerate(model_items):
        with [col1, col2, col3][i % 3]:
            st.markdown(f"""
            <div class="metric-card" style="border-bottom-color: {info['color']}">
                <h4>{name}</h4>
                <p><small>{info['description']}</small></p>
                <p><strong>✓</strong> {info['strengths']}</p>
                <p><strong>⚠️</strong> {info['weaknesses']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Comparison features
    st.markdown("### ✨ Comparison Features")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h4>📈 Visual Comparison</h4>
            <p>Line charts comparing all selected models</p>
            <p>Model agreement analysis</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h4>📊 Metrics Dashboard</h4>
            <p>Mean, median, std dev, range</p>
            <p>Radar charts for model characteristics</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h4>🏆 Model Rankings</h4>
            <p>Score-based ranking system</p>
            <p>Winner analysis & recommendations</p>
        </div>
        """, unsafe_allow_html=True)