from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView
from apps.core.views import ProductViewSet
from apps.security.views import SecurityViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'security', SecurityViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/token/', TokenObtainPairView.as_view()),
]
