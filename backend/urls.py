# backend/urls.py - FinMark with PUBLIC API endpoints
from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from datetime import datetime
import random

@api_view(['GET'])
@permission_classes([AllowAny])  # PUBLIC - No auth required
def api_root(request):
    """API root endpoint - PUBLIC"""
    return Response({
        'message': 'FinMark Security Operations Center API',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'status': 'operational',
        'endpoints': {
            'auth': '/api/auth/token/',
            'status': '/api/status/',
            'metrics': '/api/metrics/',
            'database': '/api/database/',
        }
    })

@api_view(['GET'])
@permission_classes([AllowAny])  # PUBLIC - No auth required
def api_status(request):
    """System status endpoint - PUBLIC"""
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_connected = True
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
    except Exception as e:
        db_connected = False
        tables = []
        print(f"Database error: {e}")
    
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
@permission_classes([AllowAny])  # PUBLIC - No auth required
def api_metrics(request):
    """Security metrics endpoint - PUBLIC"""
    return Response({
        'critical_alerts': random.randint(0, 5),
        'active_threats': random.randint(8, 15),
        'failed_logins': random.randint(15, 35),
        'system_health': round(random.uniform(95, 99.5), 1),
        'daily_orders': random.randint(1500, 2500),
        'timestamp': datetime.now().isoformat()
    })

@api_view(['GET'])
@permission_classes([AllowAny])  # PUBLIC - No auth required
def api_database(request):
    """Database information endpoint - PUBLIC"""
    try:
        from django.db import connection
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
        
        return Response({
            'database_connected': True,
            'database_path': 'db.sqlite3',
            'tables': tables,
            'table_count': len(tables),
            'users_count': User.objects.count(),
            'last_check': datetime.now().isoformat()
        })
    except Exception as e:
        return Response({
            'database_connected': False,
            'error': str(e),
            'last_check': datetime.now().isoformat()
        }, status=500)

# URL Patterns
urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),
    
    # PUBLIC API Root
    path('api/', api_root, name='api_root'),
    
    # JWT Authentication Endpoints
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # PUBLIC API Endpoints (Dashboard can access without login)
    path('api/status/', api_status, name='api_status'),
    path('api/metrics/', api_metrics, name='api_metrics'),
    path('api/database/', api_database, name='api_database'),
]
