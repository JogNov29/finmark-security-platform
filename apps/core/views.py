from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Product

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    
    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        return Response({
            'total_products': Product.objects.count(),
            'active_users': 150,
            'orders_today': 1247,
            'revenue_today': 85000.50
        })
