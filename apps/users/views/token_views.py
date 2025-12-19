"""
Custom Token View to use the custom serializer.
"""
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from apps.users.serializers.token_serializers import (
    CustomTokenObtainPairSerializer,
    CustomTokenRefreshSerializer,
)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Vista de login personalizada que inyecta tenant_id y role en el token.
    """

    serializer_class = CustomTokenObtainPairSerializer


class CustomTokenRefreshView(TokenRefreshView):
    """
    Vista de refresh personalizada que preserva tenant_id y role.
    """

    serializer_class = CustomTokenRefreshSerializer
