"""
Configuración de URLs principal.

Incluye las rutas de administración y las APIs de las aplicaciones.
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Autenticación JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # APIs de Aplicaciones
    path('api/users/', include('apps.users.urls')),
    path('api/tenants/', include('apps.tenants.urls')),
    path('api/recruitment/', include('apps.recruitment.urls')),
]
