from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Import all viewsets
from apps.core.views import ProductViewSet, UserActivityViewSet
from apps.security.views import SecurityViewSet, DeviceViewSet
from apps.analytics.views import SystemMetricsViewSet

# Create router and register all viewsets
router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'security', SecurityViewSet)
router.register(r'devices', DeviceViewSet)
router.register(r'metrics', SystemMetricsViewSet)
router.register(r'activity', UserActivityViewSet, basename='activity')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
