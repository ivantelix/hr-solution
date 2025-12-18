"""URLs de la app tenants."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.tenants.views import TenantViewSet

# Router para ViewSets
router = DefaultRouter()
router.register(r"tenants", TenantViewSet, basename="tenant")

urlpatterns = [
    path("", include(router.urls)),
]
