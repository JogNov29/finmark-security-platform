from rest_framework import viewsets, permissions
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
