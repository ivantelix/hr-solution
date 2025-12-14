"""
Middleware de Tenant Isolation.

Este módulo contiene el middleware que intercepta las requests,
extrae el tenant_id del JWT y lo inyecta en el request para
garantizar el aislamiento de datos por tenant.
"""

from collections.abc import Callable

from django.http import HttpRequest, HttpResponse, JsonResponse
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken


class TenantMiddleware:
    """
    Middleware para aislamiento de tenants.

    Intercepta cada request, extrae el tenant_id del JWT token
    y lo inyecta en el request.tenant_id para que esté disponible
    en toda la aplicación.

    Attributes:
        get_response: Callable para obtener la respuesta.

    Note:
        Este middleware debe estar después de AuthenticationMiddleware
        en MIDDLEWARE settings.
    """

    def __init__(self, get_response: Callable):
        """
        Inicializa el middleware.

        Args:
            get_response: Callable para procesar la request.
        """
        self.get_response = get_response
        self.jwt_authenticator = JWTAuthentication()

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        Procesa cada request.

        Args:
            request: Request HTTP entrante.

        Returns:
            HttpResponse: Respuesta HTTP.
        """
        # Extraer tenant_id del JWT si existe
        tenant_id = self._extract_tenant_id(request)

        # Inyectar tenant_id en el request
        request.tenant_id = tenant_id

        # Continuar con el procesamiento normal
        response = self.get_response(request)

        return response

    def _extract_tenant_id(self, request: HttpRequest) -> str | None:
        """
        Extrae el tenant_id del JWT token.

        Args:
            request: Request HTTP.

        Returns:
            str | None: tenant_id si existe en el token, None en
                caso contrario.

        Note:
            El tenant_id debe estar en el payload del JWT como
            'tenant_id' o 'tenant'.
        """
        # Intentar obtener el token del header Authorization
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")

        if not auth_header.startswith("Bearer "):
            return None

        try:
            # Validar y decodificar el token
            validated_token = self.jwt_authenticator.get_validated_token(
                auth_header.split(" ")[1]
            )

            # Extraer tenant_id del payload
            # Puede estar como 'tenant_id' o 'tenant'
            tenant_id = validated_token.get("tenant_id") or validated_token.get(
                "tenant"
            )

            return str(tenant_id) if tenant_id else None

        except (InvalidToken, IndexError, KeyError):
            # Token inválido o no presente
            return None


class TenantRequiredMiddleware:
    """
    Middleware que requiere tenant_id en requests autenticados.

    Valida que todas las requests autenticadas (excepto las
    excluidas) tengan un tenant_id válido.

    Note:
        Este middleware debe estar DESPUÉS de TenantMiddleware.
    """

    # Paths que no requieren tenant_id
    EXCLUDED_PATHS = [
        "/api/users/",  # Registro de usuarios
        "/api/auth/",  # Autenticación
        "/admin/",  # Django admin
        "/api/docs/",  # Documentación API
    ]

    def __init__(self, get_response: Callable):
        """
        Inicializa el middleware.

        Args:
            get_response: Callable para procesar la request.
        """
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        Procesa cada request validando tenant_id.

        Args:
            request: Request HTTP entrante.

        Returns:
            HttpResponse: Respuesta HTTP o error si falta tenant_id.
        """
        # Verificar si el path está excluido
        if self._is_excluded_path(request.path):
            return self.get_response(request)

        # Verificar si el usuario está autenticado
        if not hasattr(request, "user") or not request.user.is_authenticated:
            return self.get_response(request)

        # Verificar que tenga tenant_id
        if not hasattr(request, "tenant_id") or not request.tenant_id:
            return JsonResponse(
                {
                    "error": "Tenant ID requerido",
                    "detail": "Esta operación requiere un tenant válido.",
                },
                status=403,
            )

        return self.get_response(request)

    def _is_excluded_path(self, path: str) -> bool:
        """
        Verifica si un path está excluido de la validación.

        Args:
            path: Path de la request.

        Returns:
            bool: True si el path está excluido.
        """
        return any(path.startswith(excluded) for excluded in self.EXCLUDED_PATHS)
