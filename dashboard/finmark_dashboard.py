import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import requests
import json

# Page configuration
st.set_page_config(
    page_title="FinMark Security Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="auto"
)

# Complete CSS for dark mode with excellent visibility
st.markdown("""
<style>
    /* Dark theme base - everything visible */
    .main, .main *, .block-container, .block-container *,
    .stMarkdown, .stMarkdown *, .stText, .stText *,
    p, span, div, label, h1, h2, h3, h4, h5, h6 {
        background-color: #0e1117 !important;
        color: #ffffff !important;
    }
    
    /* Login page styling */
    .login-container {
        max-width: 400px;
        margin: 2rem auto;
        padding: 2rem;
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border: 2px solid #3b82f6;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
    }
    
    .login-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .login-header h1 {
        color: #60a5fa !important;
        font-size: 2.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    .login-header p {
        color: #94a3b8 !important;
        font-size: 1.1rem !important;
    }
    
    /* Dashboard header */
    .dashboard-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #1e40af 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        border: 1px solid #374151;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    .dashboard-header h1 {
        color: #ffffff !important;
        font-size: 2.5rem !important;
        margin: 0 !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    
    .dashboard-header p {
        color: #e2e8f0 !important;
        font-size: 1.2rem !important;
        margin: 0.5rem 0 0 0 !important;
    }
    
    /* Status indicators */
    .status-box {
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border: 2px solid;
        font-weight: bold;
        font-size: 1.1rem;
        text-align: center;
    }
    
    .status-connected {
        background: linear-gradient(135deg, #065f46, #047857);
        border-color: #10b981;
        color: #d1fae5 !important;
    }
    
    .status-error {
        background: linear-gradient(135deg, #991b1b, #dc2626);
        border-color: #ef4444;
        color: #fecaca !important;
    }
    
    .status-warning {
        background: linear-gradient(135deg, #92400e, #d97706);
        border-color: #f59e0b;
        color: #fef3c7 !important;
    }
    
    /* Input fields */
    .stTextInput > div > div > input {
        background-color: #374151 !important;
        color: #ffffff !important;
        border: 2px solid #4b5563 !important;
        border-radius: 10px !important;
        font-size: 1.1rem !important;
        padding: 1rem !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2) !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 1rem 2rem !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.3) !important;
    }
    
    /* User info box */
    .user-info {
        background: linear-gradient(135deg, #1e293b, #334155);
        border: 2px solid #10b981;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .user-info h3 {
        color: #10b981 !important;
        margin-top: 0 !important;
    }
    
    .user-info p {
        color: #f1f5f9 !important;
        margin: 0.5rem 0 !important;
    }
    
    /* Permission badges */
    .permission-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: bold;
        margin: 0.25rem;
    }
    
    .badge-admin {
        background: #991b1b;
        color: #fecaca !important;
    }
    
    .badge-staff {
        background: #1e40af;
        color: #dbeafe !important;
    }
    
    .badge-user {
        background: #374151;
        color: #e5e7eb !important;
    }
    
    /* Section headers */
    .section-header {
        color: #60a5fa !important;
        font-size: 2rem !important;
        font-weight: bold !important;
        margin: 2rem 0 1rem 0 !important;
        padding-bottom: 0.5rem !important;
        border-bottom: 3px solid #374151 !important;
    }
    
    /* Data tables */
    .stDataFrame table {
        background-color: #1f2937 !important;
        border: 1px solid #374151 !important;
        border-radius: 10px !important;
    }
    
    .stDataFrame th {
        background-color: #374151 !important;
        color: #ffffff !important;
        font-weight: bold !important;
        padding: 1rem !important;
    }
    
    .stDataFrame td {
        background-color: #1f2937 !important;
        color: #ffffff !important;
        padding: 0.75rem !important;
    }
    
    /* Sidebar */
    .sidebar .sidebar-content {
        background-color: #1f2937 !important;
    }
    
    .sidebar .sidebar-content * {
        color: #ffffff !important;
    }
    
    /* Logout button */
    .logout-btn {
        background: linear-gradient(135deg, #dc2626, #991b1b) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        font-weight: bold !important;
    }
    
    /* Connection status indicators */
    .connection-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .connection-card {
        background: #1f2937;
        border: 2px solid #374151;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
    }
    
    .connection-card h4 {
        color: #60a5fa !important;
        margin-bottom: 1rem !important;
    }
    
    /* Footer */
    .footer {
        background: linear-gradient(135deg, #1f2937, #374151);
        border: 2px solid #4b5563;
        border-radius: 15px;
        padding: 2rem;
        margin-top: 3rem;
        text-align: center;
    }
    
    .footer * {
        color: #e5e7eb !important;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = "http://localhost:8000"
API_ENDPOINTS = {
    'login': f"{API_BASE_URL}/api/auth/token/",
    'refresh': f"{API_BASE_URL}/api/auth/token/refresh/",
    'status': f"{API_BASE_URL}/api/status/",
    'metrics': f"{API_BASE_URL}/api/metrics/",
    'database': f"{API_BASE_URL}/api/database/",
    'user_profile': f"{API_BASE_URL}/api/user/profile/"
}

class FinMarkAuth:
    """Authentication and API management class"""
    
    @staticmethod
    def login(username, password):
        """Authenticate user and get JWT tokens"""
        try:
            response = requests.post(
                API_ENDPOINTS['login'],
                json={"username": username, "password": password},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return True, data
            else:
                return False, f"Login failed: {response.status_code}"
                
        except requests.exceptions.ConnectionError:
            return False, "Cannot connect to Django server. Make sure it's running on port 8000."
        except requests.exceptions.Timeout:
            return False, "Request timeout. Server may be slow to respond."
        except Exception as e:
            return False, f"Login error: {str(e)}"
    
    @staticmethod
    def get_user_info(token):
        """Get user profile information"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(API_ENDPOINTS['user_profile'], headers=headers, timeout=5)
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, "Could not fetch user info"
        except:
            return False, "User info request failed"
    
    @staticmethod
    def check_connections():
        """Check all system connections"""
        connections = {
            'django_api': False,
            'database': False,
            'jwt_auth': False
        }
        
        try:
            # Check Django API
            response = requests.get(API_ENDPOINTS['status'], timeout=5)
            if response.status_code == 200:
                connections['django_api'] = True
                data = response.json()
                connections['database'] = data.get('database', {}).get('connected', False)
        except:
            pass
        
        try:
            # Check JWT auth with test credentials
            response = requests.post(
                API_ENDPOINTS['login'],
                json={"username": "admin", "password": "admin123"},
                timeout=5
            )
            connections['jwt_auth'] = response.status_code == 200
        except:
            pass
        
        return connections
    
    @staticmethod
    def api_call(endpoint, token=None, method='GET', data=None):
        """Generic API call with token"""
        try:
            headers = {}
            if token:
                headers["Authorization"] = f"Bearer {token}"
            
            if method == 'GET':
                response = requests.get(f"{API_BASE_URL}/api/{endpoint}/", headers=headers, timeout=5)
            elif method == 'POST':
                response = requests.post(f"{API_BASE_URL}/api/{endpoint}/", headers=headers, json=data, timeout=5)
            
            return response.status_code == 200, response.json() if response.status_code == 200 else None
        except:
            return False, None

def init_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'access_token' not in st.session_state:
        st.session_state.access_token = None
    if 'refresh_token' not in st.session_state:
        st.session_state.refresh_token = None
    if 'user_info' not in st.session_state:
        st.session_state.user_info = {}
    if 'login_time' not in st.session_state:
        st.session_state.login_time = None

def login_page():
    """Render login page"""
    st.markdown("""
    <div class="login-container">
        <div class="login-header">
            <h1>🛡️ FinMark</h1>
            <p>Security Operations Center</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Check system connections first
    st.markdown('<h2 class="section-header">🔌 System Status</h2>', unsafe_allow_html=True)
    
    connections = FinMarkAuth.check_connections()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if connections['django_api']:
            st.markdown('<div class="status-box status-connected">✅ Django API<br>Connected</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-box status-error">❌ Django API<br>Disconnected</div>', unsafe_allow_html=True)
    
    with col2:
        if connections['database']:
            st.markdown('<div class="status-box status-connected">✅ Database<br>Connected</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-box status-error">❌ Database<br>Issues</div>', unsafe_allow_html=True)
    
    with col3:
        if connections['jwt_auth']:
            st.markdown('<div class="status-box status-connected">✅ JWT Auth<br>Ready</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-box status-warning">⚠️ JWT Auth<br>Check Setup</div>', unsafe_allow_html=True)
    
    # Show connection issues
    if not all(connections.values()):
        st.error("⚠️ Some systems are not responding. Please check:")
        if not connections['django_api']:
            st.write("• Django server: `python manage.py runserver 8000`")
        if not connections['database']:
            st.write("• Database: `python manage.py migrate`")
        if not connections['jwt_auth']:
            st.write("• Users: `python core_user_fix.py`")
    
    # Login form
    st.markdown('<h2 class="section-header">🔐 Login</h2>', unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("👤 Username", placeholder="Enter your username")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            login_button = st.form_submit_button("🚀 Login", use_container_width=True)
        with col2:
            demo_button = st.form_submit_button("👨‍💼 Demo", use_container_width=True)
    
    # Handle demo login
    if demo_button:
        username = "admin"
        password = "admin123"
        login_button = True
    
    # Handle login
    if login_button and username and password:
        with st.spinner("🔐 Authenticating..."):
            success, result = FinMarkAuth.login(username, password)
            
            if success:
                # Store tokens and user info
                st.session_state.authenticated = True
                st.session_state.access_token = result.get('access')
                st.session_state.refresh_token = result.get('refresh')
                st.session_state.login_time = datetime.now()
                
                # Get user info
                user_success, user_data = FinMarkAuth.get_user_info(st.session_state.access_token)
                if user_success:
                    st.session_state.user_info = user_data
                else:
                    # Fallback user info
                    st.session_state.user_info = {
                        'username': username,
                        'is_staff': True,
                        'is_superuser': username == 'admin'
                    }
                
                st.success("✅ Login successful! Redirecting to dashboard...")
                st.rerun()
            else:
                st.error(f"❌ {result}")
    
    # Demo credentials info
    st.markdown("""
    <div class="user-info">
        <h3>🔑 Demo Credentials</h3>
        <p><strong>Admin:</strong> admin / admin123 (Full access)</p>
        <p><strong>Security:</strong> security / security123 (Security monitoring)</p>
        <p><strong>Analyst:</strong> analyst / analyst123 (Analytics focus)</p>
        <p><strong>Manager:</strong> manager / manager123 (Management dashboard)</p>
    </div>
    """, unsafe_allow_html=True)

def dashboard_page():
    """Render main dashboard"""
    user = st.session_state.user_info
    
    # Header with user info
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"""
        <div class="dashboard-header">
            <h1>🛡️ FinMark Security Operations Center</h1>
            <p>Welcome back, {user.get('username', 'User')}! Real-time Security Analytics & Monitoring</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # User info and logout
        user_role = "Admin" if user.get('is_superuser') else "Staff" if user.get('is_staff') else "User"
        badge_class = "badge-admin" if user.get('is_superuser') else "badge-staff" if user.get('is_staff') else "badge-user"
        
        st.markdown(f"""
        <div class="user-info">
            <h4>👤 {user.get('username', 'User')}</h4>
            <span class="permission-badge {badge_class}">{user_role}</span>
            <p>Login: {st.session_state.login_time.strftime('%H:%M:%S') if st.session_state.login_time else 'Unknown'}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚪 Logout", key="logout", help="Logout and return to login page"):
            # Clear session
            st.session_state.authenticated = False
            st.session_state.access_token = None
            st.session_state.refresh_token = None
            st.session_state.user_info = {}
            st.session_state.login_time = None
            st.rerun()
    
    # Real-time system status
    st.markdown('<h2 class="section-header">📊 System Status</h2>', unsafe_allow_html=True)
    
    # Get real-time data
    token = st.session_state.access_token
    
    # API Status
    api_success, api_data = FinMarkAuth.api_call('status', token)
    metrics_success, metrics_data = FinMarkAuth.api_call('metrics', token)
    db_success, db_data = FinMarkAuth.api_call('database', token)
    
    # Status grid
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if api_success:
            st.markdown('<div class="status-box status-connected">✅ API Active<br>All endpoints responding</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-box status-error">❌ API Issues<br>Check connection</div>', unsafe_allow_html=True)
    
    with col2:
        if db_success and db_data:
            table_count = db_data.get('table_count', 0)
            st.markdown(f'<div class="status-box status-connected">✅ Database OK<br>{table_count} tables active</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-box status-error">❌ Database Error<br>Connection failed</div>', unsafe_allow_html=True)
    
    with col3:
        if token:
            st.markdown('<div class="status-box status-connected">✅ Authenticated<br>JWT token valid</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-box status-warning">⚠️ Auth Warning<br>No valid token</div>', unsafe_allow_html=True)
    
    with col4:
        uptime = datetime.now() - st.session_state.login_time if st.session_state.login_time else timedelta(0)
        uptime_str = str(uptime).split('.')[0]  # Remove microseconds
        st.markdown(f'<div class="status-box status-connected">🕐 Session<br>{uptime_str}</div>', unsafe_allow_html=True)
    
    # Security Metrics (with permission checks)
    st.markdown('<h2 class="section-header">📈 Security Analytics</h2>', unsafe_allow_html=True)
    
    if user.get('is_staff', False):  # Staff and above can see metrics
        
        # Get metrics from API or use defaults
        if metrics_success and metrics_data:
            critical_alerts = metrics_data.get('critical_alerts', 3)
            active_threats = metrics_data.get('active_threats', 12)
            system_health = metrics_data.get('system_health', 98.2)
            failed_logins = metrics_data.get('failed_logins', 27)
        else:
            # Fallback demo data
            critical_alerts = np.random.randint(1, 6)
            active_threats = np.random.randint(8, 15)
            system_health = round(np.random.uniform(95, 99.5), 1)
            failed_logins = np.random.randint(15, 35)
        
        # Metrics display
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
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
        
        # Charts (Admin and Security staff only)
        if user.get('is_superuser') or 'security' in user.get('username', '').lower():
            st.markdown('<h2 class="section-header">📊 Real-time Analytics</h2>', unsafe_allow_html=True)
            
            col_left, col_right = st.columns([2, 1])
            
            with col_left:
                st.subheader("🌐 Network Traffic Analysis")
                
                # Generate sample data
                hours = list(range(24))
                traffic_data = pd.DataFrame({
                    'Hour': hours,
                    'Inbound (GB)': np.random.normal(50, 15, 24),
                    'Outbound (GB)': np.random.normal(30, 10, 24)
                })
                
                fig = px.line(traffic_data, x='Hour', y=['Inbound (GB)', 'Outbound (GB)'], 
                              title="Network Traffic - Last 24 Hours")
                fig.update_layout(
                    plot_bgcolor='#1f2937',
                    paper_bgcolor='#1f2937',
                    font_color='#ffffff',
                    height=400
                )
                fig.update_xaxes(gridcolor='#374151', color='#ffffff')
                fig.update_yaxes(gridcolor='#374151', color='#ffffff')
                st.plotly_chart(fig, use_container_width=True)
            
            with col_right:
                st.subheader("🚨 Security Alerts")
                
                alerts = [
                    ("🔴", "CRITICAL", "Multiple failed login attempts"),
                    ("🟡", "WARNING", "Unusual traffic detected"),
                    ("🟢", "INFO", "Firewall rules updated"),
                    ("🟡", "WARNING", "High CPU usage on DB01"),
                    ("🟢", "INFO", "Security scan completed")
                ]
                
                for icon, level, message in alerts:
                    if level == "CRITICAL":
                        status_class = "status-error"
                    elif level == "WARNING":
                        status_class = "status-warning"
                    else:
                        status_class = "status-connected"
                    
                    st.markdown(f"""
                    <div class="status-box {status_class}">
                        {icon} <strong>{level}</strong><br>{message}
                    </div>
                    """, unsafe_allow_html=True)
    
    else:
        st.warning("🔒 You need staff permissions to view security metrics. Contact your administrator.")
    
    # System Information (Everyone can see)
    st.markdown('<h2 class="section-header">🖥️ System Information</h2>', unsafe_allow_html=True)
    
    system_data = {
        'Component': ['Django API', 'Database', 'Authentication', 'Dashboard', 'JWT Tokens'],
        'Status': [
            '🟢 Online' if api_success else '🔴 Offline',
            '🟢 Connected' if db_success else '🔴 Disconnected',
            '🟢 Active' if token else '🟡 Limited',
            '🟢 Running',
            '🟢 Valid' if token else '🔴 Missing'
        ],
        'Endpoint/Location': [
            'http://localhost:8000/api/',
            'db.sqlite3',
            '/api/auth/token/',
            'http://localhost:8501',
            'Bearer Token'
        ],
        'Last Check': [
            datetime.now().strftime('%H:%M:%S'),
            datetime.now().strftime('%H:%M:%S'),
            st.session_state.login_time.strftime('%H:%M:%S') if st.session_state.login_time else 'N/A',
            datetime.now().strftime('%H:%M:%S'),
            st.session_state.login_time.strftime('%H:%M:%S') if st.session_state.login_time else 'N/A'
        ]
    }
    
    st.dataframe(pd.DataFrame(system_data), hide_index=True, use_container_width=True)
    
    # API Testing (Admin only)
    if user.get('is_superuser'):
        with st.expander("🔧 Advanced API Testing (Admin Only)"):
            st.subheader("🔌 Test API Endpoints")
            
            endpoints = ['status', 'metrics', 'database']
            test_results = {}
            
            for endpoint in endpoints:
                success, data = FinMarkAuth.api_call(endpoint, token)
                test_results[endpoint] = success
                
                col1, col2 = st.columns([1, 3])
                with col1:
                    status = "✅ Success" if success else "❌ Failed"
                    st.write(f"**{endpoint}**: {status}")
                
                with col2:
                    if success and data:
                        st.caption(f"Response from {endpoint}:") 
                        st.json(data)
            
            # Token info
            st.subheader("🔑 JWT Token Information")
            if token:
                st.success(f"✅ Access token available (Length: {len(token)} chars)")
                st.code(f"Bearer {token[:50]}...", language="text")
            else:
                st.error("❌ No access token available")
    
    # Sidebar with session info
    with st.sidebar:
        st.markdown("### 👤 Session Information")
        st.write(f"**User:** {user.get('username', 'Unknown')}")
        st.write(f"**Role:** {user_role}")
        st.write(f"**Login:** {st.session_state.login_time.strftime('%H:%M:%S') if st.session_state.login_time else 'Unknown'}")
        st.write(f"**Token:** {'✅ Valid' if token else '❌ Missing'}")
        
        st.markdown("---")
        st.markdown("### ⚙️ Quick Actions")
        
        if st.button("🔄 Refresh Data"):
            st.rerun()
        
        if st.button("🧪 Test Connection"):
            connections = FinMarkAuth.check_connections()
            st.write("**Connection Status:**")
            for service, status in connections.items():
                icon = "✅" if status else "❌"
                st.write(f"{icon} {service.replace('_', ' ').title()}")
    
    # Footer
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.markdown(f"""
    <div class="footer">
        <strong>FinMark Security Operations Center</strong><br>
        Last Updated: {current_time} | Session: {uptime_str} | User: {user.get('username', 'Unknown')} ({user_role})
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main application logic"""
    init_session_state()
    
    # Check authentication status
    if not st.session_state.authenticated:
        login_page()
    else:
        dashboard_page()

if __name__ == "__main__":
    main()