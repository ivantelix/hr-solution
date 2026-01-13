"""
Configuración de URLs principal.

Incluye las rutas de administración y las APIs de las aplicaciones.
"""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # Documentación API
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # APIs de Aplicaciones
    path("api/users/", include("apps.users.urls")),
    path("api/tenants/", include("apps.tenants.urls")),
    path("api/recruitment/", include("apps.recruitment.urls")),
]
