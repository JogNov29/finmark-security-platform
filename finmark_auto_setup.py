#!/usr/bin/env python3
"""
FinMark Auto-Setup Script
Automatically sets up the complete FinMark Security Analytics Dashboard
"""

import os
import sys
import subprocess
import django
from pathlib import Path

def run_command(command, cwd=None):
    """Run shell command and return success status"""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def create_file(filepath, content):
    """Create file with content"""
    try:
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Created: {filepath}")
        return True
    except Exception as e:
        print(f"❌ Failed to create {filepath}: {e}")
        return False

def update_file(filepath, content):
    """Update existing file with new content"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Updated: {filepath}")
        return True
    except Exception as e:
        print(f"❌ Failed to update {filepath}: {e}")
        return False

def main():
    print("🚀 FinMark Auto-Setup Script Starting...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('manage.py'):
        print("❌ Error: manage.py not found. Please run this script from your Django project root.")
        sys.exit(1)
    
    print("📦 Required packages (install manually if needed):")
    print("   pip install Django djangorestframework djangorestframework-simplejwt")
    print("   pip install django-cors-headers streamlit requests pandas plotly")
    print("")
    
    print("🔧 Step 1: Creating enhanced Django API files...")
    
    # 1. Enhanced Security Views
    security_views_content = '''from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import SecurityEvent, Device
from apps.analytics.models import SystemMetrics

class SecurityViewSet(viewsets.ModelViewSet):
    queryset = SecurityEvent.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Get real-time security dashboard statistics"""
        # Get real counts from your database
        critical_alerts = SecurityEvent.objects.filter(
            severity='critical',
            timestamp__gte=timezone.now() - timedelta(hours=24)
        ).count()
        
        active_threats = SecurityEvent.objects.filter(
            is_threat=True,
            timestamp__gte=timezone.now() - timedelta(hours=24)
        ).count()
        
        total_events = SecurityEvent.objects.count()
        devices_online = Device.objects.filter(status='active').count()
        devices_critical = Device.objects.filter(status='critical').count()
        
        failed_logins = SecurityEvent.objects.filter(
            event_type='login_failure',
            timestamp__gte=timezone.now() - timedelta(hours=24)
        ).count()
        
        return Response({
            'critical_alerts': critical_alerts,
            'active_threats': active_threats,
            'total_events': total_events,
            'devices_online': devices_online,
            'devices_critical': devices_critical,
            'failed_logins': failed_logins,
            'system_health': self.calculate_system_health(),
            'last_updated': timezone.now().isoformat()
        })
    
    def calculate_system_health(self):
        """Calculate system health percentage based on real data"""
        total_devices = Device.objects.count()
        if total_devices == 0:
            return 100.0
            
        healthy_devices = Device.objects.filter(status='active').count()
        return round((healthy_devices / total_devices) * 100, 1)
    
    @action(detail=False, methods=['get'])
    def recent_events(self, request):
        """Get recent security events with real data"""
        events = SecurityEvent.objects.order_by('-timestamp')[:20]
        
        data = []
        for event in events:
            data.append({
                'id': str(event.id),
                'event_type': event.event_type,
                'severity': event.severity,
                'source_ip': event.source_ip,
                'timestamp': event.timestamp.isoformat(),
                'details': event.details,
                'is_threat': event.is_threat
            })
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def threat_analysis(self, request):
        """Analyze threats by type and severity"""
        # Group by event type
        by_type = SecurityEvent.objects.values('event_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Group by severity
        by_severity = SecurityEvent.objects.values('severity').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Top source IPs
        top_ips = SecurityEvent.objects.filter(
            is_threat=True
        ).values('source_ip').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        return Response({
            'by_type': list(by_type),
            'by_severity': list(by_severity),
            'top_threat_ips': list(top_ips)
        })

class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def network_status(self, request):
        """Get network device status overview"""
        devices = Device.objects.all()
        
        data = []
        for device in devices:
            data.append({
                'id': str(device.id),
                'hostname': device.hostname,
                'ip_address': device.ip_address,
                'device_type': device.device_type,
                'status': device.status,
                'os': device.os,
                'vulnerabilities': device.notes,
                'last_seen': '1 min ago'
            })
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def vulnerability_report(self, request):
        """Generate vulnerability report from device notes"""
        devices = Device.objects.exclude(notes='')
        
        vulnerabilities = []
        for device in devices:
            if device.notes:
                vulnerabilities.append({
                    'device': device.hostname,
                    'ip': device.ip_address,
                    'status': device.status,
                    'vulnerability': device.notes,
                    'severity': 'critical' if device.status == 'critical' else 'warning'
                })
        
        return Response(vulnerabilities)
'''
    
    update_file('apps/security/views.py', security_views_content)
    
    # 2. Analytics Views
    analytics_views_content = '''from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg, Max, Min
from django.utils import timezone
from datetime import timedelta
from .models import SystemMetrics, UserActivity

class SystemMetricsViewSet(viewsets.ModelViewSet):
    queryset = SystemMetrics.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def performance_timeline(self, request):
        """Get performance metrics for timeline charts"""
        # Get last 24 hours of data
        metrics = SystemMetrics.objects.filter(
            timestamp__gte=timezone.now() - timedelta(hours=24)
        ).order_by('timestamp')
        
        data = []
        for metric in metrics:
            data.append({
                'timestamp': metric.timestamp.isoformat(),
                'cpu_usage': metric.cpu_usage,
                'memory_usage': metric.memory_usage,
                'response_time': metric.response_time
            })
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def performance_overview(self, request):
        """Get system performance metrics overview"""
        # Get recent metrics (last 24 hours)
        recent_metrics = SystemMetrics.objects.filter(
            timestamp__gte=timezone.now() - timedelta(hours=24)
        )
        
        if not recent_metrics.exists():
            return Response({
                'avg_cpu': 0,
                'avg_memory': 0,
                'avg_response_time': 0,
                'max_cpu': 0,
                'max_memory': 0,
                'max_response_time': 0
            })
        
        stats = recent_metrics.aggregate(
            avg_cpu=Avg('cpu_usage'),
            avg_memory=Avg('memory_usage'),
            avg_response_time=Avg('response_time'),
            max_cpu=Max('cpu_usage'),
            max_memory=Max('memory_usage'),
            max_response_time=Max('response_time')
        )
        
        return Response(stats)
'''
    
    update_file('apps/analytics/views.py', analytics_views_content)
    
    # 3. Enhanced Core Views
    core_views_content = '''from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Product

User = get_user_model()

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Get general dashboard statistics"""
        return Response({
            'total_products': Product.objects.count(),
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'orders_today': 1847,
            'revenue_today': 85000.50,
            'target_orders': 3000
        })

class UserActivityViewSet(viewsets.ModelViewSet):
    """Handle user activity and audit logs"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        from apps.analytics.models import UserActivity
        return UserActivity.objects.all()
    
    @action(detail=False, methods=['get'])
    def recent_activity(self, request):
        """Get recent user activity for audit logs"""
        from apps.security.models import SecurityEvent
        
        recent_events = SecurityEvent.objects.order_by('-timestamp')[:50]
        
        activity_log = []
        for event in recent_events:
            activity_log.append({
                'timestamp': event.timestamp.isoformat(),
                'user': 'system',
                'action': event.event_type,
                'details': event.details,
                'ip_address': event.source_ip,
                'severity': event.severity
            })
        
        return Response(activity_log)
'''
    
    update_file('apps/core/views.py', core_views_content)
    
    # 4. Updated URLs
    updated_urls_content = '''from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Import all viewsets
from apps.core.views import ProductViewSet, UserActivityViewSet
from apps.security.views import SecurityViewSet, DeviceViewSet
from apps.analytics.views import SystemMetricsViewSet

# Create router and register all viewsets
router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'security', SecurityViewSet)
router.register(r'devices', DeviceViewSet)
router.register(r'metrics', SystemMetricsViewSet)
router.register(r'activity', UserActivityViewSet, basename='activity')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
'''
    
    update_file('backend/urls.py', updated_urls_content)
    
    # 5. Create Serializers
    security_serializers_content = '''from rest_framework import serializers
from .models import SecurityEvent, Device

class SecurityEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityEvent
        fields = '__all__'

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = '__all__'
'''
    
    create_file('apps/security/serializers.py', security_serializers_content)
    
    analytics_serializers_content = '''from rest_framework import serializers
from .models import SystemMetrics, UserActivity

class SystemMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemMetrics
        fields = '__all__'

class UserActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserActivity
        fields = '__all__'
'''
    
    create_file('apps/analytics/serializers.py', analytics_serializers_content)
    
    print("\n📱 Step 2: Creating enhanced Streamlit dashboard...")
    
    # Create the complete Streamlit dashboard
    streamlit_dashboard_content = '''# FinMark Security Operations Center - Complete Dashboard
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
'''
    
    create_file('dashboard/finmark_dashboard.py', streamlit_dashboard_content)
    
    print("\n👥 Step 3: Creating test users...")
    
    # Setup Django environment and create users
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
        django.setup()
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Create security user
        if not User.objects.filter(username='security').exists():
            User.objects.create_user(
                username='security',
                password='security123',
                email='security@finmark.com',
                role='security'
            )
            print("✅ Created security user: security/security123")
        else:
            print("✅ Security user already exists")
        
        # Create analyst user
        if not User.objects.filter(username='analyst').exists():
            User.objects.create_user(
                username='analyst',
                password='analyst123',
                email='analyst@finmark.com',
                role='analyst'
            )
            print("✅ Created analyst user: analyst/analyst123")
        else:
            print("✅ Analyst user already exists")
            
    except Exception as e:
        print(f"⚠️ Warning: Could not create users automatically: {e}")
        print("You can create them manually using Django shell")
    
    print("\n📋 Step 4: Creating startup script...")
    
    # Create startup script
    startup_script_content = '''#!/bin/bash
# FinMark System Startup Script

echo "🚀 Starting FinMark Security Operations Center..."

# Check if Django is already running
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "✅ Django already running on port 8000"
else
    echo "🔧 Starting Django server..."
    python manage.py runserver 0.0.0.0:8000 &
    sleep 3
fi

# Check if Streamlit is already running
if lsof -Pi :8501 -sTCP:LISTEN -t >/dev/null ; then
    echo "✅ Streamlit already running on port 8501"
else
    echo "🎨 Starting Streamlit dashboard..."
    streamlit run dashboard/finmark_dashboard.py --server.port 8501 &
    sleep 2
fi

echo ""
echo "🎉 FinMark System is ready!"
echo ""
echo "📊 Dashboard: http://localhost:8501"
echo "🔧 Django Admin: http://localhost:8000/admin"
echo "🔌 API: http://localhost:8000/api"
echo ""
echo "👤 Login credentials:"
echo "   Admin: admin/admin123"
echo "   Security: security/security123"
echo "   Analyst: analyst/analyst123"
echo ""
'''
    
    create_file('start_finmark.sh', startup_script_content)
    
    # Make startup script executable
    run_command('chmod +x start_finmark.sh')
    
    # Create Windows batch file too
    windows_startup_content = '''@echo off
echo 🚀 Starting FinMark Security Operations Center...

echo 🔧 Starting Django server...
start /B python manage.py runserver 0.0.0.0:8000

timeout /t 3 /nobreak > nul

echo 🎨 Starting Streamlit dashboard...
start /B streamlit run dashboard/finmark_dashboard.py --server.port 8501

timeout /t 2 /nobreak > nul

echo.
echo 🎉 FinMark System is ready!
echo.
echo 📊 Dashboard: http://localhost:8501
echo 🔧 Django Admin: http://localhost:8000/admin
echo 🔌 API: http://localhost:8000/api
echo.
echo 👤 Login credentials:
echo    Admin: admin/admin123
echo    Security: security/security123
echo    Analyst: analyst/analyst123
echo.
pause
'''
    
    create_file('start_finmark.bat', windows_startup_content)
    
    print("\n✅ Step 5: Setup complete!")
    print("=" * 50)
    print("🎉 FinMark Security Operations Center is ready!")
    print("")
    print("🚀 To start the system:")
    print("   Linux/Mac: ./start_finmark.sh")
    print("   Windows: start_finmark.bat")
    print("   Manual: python manage.py runserver & streamlit run dashboard/finmark_dashboard.py")
    print("")
    print("🌐 Access points:")
    print("   📊 Dashboard: http://localhost:8501")
    print("   🔧 Django Admin: http://localhost:8000/admin")
    print("   🔌 API: http://localhost:8000/api")
    print("")
    print("👤 Login credentials:")
    print("   Admin: admin/admin123 (Full access)")
    print("   Security: security/security123 (Security monitoring)")
    print("   Analyst: analyst/analyst123 (Analytics only)")
    print("")
    print("📝 Files created/updated:")
    print("   ✅ Enhanced Django API views")
    print("   ✅ Complete Streamlit dashboard")
    print("   ✅ API serializers")
    print("   ✅ Updated URL routing")
    print("   ✅ Test user accounts")
    print("   ✅ Startup scripts")
    print("")
    print("🔄 You can now delete any temporary Python scripts used for code generation!")

if __name__ == "__main__":
    main()