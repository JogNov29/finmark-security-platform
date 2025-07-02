import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import json
import numpy as np
import time

# Page configuration
st.set_page_config(
    page_title="FinMark Security Operations Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for better visibility
st.markdown("""
<style>
    /* Dark theme with better contrast */
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }
    
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #2a5298;
        margin-bottom: 1rem;
    }
    
    .alert-critical { border-left-color: #dc3545; background-color: #f8d7da; }
    .alert-warning { border-left-color: #ffc107; background-color: #fff3cd; }
    .alert-info { border-left-color: #17a2b8; background-color: #d1ecf1; }
    
    /* FORCE BLACK TEXT IN ALERTS - Higher Specificity */
    div[data-testid="stMarkdown"] .metric-card.alert-critical,
    div[data-testid="stMarkdown"] .metric-card.alert-warning,
    div[data-testid="stMarkdown"] .metric-card.alert-info {
        color: #000000 !important;
    }
    
    div[data-testid="stMarkdown"] .metric-card.alert-critical *,
    div[data-testid="stMarkdown"] .metric-card.alert-warning *,
    div[data-testid="stMarkdown"] .metric-card.alert-info * {
        color: #000000 !important;
    }
    
    div[data-testid="stMarkdown"] .metric-card strong {
        color: #000000 !important;
    }
    
    div[data-testid="stMarkdown"] .metric-card small {
        color: #333333 !important;
    }
    
    /* Fix text visibility */
    .stMarkdown p, .stText, div[data-testid="metric-container"] {
        color: #000000 !important;
    }
    
    /* Session info styling */
    .session-info {
        background: #e7f3ff;
        border: 2px solid #007bff;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    .session-info h4 {
        color: #007bff !important;
        margin-top: 0 !important;
    }
    
    .session-info p {
        color: #000000 !important;
        margin: 0.25rem 0 !important;
    }
</style>
""", unsafe_allow_html=True)

def get_api_data(endpoint):
    """Fetch data from Django API"""
    try:
        response = requests.get(f"http://localhost:8000/api/{endpoint}/", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        return None

def test_api_connection():
    """Test API connection"""
    try:
        response = requests.get("http://localhost:8000/api/status/", timeout=5)
        return response.status_code == 200, response.json() if response.status_code == 200 else None
    except:
        return False, None

def test_auth(username, password):
    """Test authentication"""
    try:
        response = requests.post(
            "http://localhost:8000/api/auth/token/",
            json={"username": username, "password": password},
            timeout=5
        )
        return response.status_code == 200
    except:
        return False

MAX_ATTEMPTS = 3
COOLDOWN_SECONDS = 300 #5 mins

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🛡️ FinMark Security Operations Center</h1>
        <p>Real-time Security Analytics & Monitoring Dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check login state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.username = None
        st.session_state.login_time = None
    if 'login_attempts' not in st.session_state:
        st.session_state.login_attempts = 0
    if 'lockout_time' not in st.session_state:
        st.session_state.lockout_time = None

    
    # Sidebar
    with st.sidebar:
        st.markdown("### 👤 Session Information")
        
        if st.session_state.authenticated:
            # Show user info
            st.markdown(f"""
            <div class="session-info">
                <h4>👤 {st.session_state.username}</h4>
                <p><strong>Role:</strong> Admin</p>
                <p><strong>Login:</strong> {st.session_state.login_time}</p>
                <p><strong>Token:</strong> ✅ Valid</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🚪 Logout"):
                st.session_state.authenticated = False
                st.session_state.username = None
                st.session_state.login_time = None
                st.session_state.login_attempts = 0
                st.session_state.lockout_time = None
                st.rerun()
        
        else:
            st.subheader("🔐 Login")

            now = datetime.now()

            # Handle cooldown
            if st.session_state.login_attempts >= MAX_ATTEMPTS:
                if st.session_state.lockout_time is None:
                    st.session_state.lockout_time = now

                cooldown_end = st.session_state.lockout_time + timedelta(seconds=COOLDOWN_SECONDS)
                if now < cooldown_end:
                    remaining_time = int((cooldown_end - now).total_seconds())

                    # Live countdown
                    countdown_placeholder = st.empty()
                    while remaining_time > 0:
                        mins, secs = divmod(remaining_time, 60)
                        countdown_placeholder.warning(f"⏳ Too many failed attempts. Retry in {mins}:{secs:02d} minute(s)...")
                        time.sleep(1)
                        remaining_time -= 1
                        countdown_placeholder.empty()
                    # Reset after cooldown
                    st.session_state.login_attempts = 0
                    st.session_state.lockout_time = None
                    st.rerun()

            # Login form
            with st.form("login_form"):
                username = st.text_input("Username", value="admin")
                password = st.text_input("Password", type="password", value="admin123")
                login_button = st.form_submit_button("Login")

                if login_button:
                    if test_auth(username, password):
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.session_state.login_time = datetime.now().strftime("%H:%M:%S")
                        st.session_state.login_attempts = 0
                        st.session_state.lockout_time = None
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.session_state.login_attempts += 1
                        remaining = MAX_ATTEMPTS - st.session_state.login_attempts
                        if remaining > 0:
                            st.error(f"❌ Login failed. {remaining} attempt(s) remaining.")
                        else:
                            st.warning("🚫 Too many failed login attempts. Please wait...")
        
        st.markdown("---")
        st.markdown("### ⚙️ Quick Actions")
        
        if st.button("🔄 Refresh Data"):
            st.rerun()
        
        if st.button("🧪 Test Connection"):
            api_connected, api_data = test_api_connection()
            if api_connected:
                st.success("✅ API Connected")
                if api_data and api_data.get('database', {}).get('connected'):
                    st.success("✅ Database Connected")
            else:
                st.error("❌ API Disconnected")
    
    # Get API data
    api_status = get_api_data("status")
    metrics = get_api_data("metrics")
    db_info = get_api_data("database")
    
    # Main dashboard content (only show if authenticated)
    if st.session_state.authenticated:
        # Metrics row
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        # Get metrics from API or use defaults
        if metrics:
            critical_alerts = metrics.get('critical_alerts', 3)
            active_threats = metrics.get('active_threats', 12)
            system_health = metrics.get('system_health', 98.2)
            failed_logins = metrics.get('failed_logins', 27)
        else:
            critical_alerts = 3
            active_threats = 12
            system_health = 98.2
            failed_logins = 27
        
        with col1:
            st.metric("🚨 Critical Alerts", str(critical_alerts), "+2")
        with col2:
            st.metric("⚠️ Active Threats", str(active_threats), "-5")
        with col3:
            st.metric("💚 System Health", f"{system_health}%", "+0.3%")
        with col4:
            st.metric("📦 Daily Orders", "1,847", "Target: 3,000")
        with col5:
            st.metric("🔐 Failed Logins", str(failed_logins), "-12")
        with col6:
            st.metric("📊 Data Transfer", "2.1TB", "+15%")
        
        # Charts section
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            st.subheader("🌐 Network Traffic Analysis")
            
            # Generate sample traffic data
            hours = list(range(24))
            traffic_data = pd.DataFrame({
                'Hour': hours,
                'Inbound (GB)': np.random.normal(50, 15, 24).clip(min=0),
                'Outbound (GB)': np.random.normal(30, 10, 24).clip(min=0),
                'Threats Blocked': np.random.poisson(5, 24)
            })
            
            # Create improved Plotly chart with better colors
            fig = go.Figure()
            
            # Add Inbound traffic
            fig.add_trace(go.Scatter(
                x=traffic_data['Hour'],
                y=traffic_data['Inbound (GB)'],
                mode='lines+markers',
                name='Inbound (GB)',
                line=dict(color='#00ff88', width=3),
                marker=dict(size=6, color='#00ff88')
            ))
            
            # Add Outbound traffic
            fig.add_trace(go.Scatter(
                x=traffic_data['Hour'],
                y=traffic_data['Outbound (GB)'],
                mode='lines+markers',
                name='Outbound (GB)',
                line=dict(color='#ff6b6b', width=3),
                marker=dict(size=6, color='#ff6b6b')
            ))
            
            # Update layout with dark theme
            fig.update_layout(
                title="Network Traffic - Last 24 Hours",
                xaxis_title="Hour",
                yaxis_title="Traffic (GB)",
                plot_bgcolor='#2d3748',
                paper_bgcolor='#1a202c',
                font_color='white',
                title_font_color='white',
                height=400,
                showlegend=True,
                legend=dict(
                    bgcolor='rgba(0,0,0,0.5)',
                    bordercolor='white',
                    borderwidth=1
                )
            )
            
            # Style axes
            fig.update_xaxes(
                gridcolor='#4a5568',
                zerolinecolor='#4a5568',
                tickcolor='white'
            )
            fig.update_yaxes(
                gridcolor='#4a5568',
                zerolinecolor='#4a5568',
                tickcolor='white'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col_right:
            st.subheader("🚨 Security Alerts")
            
            # Sample alerts with proper styling
            alerts = [
                ("🔴", "CRITICAL", "Multiple failed login attempts"),
                ("🟡", "WARNING", "Unusual traffic detected"),
                ("🟢", "INFO", "Firewall rules updated"),
                ("🟡", "WARNING", "High CPU usage on DB01"),
                ("🟢", "INFO", "Security scan completed")
            ]
            
            for icon, level, message in alerts:
                if level == "CRITICAL":
                    alert_class = "alert-critical"
                elif level == "WARNING":
                    alert_class = "alert-warning"
                else:
                    alert_class = "alert-info"
                
                st.markdown(f"""
                <div class="metric-card {alert_class}" style="color: #000000 !important;">
                    <span style="color: #000000 !important;">{icon} <strong style="color: #000000 !important;">{level}</strong></span><br>
                    <span style="color: #000000 !important;">{message}</span><br>
                    <small style="color: #333333 !important;">2 minutes ago</small>
                </div>
                """, unsafe_allow_html=True)
        
        # System Information Table
        st.subheader("🖥️ System Information")
        
        # Create system status data
        system_data = {
            'Component': [
                'Django API Server',
                'Database (SQLite)',
                'JWT Authentication',
                'Streamlit Dashboard',
                'Security Monitor',
                'CORS Headers'
            ],
            'Status': [
                '🟢 Online' if api_status else '🔴 Offline',
                '🟢 Connected' if db_info and db_info.get('database_connected') else '🔴 Disconnected',
                '🟢 Active',
                '🟢 Running',
                '🟢 Active',
                '🟢 Enabled'
            ],
            'Endpoint/Location': [
                'http://localhost:8000/api/',
                'db.sqlite3',
                '/api/auth/token/',
                'http://localhost:8501',
                'Security Events Monitor',
                'CORS Middleware'
            ],
            'Details': [
                f"Tables: {db_info.get('table_count', 0)}" if db_info else "Not connected",
                f"Size: {db_info.get('table_count', 0)} tables" if db_info else "No data",
                'Bearer Token Auth',
                'Streamlit v1.46+',
                'Real-time monitoring',
                'All origins allowed'
            ],
            'Last Check': [
                datetime.now().strftime('%H:%M:%S'),
                datetime.now().strftime('%H:%M:%S'),
                st.session_state.login_time if st.session_state.login_time else 'N/A',
                datetime.now().strftime('%H:%M:%S'),
                datetime.now().strftime('%H:%M:%S'),
                datetime.now().strftime('%H:%M:%S')
            ]
        }
        
        # Display as table
        system_df = pd.DataFrame(system_data)
        st.dataframe(system_df, hide_index=True, use_container_width=True, height=250)
        
        # API Status Summary
        if api_status and db_info:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.info(f"📊 Database Tables: {db_info.get('table_count', 0)}")
            
            with col2:
                st.info(f"👥 Total Users: {db_info.get('users_count', 0)}")
            
            with col3:
                st.info(f"🕐 API Status: {api_status.get('status', 'Unknown')}")
    
    else:
        # Show login prompt
        st.info("🔐 Please login to access the FinMark Security Dashboard")
        st.markdown("""
        **Demo Credentials:**
        - **Username:** admin
        - **Password:** admin123
        """)
    
    # Footer
    st.markdown("---")
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    api_indicator = "🟢 Connected" if api_status else "🔴 Disconnected"
    db_indicator = "🟢 Connected" if db_info and db_info.get('database_connected') else "🔴 Disconnected"
    
    st.markdown(f"""
    **FinMark Security Operations Center** | 
    Last updated: {current_time} | 
    API: {api_indicator} | 
    DB: {db_indicator} |
    User: {st.session_state.username if st.session_state.authenticated else 'Not logged in'}
    """)

if __name__ == "__main__":
    main()
