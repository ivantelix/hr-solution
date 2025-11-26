"""
ViewSet para Tenant.

Este módulo contiene el ViewSet de Django Rest Framework
para el modelo Tenant, proporcionando endpoints REST.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request

from apps.tenants.models import Tenant
from apps.tenants.services import TenantService
from apps.tenants.serializers import (
    TenantSerializer,
    TenantCreateSerializer,
    TenantUpdateSerializer,
)


class TenantViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de tenants.

    Proporciona endpoints REST para operaciones CRUD sobre tenants,
    delegando la lógica de negocio al TenantService.

    Endpoints:
        - GET /tenants/ - Lista de tenants del usuario
        - POST /tenants/ - Crear tenant
        - GET /tenants/{id}/ - Detalle de tenant
        - PUT /tenants/{id}/ - Actualizar tenant completo
        - PATCH /tenants/{id}/ - Actualizar tenant parcial
        - DELETE /tenants/{id}/ - Eliminar tenant
        - POST /tenants/{id}/deactivate/ - Desactivar tenant
        - POST /tenants/{id}/activate/ - Activar tenant
    """

    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [IsAuthenticated]
    service = TenantService()

    def get_queryset(self):
        """
        Filtra los tenants según el usuario autenticado.

        Returns:
            QuerySet: Tenants del usuario.
        """
        user = self.request.user
        return Tenant.objects.filter(
            tenantmembership__user=user,
            tenantmembership__is_active=True
        ).distinct()

    def get_serializer_class(self):
        """
        Obtiene el serializer según la acción.

        Returns:
            Serializer: Clase de serializer apropiada.
        """
        if self.action == 'create':
            return TenantCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TenantUpdateSerializer
        return TenantSerializer

    def create(self, request: Request) -> Response:
        """
        Crea un nuevo tenant.

        Args:
            request: Request con datos del tenant.

        Returns:
            Response: Tenant creado o errores de validación.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            tenant = self.service.create_tenant(
                **serializer.validated_data
            )

            return Response(
                TenantSerializer(tenant).data,
                status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request: Request, pk=None) -> Response:
        """
        Actualiza un tenant completo.

        Args:
            request: Request con datos actualizados.
            pk: ID del tenant.

        Returns:
            Response: Tenant actualizado o error.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            tenant = self.service.update_tenant(
                tenant_id=pk,
                **serializer.validated_data
            )

            if not tenant:
                return Response(
                    {'error': 'Tenant no encontrado'},
                    status=status.HTTP_404_NOT_FOUND
                )

            return Response(
                TenantSerializer(tenant).data,
                status=status.HTTP_200_OK
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def partial_update(
        self,
        request: Request,
        pk=None
    ) -> Response:
        """
        Actualiza parcialmente un tenant.

        Args:
            request: Request con datos actualizados.
            pk: ID del tenant.

        Returns:
            Response: Tenant actualizado o error.
        """
        serializer = self.get_serializer(
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)

        try:
            tenant = self.service.update_tenant(
                tenant_id=pk,
                **serializer.validated_data
            )

            if not tenant:
                return Response(
                    {'error': 'Tenant no encontrado'},
                    status=status.HTTP_404_NOT_FOUND
                )

            return Response(
                TenantSerializer(tenant).data,
                status=status.HTTP_200_OK
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def deactivate(self, request: Request, pk=None) -> Response:
        """
        Desactiva un tenant.

        Args:
            request: Request.
            pk: ID del tenant.

        Returns:
            Response: Confirmación o error.
        """
        tenant = self.service.deactivate_tenant(tenant_id=pk)

        if not tenant:
            return Response(
                {'error': 'Tenant no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {'message': 'Tenant desactivado exitosamente'},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def activate(self, request: Request, pk=None) -> Response:
        """
        Activa un tenant previamente desactivado.

        Args:
            request: Request.
            pk: ID del tenant.

        Returns:
            Response: Confirmación o error.
        """
        tenant = self.service.activate_tenant(tenant_id=pk)

        if not tenant:
            return Response(
                {'error': 'Tenant no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {'message': 'Tenant activado exitosamente'},
            status=status.HTTP_200_OK
        )
