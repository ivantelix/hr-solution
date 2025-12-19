"""
Configuración de URLs principal.

Incluye las rutas de administración y las APIs de las aplicaciones.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),

    # APIs de Aplicaciones
    path("api/users/", include("apps.users.urls")),
    path("api/tenants/", include("apps.tenants.urls")),
    path("api/recruitment/", include("apps.recruitment.urls")),
]
