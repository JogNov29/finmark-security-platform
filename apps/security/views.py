from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import SecurityEvent, Device

class SecurityViewSet(viewsets.ModelViewSet):
    queryset = SecurityEvent.objects.all()
    
    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        return Response({
            'critical_alerts': 3,
            'active_threats': 12,
            'total_events': SecurityEvent.objects.count(),
            'devices_online': Device.objects.filter(status='active').count()
        })
