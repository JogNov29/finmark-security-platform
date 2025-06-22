# FinMark Security Operations Center - Complete Dashboard
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json
import time

# Page configuration
st.set_page_config(
    page_title="FinMark Security Operations Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .metric-container {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 5px solid #007bff;
    }
    
    .critical-metric { border-left-color: #dc3545; background: linear-gradient(135deg, #fff5f5 0%, #fff 100%); }
    .warning-metric { border-left-color: #ffc107; background: linear-gradient(135deg, #fff8e1 0%, #fff 100%); }
    .success-metric { border-left-color: #28a745; background: linear-gradient(135deg, #f0f9ff 0%, #fff 100%); }
    .info-metric { border-left-color: #17a2b8; background: linear-gradient(135deg, #e3f2fd 0%, #fff 100%); }
    
    .alert-panel {
        background-color: #fff;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = "http://localhost:8000/api"

class FinMarkAPI:
    """API client for FinMark backend"""
    
    def __init__(self):
        self.base_url = API_BASE_URL
        self.headers = {}
    
    def set_auth_token(self, token):
        self.headers = {'Authorization': f'Bearer {token}'}
    
    def authenticate(self, username, password):
        try:
            response = requests.post(f"{self.base_url}/auth/token/", {
                'username': username,
                'password': password
            }, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            return None
        except requests.exceptions.RequestException:
            return None
    
    def get_dashboard_stats(self):
        try:
            response = requests.get(
                f"{self.base_url}/security/dashboard_stats/",
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
        except requests.exceptions.RequestException:
            pass
        
        return {
            'critical_alerts': 0,
            'active_threats': 0,
            'total_events': 0,
            'devices_online': 0,
            'failed_logins': 0,
            'system_health': 100.0
        }
    
    def get_recent_events(self):
        try:
            response = requests.get(
                f"{self.base_url}/security/recent_events/",
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
        except requests.exceptions.RequestException:
            pass
        return []
    
    def get_network_devices(self):
        try:
            response = requests.get(
                f"{self.base_url}/devices/network_status/",
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
        except requests.exceptions.RequestException:
            pass
        return []
    
    def get_system_metrics(self):
        try:
            response = requests.get(
                f"{self.base_url}/metrics/performance_timeline/",
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
        except requests.exceptions.RequestException:
            pass
        return []

# Initialize API client
api = FinMarkAPI()

def init_auth():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'access_token' not in st.session_state:
        st.session_state.access_token = None

def authenticate_user(username, password):
    tokens = api.authenticate(username, password)
    
    if tokens:
        st.session_state.authenticated = True
        st.session_state.access_token = tokens['access']
        st.session_state.username = username
        
        role_mapping = {
            'admin': 'admin',
            'security': 'security', 
            'analyst': 'analyst'
        }
        st.session_state.user_role = role_mapping.get(username, 'user')
        
        api.set_auth_token(tokens['access'])
        return True
    
    return False

def check_api_connection():
    try:
        response = requests.get("http://localhost:8000/admin/", timeout=2)
        return response.status_code in [200, 302]
    except:
        return False

def login_page():
    st.markdown("""
    <div class="main-header">
        <h1>🛡️ FinMark Security Operations Center</h1>
        <p>Advanced Security Analytics & Threat Intelligence Platform</p>
        <p><small>Milestone 1 Prototype - Connected to Live Django Backend</small></p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        api_status = check_api_connection()
        if api_status:
            st.success("🟢 Django API is running on localhost:8000")
        else:
            st.error("🔴 Django API is not running. Please start with: `python manage.py runserver`")
        
        st.markdown("### 🔐 Secure Authentication")
        
        with st.form("login_form"):
            username = st.text_input("👤 Username", placeholder="Enter your username")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            
            if st.form_submit_button("🚀 Login", use_container_width=True):
                if not api_status:
                    st.error("❌ Cannot login - Django API is not running")
                elif authenticate_user(username, password):
                    st.success("✅ Authentication successful!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")
        
        st.info("""
        **Demo Credentials:**
        - **Admin:** admin / admin123
        - **Security:** security / security123  
        - **Analyst:** analyst / analyst123
        """)

def display_header_metrics():
    data = api.get_dashboard_stats()
    
    st.markdown(f"""
    <div class="main-header">
        <h1>🛡️ FinMark Security Operations Center</h1>
        <p>Real-time Security Analytics & Monitoring Dashboard</p>
        <p><strong>User:</strong> {st.session_state.username} | <strong>Role:</strong> {st.session_state.user_role} | <strong>Status:</strong> Connected to Live Database</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.markdown(f"""
        <div class="metric-container critical-metric">
            <h3>CRITICAL ALERTS</h3>
            <h1 style="color: #dc3545; margin: 0;">{data['critical_alerts']}</h1>
            <p>🚨 From real database</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-container warning-metric">
            <h3>ACTIVE THREATS</h3>
            <h1 style="color: #ffc107; margin: 0;">{data['active_threats']}</h1>
            <p>⚠️ Real threat count</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-container success-metric">
            <h3>SYSTEM HEALTH</h3>
            <h1 style="color: #28a745; margin: 0;">{data['system_health']}%</h1>
            <p>✅ Calculated from devices</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-container info-metric">
            <h3>TOTAL EVENTS</h3>
            <h1 style="color: #17a2b8; margin: 0;">{data['total_events']}</h1>
            <p>📊 From security logs</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div class="metric-container warning-metric">
            <h3>FAILED LOGINS</h3>
            <h1 style="color: #ffc107; margin: 0;">{data['failed_logins']}</h1>
            <p>🔒 Last 24 hours</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col6:
        st.markdown(f"""
        <div class="metric-container info-metric">
            <h3>DEVICES ONLINE</h3>
            <h1 style="color: #17a2b8; margin: 0;">{data['devices_online']}</h1>
            <p>🌐 Network status</p>
        </div>
        """, unsafe_allow_html=True)

def display_main_dashboard():
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 Real Security Events Timeline")
        
        events = api.get_recent_events()
        
        if events:
            df = pd.DataFrame(events)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            fig = px.scatter(
                df.head(20), 
                x='timestamp', 
                y='event_type',
                color='severity',
                hover_data=['source_ip', 'details'],
                title="Recent Security Events from Your Database",
                color_discrete_map={
                    'critical': '#dc3545',
                    'warning': '#ffc107',
                    'info': '#17a2b8'
                }
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No security events data available")
    
    with col2:
        st.subheader("🚨 Live Security Alerts")
        
        if events:
            critical_events = [e for e in events[:10] if e['severity'] == 'critical']
            
            for event in critical_events:
                st.markdown(f"""
                <div class="alert-panel">
                    <div style="background-color: #dc3545; color: white; padding: 8px; border-radius: 4px; margin-bottom: 8px;">
                        <strong>CRITICAL</strong><br>
                        {event['details']}<br>
                        <small>IP: {event['source_ip']} | {pd.to_datetime(event['timestamp']).strftime('%H:%M:%S')}</small>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No recent alerts")
    
    # Network devices
    st.markdown("---")
    st.subheader("🌐 Network Device Status")
    
    devices = api.get_network_devices()
    
    if devices:
        df = pd.DataFrame(devices)
        
        for _, device in df.iterrows():
            status_color = {
                'active': '#28a745',
                'warning': '#ffc107', 
                'critical': '#dc3545'
            }.get(device['status'], '#28a745')
            
            st.markdown(f"""
            <div style="background: white; padding: 12px; margin: 8px 0; border-radius: 8px; border-left: 4px solid {status_color};">
                <strong>{device['hostname']}</strong> ({device['ip_address']}) - {device['device_type']}<br>
                <small>OS: {device['os']} | Status: {device['status'].upper()}</small>
                {f'<br><em>⚠️ {device["vulnerabilities"]}</em>' if device.get('vulnerabilities') else ''}
            </div>
            """, unsafe_allow_html=True)
    
    # System metrics
    st.markdown("---")
    st.subheader("📈 System Performance")
    
    metrics = api.get_system_metrics()
    
    if metrics:
        df = pd.DataFrame(metrics)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            fig = px.line(df, x='timestamp', y='cpu_usage', title='CPU Usage (%)')
            st.plotly_chart(fig, use_container_width=True)
        
        with col_b:
            fig = px.line(df, x='timestamp', y='memory_usage', title='Memory Usage (%)')
            st.plotly_chart(fig, use_container_width=True)

def sidebar_controls():
    st.sidebar.markdown(f"### 👤 Welcome, {st.session_state.username}")
    st.sidebar.markdown(f"**Role:** {st.session_state.user_role.upper()}")
    
    api_status = check_api_connection()
    if api_status:
        st.sidebar.success("🟢 Connected to Django API")
    else:
        st.sidebar.error("🔴 Django API Disconnected")
    
    st.sidebar.markdown("---")
    
    auto_refresh = st.sidebar.checkbox("Enable auto-refresh", value=False)
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Data Sources")
    st.sidebar.markdown("""
    - 🗄️ **SQLite Database:** Real data
    - 📡 **Django API:** Live connection
    - 🔒 **Security Events:** Real logs
    - 🌐 **Network Devices:** Actual inventory
    - 📈 **System Metrics:** Performance data
    """)
    
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user_role = None
        st.rerun()

def main_dashboard():
    sidebar_controls()
    display_header_metrics()
    st.markdown("---")
    display_main_dashboard()

def main():
    init_auth()
    
    if not st.session_state.authenticated:
        login_page()
    else:
        main_dashboard()

if __name__ == "__main__":
    main()
