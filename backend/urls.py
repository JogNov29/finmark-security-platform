from django.contrib import admin
from django.urls import path, include
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json

# Safe API Views
@api_view(['GET'])
def api_status(request):
    """API Status endpoint"""
    return Response({
        'status': 'online',
        'database': 'connected',
        'timestamp': '2024-01-01T00:00:00Z'
    })

@api_view(['GET']) 
def api_metrics(request):
    """Security metrics endpoint"""
    return Response({
        'critical_alerts': 3,
        'active_threats': 12,
        'system_health': 98.2,
        'daily_orders': 1847
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/status/', api_status, name='api_status'),
    path('api/metrics/', api_metrics, name='api_metrics'),
]
