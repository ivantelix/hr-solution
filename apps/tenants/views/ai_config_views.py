"""
ViewSet para TenantAIConfig.

Este módulo contiene el ViewSet para gestionar la configuración de IA
de los tenants.
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.tenants.models import TenantAIConfig
from apps.tenants.serializers import (
    TenantAIConfigCreateSerializer,
    TenantAIConfigSerializer,
)
from apps.tenants.services import TenantAIConfigService


class TenantAIConfigViewSet(viewsets.GenericViewSet):
    """
    ViewSet para configuración de IA del tenant.

    Proporciona endpoints para configurar, actualizar y gestionar
    la configuración de IA de un tenant específico.
    """

    permission_classes = [IsAuthenticated]
    service = TenantAIConfigService()

    def get_serializer_class(self):
        """
        Obtiene el serializer según la acción.

        Returns:
            Serializer: Clase de serializer apropiada.
        """
        if self.action in ["create", "update", "partial_update"]:
            return TenantAIConfigCreateSerializer
        return TenantAIConfigSerializer

    def get_queryset(self):
        """
        Retorna queryset vacío ya que usamos el servicio.
        Necesario para compatibilidad con DRF.
        """
        return TenantAIConfig.objects.none()

    def _get_tenant_id(self):
        """
        Obtiene el ID del tenant desde los kwargs de la URL.

        Returns:
            str: ID del tenant.

        Raises:
            ValidationError: Si no se provee el tenant_id.
        """
        tenant_id = self.kwargs.get("tenant_id")
        if not tenant_id:
            raise ValidationError("Tenant ID es requerido.")
        return tenant_id

    def list(self, request: Request, tenant_id=None) -> Response:
        """
        Obtiene la configuración de IA del tenant.
        Mapeado a GET /.

        Args:
            request: Request.
            tenant_id: ID del tenant.

        Returns:
            Response: Configuración o 404 si no existe.
        """
        config = self.service.get_ai_config(tenant_id)
        if not config:
            raise NotFound("Configuración de IA no encontrada para este tenant.")

        serializer = self.get_serializer(config)
        return Response(serializer.data)

    def create(self, request: Request, tenant_id=None) -> Response:
        """
        Crea o actualiza la configuración de IA.
        Mapeado a POST /.

        Args:
            request: Request con datos de configuración.
            tenant_id: ID del tenant.

        Returns:
            Response: Configuración creada/actualizada.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            config = self.service.configure_ai(
                tenant_id=tenant_id,
                provider=serializer.validated_data["provider"],
                api_key=serializer.validated_data["api_key"],
                model_name=serializer.validated_data.get("model_name", "gpt-4"),
                temperature=serializer.validated_data.get("temperature", 0.7),
                max_tokens=serializer.validated_data.get("max_tokens", 2000),
            )

            # Usar serializer de lectura para la respuesta
            read_serializer = TenantAIConfigSerializer(config)
            return Response(
                read_serializer.data, status=status.HTTP_201_CREATED
            )

        except ValueError as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=["post"])
    def activate(self, request: Request, tenant_id=None) -> Response:
        """
        Activa la configuración de IA.

        Args:
            request: Request.
            tenant_id: ID del tenant.

        Returns:
            Response: Configuración actualizada.
        """
        config = self.service.activate_ai_config(tenant_id)
        if not config:
            raise NotFound("Configuración no encontrada.")

        return Response(TenantAIConfigSerializer(config).data)

    @action(detail=False, methods=["post"])
    def deactivate(self, request: Request, tenant_id=None) -> Response:
        """
        Desactiva la configuración de IA.

        Args:
            request: Request.
            tenant_id: ID del tenant.

        Returns:
            Response: Configuración actualizada.
        """
        config = self.service.deactivate_ai_config(tenant_id)
        if not config:
            raise NotFound("Configuración no encontrada.")

        return Response(TenantAIConfigSerializer(config).data)
