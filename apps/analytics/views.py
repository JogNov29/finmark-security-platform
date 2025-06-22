from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg, Max, Min
from django.utils import timezone
from datetime import timedelta
from .models import SystemMetrics, UserActivity

class SystemMetricsViewSet(viewsets.ModelViewSet):
    queryset = SystemMetrics.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def performance_timeline(self, request):
        """Get performance metrics for timeline charts"""
        # Get last 24 hours of data
        metrics = SystemMetrics.objects.filter(
            timestamp__gte=timezone.now() - timedelta(hours=24)
        ).order_by('timestamp')
        
        data = []
        for metric in metrics:
            data.append({
                'timestamp': metric.timestamp.isoformat(),
                'cpu_usage': metric.cpu_usage,
                'memory_usage': metric.memory_usage,
                'response_time': metric.response_time
            })
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def performance_overview(self, request):
        """Get system performance metrics overview"""
        # Get recent metrics (last 24 hours)
        recent_metrics = SystemMetrics.objects.filter(
            timestamp__gte=timezone.now() - timedelta(hours=24)
        )
        
        if not recent_metrics.exists():
            return Response({
                'avg_cpu': 0,
                'avg_memory': 0,
                'avg_response_time': 0,
                'max_cpu': 0,
                'max_memory': 0,
                'max_response_time': 0
            })
        
        stats = recent_metrics.aggregate(
            avg_cpu=Avg('cpu_usage'),
            avg_memory=Avg('memory_usage'),
            avg_response_time=Avg('response_time'),
            max_cpu=Max('cpu_usage'),
            max_memory=Max('memory_usage'),
            max_response_time=Max('response_time')
        )
        
        return Response(stats)
