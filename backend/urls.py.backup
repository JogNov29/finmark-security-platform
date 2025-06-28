# backend/urls.py - Complete FinMark URLs with JWT Authentication
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
