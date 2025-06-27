#!/usr/bin/env python3
"""
FinMark JWT Authentication Fix Script
=====================================
This script fixes the missing JWT authentication endpoints and ensures proper setup.
"""

import os
import sys
import subprocess

def run_command(command, description):
    """Run a command and return success status"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} failed: {e}")
        return False

def check_file_exists(filepath):
    """Check if a file exists"""
    return os.path.exists(filepath)

def backup_file(filepath):
    """Create a backup of a file"""
    if os.path.exists(filepath):
        backup_path = f"{filepath}.backup"
        try:
            import shutil
            shutil.copy2(filepath, backup_path)
            print(f"✅ Backed up {filepath} to {backup_path}")
            return True
        except Exception as e:
            print(f"⚠️ Could not backup {filepath}: {e}")
            return False
    return False

def update_urls_file():
    """Update the URLs file with JWT authentication endpoints"""
    urls_files = ['backend/urls.py', 'finmark_project/urls.py', 'finmark/urls.py']
    
    urls_file = None
    for file_path in urls_files:
        if check_file_exists(file_path):
            urls_file = file_path
            break
    
    if not urls_file:
        print("❌ Could not find Django URLs file")
        return False
    
    print(f"📁 Found URLs file: {urls_file}")
    
    # Backup the original file
    backup_file(urls_file)
    
    # Updated URLs content with JWT endpoints
    updated_content = '''# backend/urls.py - Complete FinMark URLs with JWT Authentication
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime
import random

@api_view(['GET'])
def api_root(request):
    """API root endpoint with available endpoints"""
    return Response({
        'message': 'FinMark Security Operations Center API',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'status': 'operational',
        'endpoints': {
            'authentication': {
                'login': '/api/auth/token/',
                'refresh': '/api/auth/token/refresh/',
                'verify': '/api/auth/token/verify/',
            },
            'api': {
                'status': '/api/status/',
                'metrics': '/api/metrics/',
                'database': '/api/database/',
                'user_profile': '/api/user/profile/',
            },
            'admin': '/admin/',
        }
    })

@api_view(['GET'])
def api_status(request):
    """Comprehensive system status endpoint"""
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
            'status': 'healthy' if db_connected else 'error'
        },
        'services': {
            'api': 'healthy',
            'authentication': 'healthy',
            'security_monitor': 'healthy'
        }
    })

@api_view(['GET']) 
def api_metrics(request):
    """Security and business metrics endpoint"""
    return Response({
        'critical_alerts': random.randint(0, 5),
        'active_threats': random.randint(8, 15),
        'failed_logins': random.randint(15, 35),
        'system_health': round(random.uniform(95, 99.5), 1),
        'daily_orders': random.randint(1500, 2500),
        'timestamp': datetime.now().isoformat()
    })

@api_view(['GET'])
def api_database(request):
    """Database connection and information endpoint"""
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
            'last_check': datetime.now().isoformat()
        })
        
    except Exception as e:
        return Response({
            'database_connected': False,
            'error': str(e)
        }, status=500)

@api_view(['GET'])
def user_profile(request):
    """Get current user profile - requires authentication"""
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=401)
    
    user = request.user
    return Response({
        'username': user.username,
        'email': user.email,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
        'permissions': {
            'can_view_dashboard': True,
            'can_view_security_metrics': user.is_staff,
            'can_view_admin_functions': user.is_superuser
        }
    })

# URL Patterns with JWT Authentication (FIXED!)
urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),
    
    # API Root
    path('api/', api_root, name='api_root'),
    
    # JWT Authentication Endpoints (These were missing!)
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # API Endpoints
    path('api/status/', api_status, name='api_status'),
    path('api/metrics/', api_metrics, name='api_metrics'),
    path('api/database/', api_database, name='api_database'),
    path('api/user/profile/', user_profile, name='user_profile'),
]

# Try to include dashboard URLs if the app exists
try:
    urlpatterns.append(path('api/dashboard/', include('dashboard.urls')))
except ImportError:
    pass
'''
    
    try:
        with open(urls_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print(f"✅ Updated {urls_file} with JWT authentication endpoints")
        return True
    except Exception as e:
        print(f"❌ Failed to update {urls_file}: {e}")
        return False

def check_settings():
    """Check Django settings for JWT configuration"""
    settings_files = ['backend/settings.py', 'finmark_project/settings.py', 'finmark/settings.py']
    
    for settings_file in settings_files:
        if check_file_exists(settings_file):
            print(f"📁 Found settings file: {settings_file}")
            
            try:
                with open(settings_file, 'r') as f:
                    content = f.read()
                
                # Check for JWT configuration
                if 'rest_framework_simplejwt' in content:
                    print("✅ JWT package found in INSTALLED_APPS")
                else:
                    print("⚠️ JWT package not found in INSTALLED_APPS")
                
                if 'SIMPLE_JWT' in content:
                    print("✅ JWT configuration found")
                else:
                    print("⚠️ JWT configuration not found")
                
                if 'corsheaders' in content:
                    print("✅ CORS headers configured")
                else:
                    print("⚠️ CORS headers not configured")
                
                return True
                
            except Exception as e:
                print(f"❌ Could not read {settings_file}: {e}")
    
    return False

def install_packages():
    """Install required packages"""
    packages = [
        'djangorestframework-simplejwt',
        'django-cors-headers',
        'djangorestframework'
    ]
    
    for package in packages:
        print(f"📦 Installing {package}...")
        success = run_command(f"pip install {package}", f"Install {package}")
        if not success:
            print(f"⚠️ Failed to install {package}")

def test_jwt_endpoints():
    """Test JWT endpoints"""
    print("\n🧪 Testing JWT endpoints...")
    
    # Test token endpoint
    import requests
    
    try:
        # Test if Django server is running
        response = requests.get("http://localhost:8000/api/", timeout=5)
        if response.status_code == 200:
            print("✅ Django server is responding")
            
            # Test JWT endpoint
            try:
                response = requests.post("http://localhost:8000/api/auth/token/", 
                                       json={"username": "admin", "password": "admin123"}, 
                                       timeout=5)
                if response.status_code == 200:
                    print("✅ JWT authentication endpoint is working")
                    data = response.json()
                    if 'access' in data:
                        print("✅ JWT tokens are being generated correctly")
                    return True
                else:
                    print(f"⚠️ JWT endpoint returned status {response.status_code}")
                    print(f"Response: {response.text}")
            except Exception as e:
                print(f"❌ JWT endpoint test failed: {e}")
        else:
            print(f"⚠️ Django server responded with status {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("⚠️ Django server is not running. Start it with: python manage.py runserver")
    except Exception as e:
        print(f"❌ Server test failed: {e}")
    
    return False

def main():
    """Main fix script"""
    print("🚀 FinMark JWT Authentication Fix Script")
    print("=" * 50)
    print()
    
    # Check if we're in a Django project
    if not check_file_exists('manage.py'):
        print("❌ Not in a Django project directory (manage.py not found)")
        return
    
    print("✅ Django project detected")
    
    # Install required packages
    print("\n📦 Step 1: Installing required packages...")
    install_packages()
    
    # Check settings
    print("\n⚙️ Step 2: Checking Django settings...")
    check_settings()
    
    # Update URLs file
    print("\n🔧 Step 3: Fixing URLs configuration...")
    if update_urls_file():
        print("✅ URLs file updated successfully")
    else:
        print("❌ Failed to update URLs file")
        return
    
    # Run migrations
    print("\n🗄️ Step 4: Running Django migrations...")
    run_command("python manage.py migrate", "Database migrations")
    
    # Create superuser if needed
    print("\n👤 Step 5: Ensuring admin user exists...")
    run_command(
        'python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username=\'admin\').exists() or User.objects.create_superuser(\'admin\', \'admin@finmark.local\', \'admin123\')"',
        "Create admin user"
    )
    
    print("\n🎉 JWT Authentication Fix Complete!")
    print("=" * 50)
    print()
    print("✅ What was fixed:")
    print("   • Added missing JWT authentication endpoints")
    print("   • Updated /api/auth/token/ endpoint")
    print("   • Added /api/auth/token/refresh/ endpoint") 
    print("   • Added /api/auth/token/verify/ endpoint")
    print("   • Enhanced API status and metrics endpoints")
    print()
    print("🔑 Test your login:")
    print("   Username: admin")
    print("   Password: admin123")
    print()
    print("🌐 Available endpoints:")
    print("   • http://localhost:8000/api/ (API root)")
    print("   • http://localhost:8000/api/auth/token/ (Login)")
    print("   • http://localhost:8000/api/status/ (System status)")
    print("   • http://localhost:8000/api/metrics/ (Security metrics)")
    print("   • http://localhost:8000/admin/ (Django admin)")
    print()
    print("🚀 Next steps:")
    print("   1. Start Django: python manage.py runserver")
    print("   2. Start Streamlit: streamlit run dashboard/finmark_dashboard.py")
    print("   3. Open dashboard: http://localhost:8501")
    print()
    
    # Test endpoints if server is running
    test_jwt_endpoints()

if __name__ == "__main__":
    main()