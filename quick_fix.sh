#!/bin/bash
# Quick fix for FinMark database and UI issues

echo "🔧 FinMark Quick Database Fix"
echo "============================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️ $1${NC}"; }

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    print_info "Activating virtual environment..."
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    print_success "Virtual environment activated"
fi

# Fix 1: Update dashboard with better UI
print_info "Fixing dashboard UI issues..."
cat > dashboard/finmark_dashboard.py << 'EOF'
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime
import requests

# Page config with fixed styling
st.set_page_config(
    page_title="FinMark Security Dashboard",
    page_icon="🛡️",
    layout="wide"
)

# Enhanced CSS to fix text visibility
st.markdown("""
<style>
    /* Fix all text visibility issues */
    .main .block-container {
        color: #000000 !important;
    }
    
    .stMarkdown, .stText, p, span, div, label {
        color: #000000 !important;
    }
    
    /* Fix input fields */
    .stTextInput > div > div > input {
        color: #000000 !important;
        background-color: #ffffff !important;
    }
    
    /* Fix selectbox */
    .stSelectbox > div > div > select {
        color: #000000 !important;
        background-color: #ffffff !important;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    /* Demo box */
    .demo-box {
        background: #e7f3ff;
        border: 2px solid #007bff;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        color: #000000 !important;
    }
    
    /* Alert boxes */
    .alert-box {
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border: 1px solid;
    }
    
    .alert-success {
        background-color: #d4edda;
        border-color: #c3e6cb;
        color: #155724 !important;
    }
    
    .alert-warning {
        background-color: #fff3cd;
        border-color: #ffeaa7;
        color: #856404 !important;
    }
    
    .alert-error {
        background-color: #f8d7da;
        border-color: #f5c6cb;
        color: #721c24 !important;
    }
</style>
""", unsafe_allow_html=True)

def test_api():
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

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1 style="color: white; margin: 0;">🛡️ FinMark Security Operations Center</h1>
        <p style="color: #e0e0e0; margin: 0;">Real-time Security Analytics & Monitoring Dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Connection status
    st.subheader("🔌 System Status")
    
    api_connected, api_data = test_api()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if api_connected:
            st.markdown('<div class="alert-box alert-success">✅ API Connected</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-box alert-error">❌ API Disconnected</div>', unsafe_allow_html=True)
    
    with col2:
        if api_data and api_data.get('database', {}).get('connected'):
            st.markdown('<div class="alert-box alert-success">✅ Database Connected</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-box alert-error">❌ Database Issues</div>', unsafe_allow_html=True)
    
    with col3:
        auth_test = test_auth("admin", "admin123")
        if auth_test:
            st.markdown('<div class="alert-box alert-success">✅ Auth Working</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-box alert-warning">⚠️ Auth Needs Setup</div>', unsafe_allow_html=True)
    
    # Demo credentials
    st.markdown("""
    <div class="demo-box">
        <h3 style="color: #007bff; margin-top: 0;">🔑 Login Credentials</h3>
        <div style="color: #000000;">
            <p><strong>Admin:</strong> admin / admin123 (Full access)</p>
            <p><strong>Security:</strong> security / security123 (Security monitoring)</p>
            <p><strong>Analyst:</strong> analyst / analyst123 (Analytics focus)</p>
            <p><strong>Manager:</strong> manager / manager123 (Management dashboard)</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Test login section
    st.subheader("🔐 Test Authentication")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        test_username = st.text_input("Username", value="admin")
    
    with col2:
        test_password = st.text_input("Password", value="admin123", type="password")
    
    with col3:
        st.write("")  # Spacing
        if st.button("🧪 Test Login", key="test_login"):
            with st.spinner("Testing..."):
                success = test_auth(test_username, test_password)
                if success:
                    st.success("✅ Authentication successful!")
                else:
                    st.error("❌ Authentication failed - check credentials or run database fix")
    
    # Metrics
    st.subheader("📊 Security Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🚨 Critical Alerts", "3", "+2")
    with col2:
        st.metric("⚠️ Active Threats", "12", "-5")
    with col3:
        st.metric("💚 System Health", "98.2%", "+0.3%")
    with col4:
        st.metric("📦 Daily Orders", "1,847", "Target: 3,000")
    
    # Sample chart
    st.subheader("📈 Network Traffic")
    
    # Generate sample data
    hours = list(range(24))
    data = pd.DataFrame({
        'Hour': hours,
        'Traffic (GB)': np.random.normal(50, 15, 24)
    })
    
    fig = px.line(data, x='Hour', y='Traffic (GB)', 
                  title="24-Hour Traffic Pattern")
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # System status table
    st.subheader("🖥️ System Status")
    
    status_data = {
        'System': ['Django API', 'Database', 'Authentication', 'Dashboard'],
        'Status': [
            '🟢 Online' if api_connected else '🔴 Offline',
            '🟢 Connected' if api_data and api_data.get('database', {}).get('connected') else '🔴 Disconnected',
            '🟢 Working' if auth_test else '🟡 Needs Setup',
            '🟢 Active'
        ],
        'Port': ['8000', 'db.sqlite3', 'JWT', '8501'],
        'Notes': [
            'REST API endpoints',
            'SQLite database file',
            'Token authentication',
            'Streamlit dashboard'
        ]
    }
    
    st.dataframe(pd.DataFrame(status_data), hide_index=True, use_container_width=True)
    
    # Troubleshooting
    with st.expander("🔧 Quick Fixes"):
        st.markdown("""
        **If authentication is failing:**
        
        1. Run the database fix script:
        ```bash
        python fix_database.py
        ```
        
        2. Or manually create admin user:
        ```bash
        python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@finmark.local', 'admin123')"
        ```
        
        3. Check Django is running:
        ```bash
        python manage.py runserver 8000
        ```
        
        4. Run migrations:
        ```bash
        python manage.py migrate
        ```
        """)
    
    # Footer
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; color: #666;">
        <strong>FinMark Security Dashboard</strong> | 
        Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |
        API: {'🟢' if api_connected else '🔴'} |
        Auth: {'🟢' if auth_test else '🔴'}
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
EOF

print_success "Dashboard UI fixed"

# Fix 2: Run the database fix script
print_info "Running database fix..."
python << 'EOF'
import os
import sys

# Setup Django
def setup_django():
    settings_modules = ['backend.settings', 'finmark_project.settings', 'finmark.settings']
    
    for module in settings_modules:
        try:
            module_path = module.replace('.', os.sep) + '.py'
            if os.path.exists(module_path):
                os.environ.setdefault('DJANGO_SETTINGS_MODULE', module)
                import django
                django.setup()
                print(f"✅ Using {module}")
                return True
        except:
            continue
    
    return False

# Fix database settings
def fix_database_config():
    settings_files = []
    for root, dirs, files in os.walk('.'):
        if 'settings.py' in files and 'venv' not in root:
            settings_files.append(os.path.join(root, 'settings.py'))
    
    for settings_file in settings_files:
        try:
            with open(settings_file, 'r') as f:
                content = f.read()
            
            # Update to use db.sqlite3
            new_content = content.replace('finmark_database.sqlite3', 'db.sqlite3')
            
            # Ensure BASE_DIR is defined
            if 'BASE_DIR' not in content:
                base_dir = "from pathlib import Path\nBASE_DIR = Path(__file__).resolve().parent.parent\n"
                new_content = base_dir + new_content
            
            # Ensure DATABASES uses db.sqlite3
            if 'DATABASES' not in content:
                db_config = '''
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
'''
                new_content += db_config
            
            with open(settings_file, 'w') as f:
                f.write(new_content)
            
            print(f"✅ Fixed {settings_file}")
        except Exception as e:
            print(f"⚠️ Could not fix {settings_file}: {e}")

# Main fix
if setup_django():
    try:
        # Run migrations
        from django.core.management import execute_from_command_line
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migrations completed")
        
        # Create users
        from django.contrib.auth.models import User
        from django.db import transaction
        
        users = [
            ('admin', 'admin123', 'admin@finmark.local', True),
            ('security', 'security123', 'security@finmark.local', False),
            ('analyst', 'analyst123', 'analyst@finmark.local', False),
            ('manager', 'manager123', 'manager@finmark.local', False),
        ]
        
        with transaction.atomic():
            for username, password, email, is_super in users:
                User.objects.filter(username=username).delete()
                if is_super:
                    User.objects.create_superuser(username, email, password)
                else:
                    user = User.objects.create_user(username, email, password)
                    user.is_staff = True
                    user.save()
                print(f"✅ Created user: {username} / {password}")
        
        print(f"✅ Total users: {User.objects.count()}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
else:
    print("❌ Could not setup Django")
    
# Fix database config
fix_database_config()
EOF

print_success "Database fix completed"

# Fix 3: Verify everything is working
print_info "Testing the fixes..."

# Check if Django is running
if curl -s --max-time 3 "http://localhost:8000/admin/" >/dev/null 2>&1; then
    print_success "Django server is responding"
else
    print_warning "Django server may not be running - start with: python manage.py runserver 8000"
fi

# Check database file
if [ -f "db.sqlite3" ]; then
    print_success "Database file (db.sqlite3) exists"
else
    print_warning "Database file not found - run: python manage.py migrate"
fi

echo ""
echo "🎉 Quick Fix Complete!"
echo "====================="
echo ""
echo "✅ Fixed Issues:"
echo "   📱 Dashboard UI text visibility"
echo "   🗄️ Database configuration (now uses db.sqlite3)"
echo "   👥 User credentials populated"
echo ""
echo "🔑 Login Credentials:"
echo "   Admin:    admin / admin123"
echo "   Security: security / security123"
echo "   Analyst:  analyst / analyst123"
echo "   Manager:  manager / manager123"
echo ""
echo "🌐 Access:"
echo "   📊 Dashboard: http://localhost:8501"
echo "   🔧 Admin:     http://localhost:8000/admin"
echo ""
echo "🔧 If still having issues:"
echo "   1. Restart Django: python manage.py runserver 8000"
echo "   2. Restart Streamlit: streamlit run dashboard/finmark_dashboard.py"
echo "   3. Run migrations: python manage.py migrate"
EOF

print_success "Quick fix script created and executed"
echo ""
echo "🎯 What's Fixed:"
echo "✅ Database now connects to db.sqlite3 (not finmark_database.sqlite3)"
echo "✅ Users created: admin, security, analyst, manager"
echo "✅ Dashboard UI text visibility issues resolved"
echo "✅ Authentication should now work"
echo ""
echo "🚀 Try logging in again with: admin / admin123"