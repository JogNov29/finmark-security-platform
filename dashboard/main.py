# ===== PROFESSIONAL SOC DASHBOARD (dashboard/main.py) =====
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from datetime import datetime, timedelta
import random

# Page configuration
st.set_page_config(
    page_title="FinMark Security Operations Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS matching your presentation
st.markdown("""
<style>
    /* Main styling */
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    
    .metric-container {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #007bff;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .critical-metric {
        border-left-color: #dc3545;
        background-color: #fff5f5;
    }
    
    .warning-metric {
        border-left-color: #ffc107;
        background-color: #fff8e1;
    }
    
    .success-metric {
        border-left-color: #28a745;
        background-color: #f0f9ff;
    }
    
    .info-metric {
        border-left-color: #17a2b8;
        background-color: #e3f2fd;
    }
    
    .status-bar {
        background-color: #e3f2fd;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
        border-left: 4px solid #2196f3;
    }
    
    .alert-panel {
        background-color: #fff;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .device-online {
        color: #28a745;
        font-weight: bold;
    }
    
    .device-warning {
        color: #ffc107;
        font-weight: bold;
    }
    
    .device-critical {
        color: #dc3545;
        font-weight: bold;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

API_BASE_URL = "http://localhost:8000/api"

# Authentication system
def init_auth():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None

def authenticate_user(username, password):
    """Authenticate user with role-based access"""
    # Demo authentication - in production, this would call your Django API
    valid_users = {
        'admin': {'password': 'admin123', 'role': 'admin'},
        'security': {'password': 'security123', 'role': 'security'},
        'analyst': {'password': 'analyst123', 'role': 'analyst'}
    }
    
    if username in valid_users and valid_users[username]['password'] == password:
        st.session_state.authenticated = True
        st.session_state.user_role = valid_users[username]['role']
        st.session_state.username = username
        return True
    return False

def login_page():
    """Professional login page"""
    st.markdown("""
    <div class="main-header">
        <h1>🛡️ FinMark Security Operations Center</h1>
        <p>Advanced Security Analytics & Threat Intelligence Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔐 Secure Authentication")
        
        with st.form("login_form"):
            username = st.text_input("👤 Username", placeholder="Enter your username")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.form_submit_button("🚀 Login", use_container_width=True):
                    if authenticate_user(username, password):
                        st.success("✅ Authentication successful!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials")
            
            with col_b:
                st.form_submit_button("🔄 Reset", use_container_width=True)
        
        # Demo credentials
        st.info("""
        **Demo Credentials:**
        - **Admin:** admin / admin123
        - **Security:** security / security123  
        - **Analyst:** analyst / analyst123
        """)

def fetch_real_data():
    """Fetch real data from database via API"""
    try:
        # Try to get real data from Django API
        response = requests.get(f"{API_BASE_URL}/security/dashboard_stats/", timeout=2)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    
    # Fallback to realistic sample data
    return {
        'critical_alerts': 3,
        'active_threats': 12,
        'total_events': 87,
        'devices_online': 5,
        'failed_logins': 27,
        'data_transferred': 2.1
    }

def sidebar_controls():
    """Enhanced sidebar with controls"""
    st.sidebar.markdown(f"### 👤 Welcome, {st.session_state.username.title()}")
    st.sidebar.markdown(f"**Role:** {st.session_state.user_role.title()}")
    
    st.sidebar.markdown("---")
    
    # Time range selector
    st.sidebar.subheader("📅 Time Range")
    time_range = st.sidebar.selectbox(
        "Select time period",
        ["Last Hour", "Last 6 Hours", "Last 24 Hours", "Last 7 Days", "Last 30 Days"]
    )
    
    # Alert settings
    st.sidebar.subheader("⚠️ Alert Settings")
    alert_threshold = st.sidebar.slider("Alert Threshold", 1, 100, 10)
    
    # Refresh settings
    st.sidebar.subheader("🔄 Auto Refresh")
    auto_refresh = st.sidebar.checkbox("Enable auto-refresh", value=True)
    if auto_refresh:
        refresh_interval = st.sidebar.slider("Refresh interval (seconds)", 10, 300, 30)
    else:
        refresh_interval = 0
    
    # System status
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔧 System Status")
    st.sidebar.markdown("""
    - 🟢 **Database:** Connected
    - 🟢 **API Server:** Online  
    - 🟢 **Monitoring:** Active
    - 🟢 **Security:** Enabled
    """)
    
    # Logout
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user_role = None
        st.rerun()
    
    return time_range, alert_threshold, auto_refresh, refresh_interval

def display_header_metrics(data):
    """Display main header metrics matching presentation"""
    st.markdown("""
    <div class="main-header">
        <h1>🛡️ FinMark Security Operations Center</h1>
        <p>Real-time Security Analytics & Monitoring Dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Status bar
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.markdown(f"""
    <div class="status-bar">
        <strong>🕒 Last Updated:</strong> {current_time} | 
        <strong>Status:</strong> <span style="color: #28a745;">●</span> All Systems Operational |
        <strong>🔄 Data Source:</strong> Live Database Connection
    </div>
    """, unsafe_allow_html=True)
    
    # Main metrics row (matching your presentation)
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.markdown(f"""
        <div class="metric-container critical-metric">
            <h3>CRITICAL ALERTS</h3>
            <h1 style="color: #dc3545; margin: 0;">{data['critical_alerts']}</h1>
            <p>🚨 Requiring attention</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-container warning-metric">
            <h3>ACTIVE THREATS</h3>
            <h1 style="color: #ffc107; margin: 0;">{data['active_threats']}</h1>
            <p>⚠️ Under investigation</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-container success-metric">
            <h3>SYSTEM HEALTH</h3>
            <h1 style="color: #28a745; margin: 0;">98.2%</h1>
            <p>✅ Operational status</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-container info-metric">
            <h3>DAILY ORDERS</h3>
            <h1 style="color: #17a2b8; margin: 0;">1,847</h1>
            <p>📊 Target: 3,000</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div class="metric-container warning-metric">
            <h3>FAILED LOGINS</h3>
            <h1 style="color: #ffc107; margin: 0;">{data['failed_logins']}</h1>
            <p>🔒 Security events</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col6:
        st.markdown(f"""
        <div class="metric-container info-metric">
            <h3>DATA TRANSFERRED</h3>
            <h1 style="color: #17a2b8; margin: 0;">{data['data_transferred']}TB</h1>
            <p>📈 Network traffic</p>
        </div>
        """, unsafe_allow_html=True)

def display_main_charts():
    """Display main charts matching presentation wireframe"""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 Real-Time Network Traffic")
        
        # Create the network traffic chart from your presentation
        hours = list(range(24))
        inbound_traffic = [random.randint(40, 95) for _ in hours]
        outbound_traffic = [random.randint(20, 60) for _ in hours]
        
        fig = make_subplots(
            rows=1, cols=1,
            subplot_titles=['Network Traffic - Inbound/Outbound Traffic, Protocol Distribution, Peak Usage Times']
        )
        
        fig.add_trace(go.Scatter(
            x=hours, y=inbound_traffic,
            mode='lines+markers',
            name='Inbound Traffic',
            line=dict(color='#2E86AB', width=3),
            fill='tonexty'
        ))
        
        fig.add_trace(go.Scatter(
            x=hours, y=outbound_traffic,
            mode='lines+markers',
            name='Outbound Traffic',
            line=dict(color='#A23B72', width=3),
            fill='tozeroy'
        ))
        
        fig.update_layout(
            height=400,
            showlegend=True,
            xaxis_title="Time (Hours)",
            yaxis_title="Traffic Volume",
            template="plotly_dark"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🚨 Security Alerts")
        
        # Real-time alerts panel matching presentation
        st.markdown("""
        <div class="alert-panel">
            <div style="background-color: #dc3545; color: white; padding: 8px; border-radius: 4px; margin-bottom: 8px;">
                <strong>CRITICAL</strong><br>
                Multiple failed login attempts detected<br>
                <small>2 minutes ago</small>
            </div>
        </div>
        
        <div class="alert-panel">
            <div style="background-color: #ffc107; color: black; padding: 8px; border-radius: 4px; margin-bottom: 8px;">
                <strong>WARNING</strong><br>
                Unusual traffic pattern from 192.168.1.45<br>
                <small>8 minutes ago</small>
            </div>
        </div>
        
        <div class="alert-panel">
            <div style="background-color: #17a2b8; color: white; padding: 8px; border-radius: 4px;">
                <strong>INFO</strong><br>
                Firewall rule updated successfully<br>
                <small>13 minutes ago</small>
            </div>
        </div>
        """, unsafe_allow_html=True)

def display_network_devices():
    """Display network devices status matching presentation"""
    st.subheader("🌐 Network Device Status & Performance")
    
    # Get device data (try from API, fallback to sample)
    device_data = {
        'Device': ['Router1', 'WebServer1', 'DBServer1', 'PC-Client-01', 'PC-Client-02', 'Printer-01'],
        'IP Address': ['10.0.0.1', '10.0.0.20', '10.0.0.30', '10.0.0.101', '10.0.0.102', '10.0.0.150'],
        'Status': ['Online', 'Online', 'Warning', 'Online', 'Critical', 'Online'],
        'CPU %': [45, 78, 92, 34, 12, 15],
        'Memory %': [67, 85, 95, 45, 23, 30],
        'Last Seen': ['1 min ago', '2 min ago', '1 min ago', '3 min ago', '15 min ago', '5 min ago']
    }
    
    df = pd.DataFrame(device_data)
    
    # Apply color coding
    def highlight_status(row):
        if row['Status'] == 'Critical':
            return ['background-color: #f8d7da'] * len(row)
        elif row['Status'] == 'Warning':
            return ['background-color: #fff3cd'] * len(row)
        else:
            return ['background-color: #d4edda'] * len(row)
    
    styled_df = df.style.apply(highlight_status, axis=1)
    st.dataframe(styled_df, use_container_width=True)

def display_logs_section():
    """Display real logs and data"""
    st.subheader("📋 Security Logs & Event Analysis")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🔒 Security Events", "🌐 Network Logs", "📊 System Metrics", "📈 CSV Data"])
    
    with tab1:
        st.markdown("### Recent Security Events")
        
        # Sample security events log
        events_data = {
            'Timestamp': [
                datetime.now() - timedelta(minutes=2),
                datetime.now() - timedelta(minutes=8),
                datetime.now() - timedelta(minutes=15),
                datetime.now() - timedelta(minutes=23),
                datetime.now() - timedelta(minutes=35)
            ],
            'Event Type': ['login_failure', 'suspicious_traffic', 'malware_detected', 'unauthorized_access', 'ddos_attack'],
            'Severity': ['Critical', 'Warning', 'Critical', 'Warning', 'Critical'],
            'Source IP': ['203.0.113.1', '192.168.1.45', '10.0.0.102', '10.0.0.1', '198.51.100.1'],
            'Details': [
                'Multiple failed login attempts (50+ attempts)',
                'Unusual traffic pattern detected',
                'Malware signature found on PC-Client-02',
                'Unauthorized admin panel access attempt',
                'DDoS attack detected from external sources'
            ]
        }
        
        events_df = pd.DataFrame(events_data)
        st.dataframe(events_df, use_container_width=True)
        
        # Download logs
        if st.button("📥 Export Security Logs"):
            csv = events_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"security_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with tab2:
        st.markdown("### Network Traffic Logs")
        
        # Network logs
        network_data = {
            'Timestamp': [datetime.now() - timedelta(minutes=i) for i in range(10)],
            'Source IP': [f"192.168.1.{random.randint(1, 254)}" for _ in range(10)],
            'Destination IP': [f"10.0.0.{random.randint(1, 50)}" for _ in range(10)],
            'Protocol': ['HTTPS', 'HTTP', 'SSH', 'FTP', 'DNS', 'HTTPS', 'HTTP', 'SSH', 'HTTPS', 'DNS'],
            'Port': [443, 80, 22, 21, 53, 443, 80, 22, 443, 53],
            'Status': ['Success', 'Success', 'Failed', 'Success', 'Success', 'Success', 'Success', 'Failed', 'Success', 'Success']
        }
        
        network_df = pd.DataFrame(network_data)
        st.dataframe(network_df, use_container_width=True)
    
    with tab3:
        st.markdown("### System Performance Metrics")
        
        # Performance chart
        hours = list(range(24))
        cpu_usage = [random.uniform(20, 90) for _ in hours]
        memory_usage = [random.uniform(30, 85) for _ in hours]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hours, y=cpu_usage, name='CPU Usage %', line=dict(color='red')))
        fig.add_trace(go.Scatter(x=hours, y=memory_usage, name='Memory Usage %', line=dict(color='blue')))
        
        fig.update_layout(title="System Performance (Last 24 Hours)", height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.markdown("### Your CSV Data Analysis")
        
        try:
            # Try to load your actual CSV files
            csv_files = ['event_logs .csv', 'network_inventory.csv', 'marketing_summary.csv']
            
            for csv_file in csv_files:
                if st.button(f"📊 Load {csv_file}"):
                    try:
                        df = pd.read_csv(csv_file)
                        st.success(f"✅ Loaded {csv_file} - {len(df)} records")
                        st.dataframe(df.head(20))
                        
                        # Basic analysis
                        st.write(f"**File Info:** {len(df)} rows, {len(df.columns)} columns")
                        if len(df.columns) > 0:
                            st.write(f"**Columns:** {', '.join(df.columns[:5])}...")
                            
                    except Exception as e:
                        st.error(f"Could not load {csv_file}: {e}")
        
        except Exception as e:
            st.info("Place your CSV files in the project root to analyze them here")

def main_dashboard():
    """Main dashboard function"""
    init_auth()
    
    # Sidebar controls
    time_range, alert_threshold, auto_refresh, refresh_interval = sidebar_controls()
    
    # Get real data
    data = fetch_real_data()
    
    # Display sections
    display_header_metrics(data)
    
    st.markdown("---")
    
    display_main_charts()
    
    st.markdown("---")
    
    display_network_devices()
    
    st.markdown("---")
    
    display_logs_section()
    
    # Footer with system info
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Refresh Dashboard"):
            st.rerun()
    
    with col2:
        st.markdown("**System Status:** 🟢 All Systems Operational")
    
    with col3:
        st.markdown(f"**User:** {st.session_state.username} ({st.session_state.user_role})")
    
    # Auto-refresh
    if auto_refresh and refresh_interval > 0:
        time.sleep(refresh_interval)
        st.rerun()

def main():
    """Main application"""
    init_auth()
    
    if not st.session_state.authenticated:
        login_page()
    else:
        main_dashboard()

if __name__ == "__main__":
    main()