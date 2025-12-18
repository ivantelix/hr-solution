"""
ViewSet para autenticación y registro.

Este módulo contiene los endpoints públicos para registro
de nuevos tenant owners y autenticación.
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.serializers import RegisterTenantOwnerSerializer


class AuthViewSet(viewsets.GenericViewSet):
    """
    ViewSet para autenticación y registro.

    Proporciona endpoints públicos para:
    - Registro de nuevos tenant owners
    - Login (delegado a JWT)
    - Refresh token (delegado a JWT)

    Endpoints:
        - POST /auth/register/ - Registro de tenant owner
    """

    permission_classes = [AllowAny]
    serializer_class = RegisterTenantOwnerSerializer

    @action(detail=False, methods=["post"])
    def register(self, request: Request) -> Response:
        """
        Registra un nuevo usuario como tenant owner.

        Este endpoint crea:
        1. Un nuevo usuario
        2. Un nuevo tenant
        3. La relación de membresía con rol OWNER
        4. Tokens JWT para login automático

        Args:
            request: Request con datos de registro.

        Returns:
            Response: Usuario, tenant y tokens creados.

        Example:
            POST /auth/register/
            {
                "username": "admin@empresa.com",
                "email": "admin@empresa.com",
                "password": "SecurePass123",
                "password_confirm": "SecurePass123",
                "first_name": "Juan",
                "last_name": "Pérez",
                "phone": "+1234567890",
                "company_name": "Mi Empresa S.A.",
                "company_slug": "mi-empresa",
                "industry": "technology",
                "plan": "basic"
            }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            # Crear usuario y tenant
            result = serializer.save()

            # Generar tokens JWT para login automático
            user = result["user"]
            refresh = RefreshToken.for_user(user)

            # Preparar respuesta
            response_data = serializer.to_representation(result)
            response_data["tokens"] = {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"error": f"Error al crear la cuenta: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
