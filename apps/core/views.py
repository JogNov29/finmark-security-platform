from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Product

User = get_user_model()

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Get general dashboard statistics"""
        return Response({
            'total_products': Product.objects.count(),
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'orders_today': 1847,
            'revenue_today': 85000.50,
            'target_orders': 3000
        })

class UserActivityViewSet(viewsets.ModelViewSet):
    """Handle user activity and audit logs"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        from apps.analytics.models import UserActivity
        return UserActivity.objects.all()
    
    @action(detail=False, methods=['get'])
    def recent_activity(self, request):
        """Get recent user activity for audit logs"""
        from apps.security.models import SecurityEvent
        
        recent_events = SecurityEvent.objects.order_by('-timestamp')[:50]
        
        activity_log = []
        for event in recent_events:
            activity_log.append({
                'timestamp': event.timestamp.isoformat(),
                'user': 'system',
                'action': event.event_type,
                'details': event.details,
                'ip_address': event.source_ip,
                'severity': event.severity
            })
        
        return Response(activity_log)
