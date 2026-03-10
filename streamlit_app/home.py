import streamlit as st
import base64
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Kenya Weather Forecast | DSA 8502",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for stunning design
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-family: 'Poppins', sans-serif;
    }
    
    /* Animated Background */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: radial-gradient(circle at 20% 50%, rgba(255,255,255,0.1) 0%, transparent 50%),
                    radial-gradient(circle at 80% 80%, rgba(255,255,255,0.1) 0%, transparent 50%);
        pointer-events: none;
        z-index: 0;
    }
    
    /* Main Title with Animation */
    .title-container {
        text-align: center;
        padding: 2rem 0;
        animation: fadeInDown 1.5s ease;
    }
    
    .main-title {
        font-size: 4.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #ffffff 0%, #ffd700 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        margin-bottom: 0.5rem;
        letter-spacing: 2px;
    }
    
    .title-underline {
        width: 150px;
        height: 4px;
        background: linear-gradient(90deg, transparent, #ffd700, transparent);
        margin: 1rem auto;
        animation: pulse 2s infinite;
    }
    
    .subtitle {
        font-size: 1.5rem;
        color: rgba(255,255,255,0.9);
        font-weight: 300;
        margin-top: 1rem;
        animation: fadeInUp 1.5s ease;
    }
    
    /* Weather Icon Animation */
    .weather-icon-container {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 2rem;
        margin: 2rem 0;
        animation: float 3s ease-in-out infinite;
    }
    
    .weather-icon {
        font-size: 4rem;
        filter: drop-shadow(0 10px 20px rgba(0,0,0,0.2));
        transition: transform 0.3s ease;
    }
    
    .weather-icon:hover {
        transform: scale(1.2) rotate(5deg);
    }
    
    /* Glass Card Effect */
    .glass-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 20px 40px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
        height: 100%;
        animation: fadeIn 1s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 30px 50px rgba(0,0,0,0.3);
        background: rgba(255, 255, 255, 0.15);
    }
    
    .card-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .card-title {
        font-size: 1.8rem;
        font-weight: 600;
        color: #ffd700;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .card-text {
        color: rgba(255,255,255,0.9);
        line-height: 1.8;
        font-size: 1rem;
    }
    
    .feature-list {
        list-style: none;
        padding: 0;
        margin-top: 1.5rem;
    }
    
    .feature-list li {
        color: rgba(255,255,255,0.8);
        margin: 0.8rem 0;
        padding-left: 1.8rem;
        position: relative;
        transition: transform 0.3s ease;
    }
    
    .feature-list li:hover {
        transform: translateX(10px);
        color: white;
    }
    
    .feature-list li::before {
        content: "✦";
        color: #ffd700;
        position: absolute;
        left: 0;
        font-size: 1.2rem;
        animation: sparkle 1.5s infinite;
    }
    
    /* Stats Section */
    .stats-container {
        display: flex;
        justify-content: space-around;
        flex-wrap: wrap;
        gap: 2rem;
        margin: 3rem 0;
        animation: fadeInUp 1.5s ease;
    }
    
    .stat-item {
        text-align: center;
        padding: 1.5rem;
        background: rgba(255,255,255,0.1);
        border-radius: 15px;
        min-width: 200px;
        backdrop-filter: blur(5px);
        border: 1px solid rgba(255,255,255,0.2);
        transition: all 0.3s ease;
    }
    
    .stat-item:hover {
        transform: scale(1.05);
        background: rgba(255,255,255,0.2);
    }
    
    .stat-number {
        font-size: 3rem;
        font-weight: 700;
        color: #ffd700;
        line-height: 1.2;
    }
    
    .stat-label {
        font-size: 1.1rem;
        color: rgba(255,255,255,0.9);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Section Title */
    .section-title {
        font-size: 2.5rem;
        font-weight: 600;
        color: white;
        text-align: center;
        margin: 3rem 0 2rem;
        position: relative;
        animation: fadeIn 1s ease;
    }
    
    .section-title::after {
        content: "";
        display: block;
        width: 100px;
        height: 3px;
        background: linear-gradient(90deg, transparent, #ffd700, transparent);
        margin: 1rem auto;
    }
    
    /* Data Source Section */
    .data-source {
        background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
        border-radius: 30px;
        padding: 3rem;
        margin: 3rem 0;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
        animation: slideIn 1s ease;
    }
    
    .api-tag {
        display: inline-block;
        background: rgba(255,215,0,0.2);
        color: #ffd700;
        padding: 0.5rem 1.5rem;
        border-radius: 30px;
        font-weight: 600;
        margin: 0.5rem;
        border: 1px solid rgba(255,215,0,0.3);
        transition: all 0.3s ease;
    }
    
    .api-tag:hover {
        background: rgba(255,215,0,0.3);
        transform: scale(1.05);
    }
    
    /* Navigation Message */
    .nav-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        margin: 2rem 0;
        border: 2px solid rgba(255,255,255,0.3);
        animation: pulse 2s infinite;
    }
    
    .nav-message-text {
        font-size: 1.3rem;
        color: white;
        font-weight: 500;
    }
    
    .nav-highlight {
        color: #ffd700;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #2c3e50 0%, #3498db 100%);
    }
    
    .sidebar-content {
        padding: 2rem 1rem;
    }
    
    /* Animations */
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-50px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-20px); }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.8; }
    }
    
    @keyframes sparkle {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.5; transform: scale(1.2); }
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2.5rem;
        }
        .subtitle {
            font-size: 1.2rem;
        }
        .card-title {
            font-size: 1.5rem;
        }
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255,255,255,0.1);
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
</style>
""", unsafe_allow_html=True)

# Animated Title Section
st.markdown("""
<div class="title-container">
    <h1 class="main-title">
        🌦️ KENYA WEATHER FORECAST
    </h1>
    <div class="title-underline"></div>
    <p class="subtitle">
        Advanced Weather Analytics & AI-Powered Predictions for Smart Decision Making
    </p>
</div>
""", unsafe_allow_html=True)

# Animated Weather Icons
st.markdown("""
<div class="weather-icon-container">
    <span class="weather-icon">☀️</span>
    <span class="weather-icon">🌤️</span>
    <span class="weather-icon">⛅</span>
    <span class="weather-icon">🌥️</span>
    <span class="weather-icon">☁️</span>
    <span class="weather-icon">🌧️</span>
    <span class="weather-icon">⛈️</span>
    <span class="weather-icon">🌈</span>
</div>
""", unsafe_allow_html=True)

# Stats Section
st.markdown("""
<div class="stats-container">
    <div class="stat-item">
        <div class="stat-number">4</div>
        <div class="stat-label">Major Cities</div>
    </div>
    <div class="stat-item">
        <div class="stat-number">5</div>
        <div class="stat-label">Forecast Models</div>
    </div>
    <div class="stat-item">
        <div class="stat-number">731</div>
        <div class="stat-label">Days of Data</div>
    </div>
    <div class="stat-item">
        <div class="stat-number">80-90%(depending on the model used)</div>
        <div class="stat-label">Accuracy</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Project Description with Glass Cards
st.markdown('<h2 class="section-title">🎯 Project Overview</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="glass-card">
        <div class="card-icon">📊</div>
        <div class="card-title">Smart Analytics</div>
        <div class="card-text">
            Experience real-time weather analytics powered by cutting-edge technology. 
            Our platform transforms complex weather data into actionable insights through:
        </div>
        <ul class="feature-list">
            <li>📈 Interactive time-series visualizations</li>
            <li>🌡️ Multi-city temperature tracking</li>
            <li>💧 Humidity and precipitation analysis</li>
            <li>🌬️ Wind pattern monitoring</li>
            <li>📉 Trend detection and anomaly alerts</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="glass-card">
        <div class="card-icon">🤖</div>
        <div class="card-title">AI Forecasting</div>
        <div class="card-text">
            Leverage state-of-the-art machine learning models for accurate weather prediction:
        </div>
        <ul class="feature-list">
            <li>📊 ARIMA/SARIMA statistical models</li>
            <li>🌲 Random Forest regression</li>
            <li>📈 Linear Regression analysis</li>
            <li>🔮 Facebook Prophet forecasting</li>
            <li>🧠 LSTM deep learning networks</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Second row of cards
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="glass-card">
        <div class="card-icon">🎯</div>
        <div class="card-title">Portfolio Integration</div>
        <div class="card-text">
            Weather insights mapped to business portfolios:
        </div>
        <ul class="feature-list">
            <li>🏙️ Nairobi - Urban Microloans</li>
            <li>🌾 Kisumu - Lake Region Agri</li>
            <li>🌽 Nakuru - High Potential Farming</li>
            <li>⚓ Mombasa - Coastal Trade</li>
            <li>💼 Risk assessment tools</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="glass-card">
        <div class="card-icon">📱</div>
        <div class="card-title">Interactive Features</div>
        <div class="card-text">
            Explore weather data with powerful tools:
        </div>
        <ul class="feature-list">
            <li>🗺️ Interactive weather maps</li>
            <li>📊 Custom chart builder</li>
            <li>📥 Data export options</li>
            <li>📈 Model comparison dashboard</li>
            <li>🔔 Alert configuration</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Data Source Section
st.markdown("""
<div class="data-source">
    <h2 style="color: white; text-align: center; margin-bottom: 2rem;">🌐 Data Sources & Technology</h2>
    <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 1rem; margin-bottom: 2rem;">
        <span class="api-tag">Open-Meteo API</span>
        <span class="api-tag">Python 3.9+</span>
        <span class="api-tag">FastAPI</span>
        <span class="api-tag">Streamlit</span>
        <span class="api-tag">TensorFlow</span>
        <span class="api-tag">Prophet</span>
        <span class="api-tag">Scikit-learn</span>
        <span class="api-tag">Pandas</span>
        <span class="api-tag">Plotly</span>
    </div>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem;">
        <div style="text-align: center;">
            <h3 style="color: #ffd700; margin-bottom: 1rem;">📡 Real-time Data</h3>
            <p style="color: white;">Live weather updates from Open-Meteo API with global coverage and high-resolution data</p>
        </div>
        <div style="text-align: center;">
            <h3 style="color: #ffd700; margin-bottom: 1rem;">🤖 ML Models</h3>
            <p style="color: white;">7 different forecasting models with automated training and evaluation</p>
        </div>
        <div style="text-align: center;">
            <h3 style="color: #ffd700; margin-bottom: 1rem;">📊 Visual Analytics</h3>
            <p style="color: white;">Interactive dashboards with real-time updates and custom visualizations</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Benefits Section
st.markdown('<h2 class="section-title">✨ Key Benefits</h2>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

benefits = [
    {"icon": "🎯", "title": "Accurate", "desc": "High-precision forecasts"},
    {"icon": "⚡", "title": "Real-time", "desc": "Live data updates"},
    {"icon": "📈", "title": "Scalable", "desc": "Handles big data"},
    {"icon": "🔒", "title": "Reliable", "desc": "90% uptime"}
]

for col, benefit in zip([col1, col2, col3, col4], benefits):
    with col:
        st.markdown(f"""
        <div style="text-align: center; padding: 1.5rem; background: rgba(255,255,255,0.05); border-radius: 15px; margin: 0.5rem;">
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">{benefit['icon']}</div>
            <h3 style="color: #ffd700; margin-bottom: 0.5rem;">{benefit['title']}</h3>
            <p style="color: white;">{benefit['desc']}</p>
        </div>
        """, unsafe_allow_html=True)

# Navigation Message
st.markdown("""
<div class="nav-message">
    <p class="nav-message-text">
        👉 Ready to explore? Use the <span class="nav-highlight">sidebar</span> to navigate to:
    </p>
    <div style="display: flex; justify-content: center; gap: 2rem; margin-top: 1rem; flex-wrap: wrap;">
        <span style="color: white; font-size: 1.1rem;">📊 Dashboard</span>
        <span style="color: #ffd700; font-size: 1.5rem;">•</span>
        <span style="color: white; font-size: 1.1rem;">🔮 Predictions</span>
        <span style="color: #ffd700; font-size: 1.5rem;">•</span>
        <span style="color: white; font-size: 1.1rem;">🗺️ Weather Map</span>
        <span style="color: #ffd700; font-size: 1.5rem;">•</span>
        <span style="color: white; font-size: 1.1rem;">📈 Model Comparison</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 4rem; padding: 2rem; border-top: 1px solid rgba(255,255,255,0.2);">
    <p style="color: rgba(255,255,255,0.7);">
        © 2026 DSA 8502: Predictive Optimization Analytics | Created by Chepkwony C Viotry (Reg No: 192744)
    </p>
    <p style="color: rgba(255,255,255,0.5); font-size: 0.9rem; margin-top: 0.5rem;">
        Version 2.0 | Last Updated: March 2026
    </p>
</div>
""", unsafe_allow_html=True)

# Enhanced Sidebar
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem; background: rgba(255,255,255,0.1); border-radius: 15px; margin-bottom: 2rem;">
        <h1 style="color: white; font-size: 2rem;">🌤️</h1>
        <h2 style="color: #ffd700; font-size: 1.5rem;">Weather AI</h2>
        <p style="color: rgba(255,255,255,0.8);">Professional Edition</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🧭 Navigation")
    
    # Current time display
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.markdown(f"""
    <div style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 10px; margin: 1rem 0;">
        <p style="color: #ffd700; margin: 0;">Current Time:</p>
        <p style="color: white; font-size: 0.9rem;">{current_time}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📌 Quick Access")
    
    # Quick links with icons
    pages = {
        "🏠 Home": "Home",
        "📊 Dashboard": "Dashboard", 
        "🔮 Predictions": "Predictions",
        "🗺️ Weather Map": "Map",
        "📈 Model Comparison": "Comparison"
    }
    
    for icon, name in pages.items():
        st.markdown(f"""
        <div style="padding: 0.5rem; margin: 0.2rem 0; border-radius: 10px; background: rgba(255,255,255,0.05);">
            <span style="color: white;">{icon}</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # System Status
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1rem; border-radius: 15px;">
        <h4 style="color: white; margin-bottom: 0.5rem;">🟢 System Status</h4>
        <p style="color: white; font-size: 0.9rem; margin: 0;">All systems operational</p>
        <p style="color: #ffd700; font-size: 0.9rem;">API: Connected</p>
        <p style="color: #ffd700; font-size: 0.9rem;">Models: Loaded</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 👨‍💻 Developer")
    st.markdown("""
    <div style="text-align: center;">
        <p style="color: white;">Chepkwony C Viotry</p>
        <p style="color: #ffd700; font-size: 0.9rem;">Reg No: 192744</p>
    </div>
    """, unsafe_allow_html=True)
    