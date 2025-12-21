"""URLs de la app tenants."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.tenants.views import TenantAIConfigViewSet, TenantViewSet
from apps.tenants.views.permission_views import PermissionListView

# Router para ViewSets
router = DefaultRouter()
router.register(r"tenants", TenantViewSet, basename="tenant")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "tenants/<str:tenant_id>/ai-config/",
        TenantAIConfigViewSet.as_view({"get": "list", "post": "create"}),
        name="tenant-ai-config",
    ),
    path(
        "tenants/<str:tenant_id>/ai-config/activate/",
        TenantAIConfigViewSet.as_view({"post": "activate"}),
        name="tenant-ai-config-activate",
    ),
    path(
        "tenants/<str:tenant_id>/ai-config/deactivate/",
        TenantAIConfigViewSet.as_view({"post": "deactivate"}),
        name="tenant-ai-config-deactivate",
    ),
    path(
        "permissions/",
        PermissionListView.as_view(),
        name="permission-list",
    ),
]

