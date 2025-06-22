# Enhanced Django Views with Filtering Support
# apps/security/views.py

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from django.utils.dateparse import parse_datetime
from .models import SecurityEvent, Device
from apps.analytics.models import SystemMetrics

class SecurityViewSet(viewsets.ModelViewSet):
    queryset = SecurityEvent.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_date_filter(self, request):
        """Parse date filter parameters"""
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        filters = Q()
        
        if start_date:
            try:
                start_dt = parse_datetime(start_date)
                if start_dt:
                    filters &= Q(timestamp__gte=start_dt)
            except:
                pass
        
        if end_date:
            try:
                end_dt = parse_datetime(end_date)
                if end_dt:
                    filters &= Q(timestamp__lte=end_dt)
            except:
                pass
        
        # Default to last 7 days if no dates provided
        if not start_date and not end_date:
            filters &= Q(timestamp__gte=timezone.now() - timedelta(days=7))
        
        return filters
    
    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Get real-time security dashboard statistics with date filtering"""
        date_filters = self.get_date_filter(request)
        
        # Get counts with date filtering
        filtered_events = SecurityEvent.objects.filter(date_filters)
        
        critical_alerts = filtered_events.filter(severity='critical').count()
        active_threats = filtered_events.filter(is_threat=True).count()
        failed_logins = filtered_events.filter(event_type='login_failure').count()
        total_events = filtered_events.count()
        
        # Device statistics (not date filtered)
        devices_online = Device.objects.filter(status='active').count()
        devices_critical = Device.objects.filter(status='critical').count()
        
        system_health = self.calculate_system_health()
        
        return Response({
            'critical_alerts': critical_alerts,
            'active_threats': active_threats,
            'total_events': total_events,
            'devices_online': devices_online,
            'devices_critical': devices_critical,
            'failed_logins': failed_logins,
            'system_health': system_health,
            'last_updated': timezone.now().isoformat(),
            'filter_applied': bool(request.GET.get('start_date') or request.GET.get('end_date'))
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
        """Get recent security events with comprehensive filtering"""
        date_filters = self.get_date_filter(request)
        
        # Additional filters
        event_type = request.GET.get('event_type')
        severity = request.GET.get('severity')
        source_ip = request.GET.get('source_ip')
        is_threat = request.GET.get('is_threat')
        
        # Build query
        queryset = SecurityEvent.objects.filter(date_filters)
        
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        
        if severity:
            queryset = queryset.filter(severity=severity)
        
        if source_ip:
            queryset = queryset.filter(source_ip__icontains=source_ip)
        
        if is_threat is not None:
            is_threat_bool = is_threat.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(is_threat=is_threat_bool)
        
        # Order by most recent
        events = queryset.order_by('-timestamp')[:100]  # Limit to 100 events
        
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
        
        return Response({
            'events': data,
            'total_count': queryset.count(),
            'filter_info': {
                'date_filter': bool(request.GET.get('start_date') or request.GET.get('end_date')),
                'event_type': event_type,
                'severity': severity,
                'source_ip': source_ip,
                'is_threat': is_threat
            }
        })
    
    @action(detail=False, methods=['get'])
    def threat_analysis(self, request):
        """Analyze threats by type and severity with date filtering"""
        date_filters = self.get_date_filter(request)
        filtered_events = SecurityEvent.objects.filter(date_filters)
        
        # Group by event type
        by_type = filtered_events.values('event_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Group by severity
        by_severity = filtered_events.values('severity').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Top threat IPs
        top_threat_ips = filtered_events.filter(
            is_threat=True
        ).values('source_ip').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # Threat trend over time (last 24 hours)
        threat_trend = []
        now = timezone.now()
        for i in range(24):
            hour_start = now - timedelta(hours=i+1)
            hour_end = now - timedelta(hours=i)
            
            hour_threats = filtered_events.filter(
                is_threat=True,
                timestamp__gte=hour_start,
                timestamp__lt=hour_end
            ).count()
            
            threat_trend.append({
                'hour': hour_start.strftime('%H:00'),
                'threats': hour_threats
            })
        
        return Response({
            'by_type': list(by_type),
            'by_severity': list(by_severity),
            'top_threat_ips': list(top_threat_ips),
            'threat_trend': threat_trend,
            'analysis_period': {
                'start': request.GET.get('start_date', 'Last 7 days'),
                'end': request.GET.get('end_date', 'Now')
            }
        })
    
    @action(detail=False, methods=['get'])
    def export_events(self, request):
        """Export security events as JSON/CSV"""
        date_filters = self.get_date_filter(request)
        events = SecurityEvent.objects.filter(date_filters).order_by('-timestamp')
        
        format_type = request.GET.get('format', 'json')
        
        if format_type == 'csv':
            # Return CSV format
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow(['Timestamp', 'Event Type', 'Severity', 'Source IP', 'Details', 'Is Threat'])
            
            # Write data
            for event in events:
                writer.writerow([
                    event.timestamp.isoformat(),
                    event.event_type,
                    event.severity,
                    event.source_ip,
                    event.details,
                    event.is_threat
                ])
            
            csv_data = output.getvalue()
            output.close()
            
            return Response({
                'format': 'csv',
                'data': csv_data,
                'filename': f'security_events_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv'
            })
        
        else:
            # Return JSON format
            data = []
            for event in events:
                data.append({
                    'timestamp': event.timestamp.isoformat(),
                    'event_type': event.event_type,
                    'severity': event.severity,
                    'source_ip': event.source_ip,
                    'details': event.details,
                    'is_threat': event.is_threat
                })
            
            return Response({
                'format': 'json',
                'events': data,
                'total_count': len(data),
                'exported_at': timezone.now().isoformat()
            })

class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def network_status(self, request):
        """Get network device status overview with filtering"""
        status_filter = request.GET.get('status')
        device_type_filter = request.GET.get('device_type')
        
        queryset = Device.objects.all()
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        if device_type_filter:
            queryset = queryset.filter(device_type=device_type_filter)
        
        devices = queryset.order_by('hostname')
        
        data = []
        for device in devices:
            # Calculate last seen (simulate)
            import random
            last_seen_minutes = random.randint(1, 60)
            if device.status == 'critical':
                last_seen_minutes = random.randint(60, 1440)  # 1-24 hours for critical
            
            last_seen = f"{last_seen_minutes} min ago" if last_seen_minutes < 60 else f"{last_seen_minutes // 60} hours ago"
            
            data.append({
                'id': str(device.id),
                'hostname': device.hostname,
                'ip_address': device.ip_address,
                'device_type': device.device_type,
                'status': device.status,
                'os': device.os,
                'vulnerabilities': device.notes if device.notes else None,
                'last_seen': last_seen
            })
        
        # Summary statistics
        total_devices = queryset.count()
        status_summary = queryset.values('status').annotate(
            count=Count('id')
        ).order_by('-count')
        
        type_summary = queryset.values('device_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return Response({
            'devices': data,
            'summary': {
                'total_devices': total_devices,
                'by_status': list(status_summary),
                'by_type': list(type_summary)
            },
            'filters_applied': {
                'status': status_filter,
                'device_type': device_type_filter
            }
        })
    
    @action(detail=False, methods=['get'])
    def vulnerability_report(self, request):
        """Generate comprehensive vulnerability report"""
        devices_with_vulns = Device.objects.exclude(notes='').exclude(notes__isnull=True)
        
        vulnerabilities = []
        for device in devices_with_vulns:
            # Analyze vulnerability severity from notes
            notes_lower = device.notes.lower()
            
            if any(keyword in notes_lower for keyword in ['critical', 'no firewall', 'no antivirus']):
                vuln_severity = 'critical'
                risk_score = 9
            elif any(keyword in notes_lower for keyword in ['outdated', 'ssl', 'tls', 'password']):
                vuln_severity = 'high'
                risk_score = 7
            elif any(keyword in notes_lower for keyword in ['update', 'patch', 'config']):
                vuln_severity = 'medium'
                risk_score = 5
            else:
                vuln_severity = 'low'
                risk_score = 3
            
            vulnerabilities.append({
                'device': device.hostname,
                'ip': device.ip_address,
                'device_type': device.device_type,
                'status': device.status,
                'vulnerability': device.notes,
                'severity': vuln_severity,
                'risk_score': risk_score,
                'remediation_priority': 'high' if risk_score >= 7 else 'medium' if risk_score >= 5 else 'low'
            })
        
        # Sort by risk score
        vulnerabilities.sort(key=lambda x: x['risk_score'], reverse=True)
        
        # Summary statistics
        total_vulnerabilities = len(vulnerabilities)
        critical_vulns = len([v for v in vulnerabilities if v['severity'] == 'critical'])
        high_vulns = len([v for v in vulnerabilities if v['severity'] == 'high'])
        
        return Response({
            'vulnerabilities': vulnerabilities,
            'summary': {
                'total_vulnerabilities': total_vulnerabilities,
                'critical': critical_vulns,
                'high': high_vulns,
                'medium': len([v for v in vulnerabilities if v['severity'] == 'medium']),
                'low': len([v for v in vulnerabilities if v['severity'] == 'low'])
            },
            'report_generated_at': timezone.now().isoformat()
        })

# apps/analytics/views.py - Enhanced Analytics Views

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg, Max, Min, Count
from django.utils import timezone
from datetime import timedelta
from django.utils.dateparse import parse_datetime
from .models import SystemMetrics, UserActivity

class SystemMetricsViewSet(viewsets.ModelViewSet):
    queryset = SystemMetrics.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_date_filter(self, request):
        """Parse date filter parameters for metrics"""
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        filters = {}
        
        if start_date:
            try:
                start_dt = parse_datetime(start_date)
                if start_dt:
                    filters['timestamp__gte'] = start_dt
            except:
                pass
        
        if end_date:
            try:
                end_dt = parse_datetime(end_date)
                if end_dt:
                    filters['timestamp__lte'] = end_dt
            except:
                pass
        
        # Default to last 24 hours if no dates provided
        if not start_date and not end_date:
            filters['timestamp__gte'] = timezone.now() - timedelta(hours=24)
        
        return filters
    
    @action(detail=False, methods=['get'])
    def performance_timeline(self, request):
        """Get performance metrics for timeline charts with date filtering"""
        date_filters = self.get_date_filter(request)
        
        metrics = SystemMetrics.objects.filter(**date_filters).order_by('timestamp')
        
        data = []
        for metric in metrics:
            data.append({
                'timestamp': metric.timestamp.isoformat(),
                'cpu_usage': metric.cpu_usage,
                'memory_usage': metric.memory_usage,
                'response_time': metric.response_time
            })
        
        return Response({
            'metrics': data,
            'total_count': len(data),
            'time_range': {
                'start': request.GET.get('start_date', 'Auto-determined'),
                'end': request.GET.get('end_date', 'Now')
            }
        })
    
    @action(detail=False, methods=['get'])
    def performance_overview(self, request):
        """Get system performance metrics overview with date filtering"""
        date_filters = self.get_date_filter(request)
        
        recent_metrics = SystemMetrics.objects.filter(**date_filters)
        
        if not recent_metrics.exists():
            return Response({
                'avg_cpu': 0,
                'avg_memory': 0,
                'avg_response_time': 0,
                'max_cpu': 0,
                'max_memory': 0,
                'max_response_time': 0,
                'min_cpu': 0,
                'min_memory': 0,
                'min_response_time': 0,
                'data_points': 0
            })
        
        stats = recent_metrics.aggregate(
            avg_cpu=Avg('cpu_usage'),
            avg_memory=Avg('memory_usage'),
            avg_response_time=Avg('response_time'),
            max_cpu=Max('cpu_usage'),
            max_memory=Max('memory_usage'),
            max_response_time=Max('response_time'),
            min_cpu=Min('cpu_usage'),
            min_memory=Min('memory_usage'),
            min_response_time=Min('response_time')
        )
        
        stats['data_points'] = recent_metrics.count()
        
        # Calculate performance status
        avg_cpu = stats['avg_cpu'] or 0
        avg_memory = stats['avg_memory'] or 0
        avg_response = stats['avg_response_time'] or 0
        
        if avg_cpu > 80 or avg_memory > 85 or avg_response > 500:
            performance_status = 'critical'
        elif avg_cpu > 60 or avg_memory > 70 or avg_response > 300:
            performance_status = 'warning'
        else:
            performance_status = 'good'
        
        stats['performance_status'] = performance_status
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def performance_trends(self, request):
        """Get performance trends and predictions"""
        date_filters = self.get_date_filter(request)
        
        # Get hourly averages for trend analysis
        from django.db.models import Avg
        from django.db.models.functions import TruncHour
        
        hourly_metrics = SystemMetrics.objects.filter(**date_filters).annotate(
            hour=TruncHour('timestamp')
        ).values('hour').annotate(
            avg_cpu=Avg('cpu_usage'),
            avg_memory=Avg('memory_usage'),
            avg_response=Avg('response_time')
        ).order_by('hour')
        
        trends = []
        for metric in hourly_metrics:
            trends.append({
                'hour': metric['hour'].isoformat(),
                'avg_cpu': round(metric['avg_cpu'] or 0, 2),
                'avg_memory': round(metric['avg_memory'] or 0, 2),
                'avg_response_time': round(metric['avg_response'] or 0, 2)
            })
        
        return Response({
            'hourly_trends': trends,
            'trend_analysis': {
                'data_points': len(trends),
                'time_span_hours': len(trends),
                'analysis_generated_at': timezone.now().isoformat()
            }
        })

class UserActivityViewSet(viewsets.ModelViewSet):
    """Enhanced user activity tracking with filtering"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserActivity.objects.all()
    
    def get_date_filter(self, request):
        """Parse date filter parameters"""
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        filters = {}
        
        if start_date:
            try:
                start_dt = parse_datetime(start_date)
                if start_dt:
                    filters['timestamp__gte'] = start_dt
            except:
                pass
        
        if end_date:
            try:
                end_dt = parse_datetime(end_date)
                if end_dt:
                    filters['timestamp__lte'] = end_dt
            except:
                pass
        
        # Default to last 7 days
        if not start_date and not end_date:
            filters['timestamp__gte'] = timezone.now() - timedelta(days=7)
        
        return filters
    
    @action(detail=False, methods=['get'])
    def recent_activity(self, request):
        """Get recent user activity for audit logs with filtering"""
        date_filters = self.get_date_filter(request)
        
        # Get user activities
        activities = UserActivity.objects.filter(**date_filters).order_by('-timestamp')[:50]
        
        activity_log = []
        for activity in activities:
            activity_log.append({
                'id': str(activity.id),
                'timestamp': activity.timestamp.isoformat(),
                'user': activity.user.username,
                'action': activity.event_type,
                'details': activity.details,
                'ip_address': activity.ip_address
            })
        
        # Also include recent security events
        from apps.security.models import SecurityEvent
        recent_events = SecurityEvent.objects.filter(**date_filters).order_by('-timestamp')[:25]
        
        for event in recent_events:
            activity_log.append({
                'id': str(event.id),
                'timestamp': event.timestamp.isoformat(),
                'user': 'system',
                'action': event.event_type,
                'details': event.details,
                'ip_address': event.source_ip,
                'severity': event.severity
            })
        
        # Sort combined log by timestamp
        activity_log.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return Response({
            'activities': activity_log[:50],  # Limit to 50 most recent
            'total_user_activities': activities.count(),
            'total_security_events': recent_events.count()
        })
    
    @action(detail=False, methods=['get'])
    def activity_summary(self, request):
        """Get user activity summary and statistics"""
        date_filters = self.get_date_filter(request)
        
        activities = UserActivity.objects.filter(**date_filters)
        
        # Activity by type
        by_type = activities.values('event_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Activity by user
        by_user = activities.values('user__username').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Activity by hour
        from django.db.models.functions import Extract
        by_hour = activities.annotate(
            hour=Extract('timestamp', 'hour')
        ).values('hour').annotate(
            count=Count('id')
        ).order_by('hour')
        
        return Response({
            'summary': {
                'total_activities': activities.count(),
                'unique_users': activities.values('user').distinct().count(),
                'by_type': list(by_type),
                'by_user': list(by_user),
                'by_hour': list(by_hour)
            },
            'period': {
                'start': request.GET.get('start_date', 'Last 7 days'),
                'end': request.GET.get('end_date', 'Now')
            }
        })