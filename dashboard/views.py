# dashboard/views.py
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from datetime import datetime, timedelta
import os
import random

User = get_user_model()

@api_view(['GET'])
@permission_classes([AllowAny])
def system_status(request):
    """Return comprehensive system status"""
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_connected = True
            
            # Get database info
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            
    except Exception as e:
        db_connected = False
        tables = []
    
    # Check database file
    db_path = os.path.join(os.getcwd(), 'db.sqlite3')
    db_exists = os.path.exists(db_path)
    
    return Response({
        'timestamp': datetime.now().isoformat(),
        'status': 'online',
        'database': {
            'connected': db_connected,
            'path': db_path,
            'exists': db_exists,
            'tables': len(tables),
            'status': 'healthy' if db_connected else 'error'
        },
        'services': {
            'api': 'healthy',
            'authentication': 'healthy',
            'security_monitor': 'healthy'
        },
        'metrics': {
            'uptime': '99.8%',
            'active_users': User.objects.count(),
            'total_requests': random.randint(1000, 5000)
        }
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def security_metrics(request):
    """Return security metrics - requires authentication"""
    return Response({
        'critical_alerts': random.randint(0, 5),
        'active_threats': random.randint(5, 20),
        'failed_logins': random.randint(10, 50),
        'system_health': round(random.uniform(95, 99.9), 1),
        'successful_logins': random.randint(100, 500),
        'data_transferred': f"{random.uniform(1.0, 5.0):.1f}TB",
        'daily_orders': random.randint(1500, 2500),
        'timestamp': datetime.now().isoformat()
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def database_info(request):
    """Return detailed database information"""
    try:
        with connection.cursor() as cursor:
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            
            # Get user count
            user_count = User.objects.count()
            
            # Get database size (approximate)
            db_path = os.path.join(os.getcwd(), 'db.sqlite3')
            db_size = os.path.getsize(db_path) if os.path.exists(db_path) else 0
            
        return Response({
            'database_connected': True,
            'database_path': db_path,
            'database_size_bytes': db_size,
            'database_size_mb': round(db_size / (1024 * 1024), 2),
            'tables': tables,
            'table_count': len(tables),
            'users_count': user_count,
            'last_check': datetime.now().isoformat()
        })
        
    except Exception as e:
        return Response({
            'database_connected': False,
            'error': str(e),
            'last_check': datetime.now().isoformat()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Return current user profile information"""
    user = request.user
    
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
        'is_active': user.is_active,
        'date_joined': user.date_joined.isoformat(),
        'last_login': user.last_login.isoformat() if user.last_login else None,
        'groups': [group.name for group in user.groups.all()],
        'permissions': {
            'can_view_dashboard': True,
            'can_view_security_metrics': user.is_staff,
            'can_view_admin_functions': user.is_superuser,
            'can_manage_users': user.is_superuser
        }
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def csv_data_status(request):
    """Check status of CSV data files"""
    csv_files = [
        'event_logs.csv',
        'marketing_summary.csv', 
        'trend_report.csv',
        'network_inventory.csv',
        'traffic_logs.csv'
    ]
    
    file_status = {}
    total_size = 0
    
    for csv_file in csv_files:
        if os.path.exists(csv_file):
            file_size = os.path.getsize(csv_file)
            total_size += file_size
            file_status[csv_file] = {
                'exists': True,
                'size_bytes': file_size,
                'size_kb': round(file_size / 1024, 2),
                'last_modified': datetime.fromtimestamp(os.path.getmtime(csv_file)).isoformat()
            }
        else:
            file_status[csv_file] = {
                'exists': False,
                'size_bytes': 0,
                'size_kb': 0,
                'last_modified': None
            }
    
    available_files = sum(1 for f in file_status.values() if f['exists'])
    
    return Response({
        'csv_files': file_status,
        'summary': {
            'total_files': len(csv_files),
            'available_files': available_files,
            'missing_files': len(csv_files) - available_files,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2)
        },
        'last_check': datetime.now().isoformat()
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def api_health(request):
    """Simple health check endpoint"""
    return Response({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'service': 'FinMark Security API'
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_auth(request):
    """Test authentication endpoint"""
    return Response({
        'authenticated': True,
        'user': request.user.username,
        'permissions': {
            'is_staff': request.user.is_staff,
            'is_superuser': request.user.is_superuser
        },
        'message': 'Authentication successful',
        'timestamp': datetime.now().isoformat()
    })

# Additional utility endpoints
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def system_logs(request):
    """Get recent system logs (requires staff permission)"""
    if not request.user.is_staff:
        return Response({
            'error': 'Staff permission required'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Mock log data
    logs = [
        {
            'timestamp': (datetime.now() - timedelta(minutes=5)).isoformat(),
            'level': 'INFO',
            'message': 'User login successful',
            'user': request.user.username
        },
        {
            'timestamp': (datetime.now() - timedelta(minutes=15)).isoformat(),
            'level': 'WARNING',
            'message': 'Failed login attempt detected',
            'ip': '192.168.1.45'
        },
        {
            'timestamp': (datetime.now() - timedelta(minutes=30)).isoformat(),
            'level': 'INFO',
            'message': 'System backup completed',
            'status': 'success'
        }
    ]
    
    return Response({
        'logs': logs,
        'total': len(logs),
        'last_update': datetime.now().isoformat()
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def security_alerts(request):
    """Get current security alerts"""
    if not request.user.is_staff:
        return Response({
            'error': 'Staff permission required'
        }, status=status.HTTP_403_FORBIDDEN)
    
    alerts = [
        {
            'id': 1,
            'severity': 'critical',
            'title': 'Multiple Failed Login Attempts',
            'description': 'Detected multiple failed login attempts from IP 192.168.1.45',
            'timestamp': (datetime.now() - timedelta(minutes=2)).isoformat(),
            'status': 'active'
        },
        {
            'id': 2,
            'severity': 'warning',
            'title': 'Unusual Traffic Pattern',
            'description': 'Unusual traffic pattern detected on network interface',
            'timestamp': (datetime.now() - timedelta(minutes=8)).isoformat(),
            'status': 'investigating'
        },
        {
            'id': 3,
            'severity': 'info',
            'title': 'System Update',
            'description': 'Security definitions updated successfully',
            'timestamp': (datetime.now() - timedelta(minutes=15)).isoformat(),
            'status': 'resolved'
        }
    ]
    
    return Response({
        'alerts': alerts,
        'summary': {
            'critical': len([a for a in alerts if a['severity'] == 'critical']),
            'warning': len([a for a in alerts if a['severity'] == 'warning']),
            'info': len([a for a in alerts if a['severity'] == 'info']),
            'active': len([a for a in alerts if a['status'] == 'active'])
        },
        'last_update': datetime.now().isoformat()
    })