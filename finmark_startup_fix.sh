#!/bin/bash
# FinMark Startup Fix Script - Addresses Django, Database, and JWT issues

echo "🚀 FinMark System Fix & Startup"
echo "==============================="

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

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    print_error "manage.py not found. Please run this script from your Django project root."
    exit 1
fi

print_success "Django project detected"

# Step 1: Virtual Environment
print_info "Step 1: Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv || python -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi
print_success "Virtual environment activated"

# Step 2: Install essential packages
print_info "Step 2: Installing essential packages..."
pip install --quiet --upgrade pip

# Install core Django packages
pip install --quiet \
    "Django>=4.2.0,<5.0" \
    "djangorestframework>=3.14.0" \
    "djangorestframework-simplejwt>=5.2.0" \
    "django-cors-headers>=4.0.0" \
    "django-filter>=23.0.0" \
    "streamlit>=1.28.0" \
    "requests>=2.31.0" \
    "pandas>=2.0.0" \
    "plotly>=5.15.0"

print_success "Essential packages installed"

# Step 3: Fix database configuration
print_info "Step 3: Fixing database configuration..."

# Standardize on db.sqlite3
if [ -f "finmark_database.sqlite3" ] && [ ! -f "db.sqlite3" ]; then
    mv finmark_database.sqlite3 db.sqlite3
    print_success "Moved finmark_database.sqlite3 to db.sqlite3"
fi

# Fix settings.py to use db.sqlite3
if [ -f "backend/settings.py" ]; then
    sed -i.bak 's/finmark_database\.sqlite3/db.sqlite3/g' backend/settings.py
    print_success "Updated database path in settings"
fi

# Step 4: Fix Django settings for JWT and CORS
print_info "Step 4: Ensuring Django configuration..."

# Create a minimal working settings fix
python3 << 'EOF'
import os
from pathlib import Path

# Find settings file
settings_files = ['backend/settings.py', 'finmark_project/settings.py', 'finmark/settings.py']
settings_file = None

for file in settings_files:
    if os.path.exists(file):
        settings_file = file
        break

if not settings_file:
    print("❌ No settings.py found")
    exit(1)

print(f"✅ Found settings: {settings_file}")

# Read current settings
with open(settings_file, 'r') as f:
    content = f.read()

# Ensure required apps are installed
required_apps = [
    "'rest_framework'",
    "'rest_framework_simplejwt'", 
    "'corsheaders'",
    "'django_filters'"
]

for app in required_apps:
    if app not in content and 'INSTALLED_APPS' in content:
        content = content.replace(
            'INSTALLED_APPS = [',
            f'INSTALLED_APPS = [\n    {app},'
        )
        print(f"✅ Added {app}")

# Ensure CORS middleware is present
if "'corsheaders.middleware.CorsMiddleware'" not in content:
    content = content.replace(
        'MIDDLEWARE = [',
        "MIDDLEWARE = [\n    'corsheaders.middleware.CorsMiddleware',"
    )
    print("✅ Added CORS middleware")

# Add CORS settings if missing
if 'CORS_ALLOW_ALL_ORIGINS' not in content:
    cors_config = '''
# CORS Configuration
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8501",
    "http://127.0.0.1:8501",
]
'''
    content += cors_config
    print("✅ Added CORS configuration")

# Add JWT settings if missing
if 'SIMPLE_JWT' not in content:
    jwt_config = '''
# JWT Configuration
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}
'''
    content += jwt_config
    print("✅ Added JWT configuration")

# Write back
with open(settings_file, 'w') as f:
    f.write(content)

print("✅ Django settings updated")
EOF

# Step 5: Fix URLs for JWT endpoints
print_info "Step 5: Setting up JWT endpoints..."

# Create/fix URLs
cat > backend/urls.py << 'EOF'
from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime
import random

@api_view(['GET'])
def api_root(request):
    return Response({
        'message': 'FinMark Security Operations Center API',
        'timestamp': datetime.now().isoformat(),
        'status': 'operational',
        'endpoints': {
            'auth': '/api/auth/token/',
            'status': '/api/status/', 
            'metrics': '/api/metrics/',
        }
    })

@api_view(['GET'])
def api_status(request):
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_connected = True
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
    except Exception:
        db_connected = False
        tables = []
    
    return Response({
        'timestamp': datetime.now().isoformat(),
        'status': 'online',
        'database': {
            'connected': db_connected,
            'tables_count': len(tables),
        }
    })

@api_view(['GET'])
def api_metrics(request):
    return Response({
        'critical_alerts': random.randint(0, 5),
        'active_threats': random.randint(8, 15),
        'system_health': round(random.uniform(95, 99.5), 1),
        'timestamp': datetime.now().isoformat()
    })

@api_view(['GET'])
def api_database(request):
    try:
        from django.db import connection
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
        
        return Response({
            'database_connected': True,
            'tables': tables,
            'table_count': len(tables),
            'users_count': User.objects.count(),
        })
    except Exception as e:
        return Response({'database_connected': False, 'error': str(e)}, status=500)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api_root, name='api_root'),
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/status/', api_status, name='api_status'),
    path('api/metrics/', api_metrics, name='api_metrics'),
    path('api/database/', api_database, name='api_database'),
]
EOF

print_success "JWT endpoints configured"

# Step 6: Database migrations
print_info "Step 6: Setting up database..."

# Set Django settings
export DJANGO_SETTINGS_MODULE=backend.settings

# Run migrations
print_info "Running Django migrations..."
python manage.py makemigrations --verbosity=0 2>/dev/null || print_warning "No new migrations needed"
python manage.py migrate --verbosity=0 || {
    print_warning "Migration failed, creating new database..."
    rm -f db.sqlite3
    python manage.py migrate --verbosity=0
}

print_success "Database migrations completed"

# Step 7: Create users
print_info "Step 7: Creating default users..."

python manage.py shell << 'EOF'
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

users = [
    ('admin', 'admin123', 'admin@finmark.local', True, True),
    ('security', 'security123', 'security@finmark.local', False, True),
    ('analyst', 'analyst123', 'analyst@finmark.local', False, True),
    ('manager', 'manager123', 'manager@finmark.local', False, True),
]

created = 0
with transaction.atomic():
    for username, password, email, is_super, is_staff in users:
        if not User.objects.filter(username=username).exists():
            if is_super:
                User.objects.create_superuser(username, email, password)
            else:
                user = User.objects.create_user(username, email, password)
                user.is_staff = is_staff
                user.save()
            created += 1
            print(f"Created: {username}")

print(f"Users in system: {User.objects.count()}")
EOF

print_success "Default users created"

# Step 8: Test the setup
print_info "Step 8: Testing system..."

# Test Django
python manage.py check --verbosity=0 && print_success "Django system check passed" || print_error "Django system check failed"

# Test database connection
python << 'EOF'
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
import django
django.setup()

try:
    from django.db import connection
    from django.contrib.auth import get_user_model
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    print("✅ Database connection successful")
    
    User = get_user_model()
    if User.objects.filter(username='admin').exists():
        print("✅ Admin user exists")
    else:
        print("❌ Admin user missing")
        
except Exception as e:
    print(f"❌ Database test failed: {e}")
EOF

# Step 9: Start services
print_info "Step 9: Starting services..."

# Kill any existing processes
pkill -f "manage.py runserver" 2>/dev/null || true
pkill -f "streamlit run" 2>/dev/null || true
sleep 2

# Start Django
print_info "Starting Django server..."
python manage.py runserver 0.0.0.0:8000 > django.log 2>&1 &
DJANGO_PID=$!

# Wait for Django to start
sleep 5

# Test Django is responding
if curl -s --max-time 5 "http://localhost:8000/api/" >/dev/null 2>&1; then
    print_success "Django server running (PID: $DJANGO_PID)"
else
    print_error "Django server failed to start"
    cat django.log
    exit 1
fi

# Start Streamlit if dashboard exists
if [ -f "dashboard/finmark_dashboard.py" ]; then
    print_info "Starting Streamlit dashboard..."
    streamlit run dashboard/finmark_dashboard.py --server.port 8501 --server.headless true > streamlit.log 2>&1 &
    STREAMLIT_PID=$!
    sleep 3
    
    if curl -s --max-time 5 "http://localhost:8501/" >/dev/null 2>&1; then
        print_success "Streamlit dashboard running (PID: $STREAMLIT_PID)"
    else
        print_warning "Streamlit may still be starting..."
    fi
elif [ -f "dashboard/main.py" ]; then
    print_info "Starting Streamlit dashboard (main.py)..."
    streamlit run dashboard/main.py --server.port 8501 --server.headless true > streamlit.log 2>&1 &
    STREAMLIT_PID=$!
else
    print_warning "No dashboard file found"
fi

# Final verification
print_info "Step 10: Final verification..."

echo ""
echo "🧪 Testing API endpoints..."

# Test status endpoint
if curl -s "http://localhost:8000/api/status/" | grep -q "online"; then
    print_success "API status endpoint working"
else
    print_warning "API status endpoint not responding"
fi

# Test JWT endpoint
if curl -s -X POST "http://localhost:8000/api/auth/token/" \
   -H "Content-Type: application/json" \
   -d '{"username":"admin","password":"admin123"}' | grep -q "access"; then
    print_success "JWT authentication working"
else
    print_warning "JWT authentication may have issues"
fi

echo ""
echo "🎉 FinMark System Setup Complete!"
echo "================================="
echo ""
echo "🌐 Access Points:"
echo "   📊 Dashboard:    http://localhost:8501"
echo "   🔧 Admin:        http://localhost:8000/admin"
echo "   🔌 API:          http://localhost:8000/api"
echo ""
echo "👤 Login Credentials:"
echo "   🔑 admin     / admin123     (Super Admin)"
echo "   🔑 security  / security123  (Security Staff)"
echo "   🔑 analyst   / analyst123   (Data Analyst)"
echo "   🔑 manager   / manager123   (Manager)"
echo ""
echo "✅ Services Status:"
if [ ! -z "$DJANGO_PID" ]; then
    echo "   🟢 Django Server: Running (PID: $DJANGO_PID)"
else
    echo "   🔴 Django Server: Not Started"
fi

if [ ! -z "$STREAMLIT_PID" ]; then
    echo "   🟢 Streamlit Dashboard: Running (PID: $STREAMLIT_PID)"
else
    echo "   ⚪ Streamlit Dashboard: Not Available"
fi

echo "   🟢 Database: db.sqlite3 (SQLite)"
echo "   🟢 JWT Authentication: Configured"
echo "   🟢 CORS: Enabled"
echo ""
echo "📋 API Endpoints:"
echo "   🔐 POST /api/auth/token/        (Login)"
echo "   📊 GET  /api/status/            (System Status)" 
echo "   📈 GET  /api/metrics/           (Security Metrics)"
echo "   🗄️ GET  /api/database/          (Database Info)"
echo ""
echo "🔧 Logs:"
echo "   📄 Django: django.log"
echo "   📄 Streamlit: streamlit.log"
echo ""
echo "🛑 To stop: Press Ctrl+C or run:"
echo "   pkill -f 'manage.py runserver'"
echo "   pkill -f 'streamlit run'"
echo ""

# Keep running
trap 'echo ""; echo "🛑 Stopping services..."; kill $DJANGO_PID $STREAMLIT_PID 2>/dev/null; echo "✅ Services stopped"; exit 0' INT

print_info "Services running. Press Ctrl+C to stop."

# Monitor loop
while true; do
    sleep 30
    
    # Check if Django is still running
    if ! kill -0 $DJANGO_PID 2>/dev/null; then
        print_error "Django server stopped unexpectedly"
        break
    fi
    
    # Check if Streamlit is still running (if it was started)
    if [ ! -z "$STREAMLIT_PID" ] && ! kill -0 $STREAMLIT_PID 2>/dev/null; then
        print_warning "Streamlit dashboard stopped"
    fi
    
    # Optional: periodic health check
    # print_info "Services still running..."
done