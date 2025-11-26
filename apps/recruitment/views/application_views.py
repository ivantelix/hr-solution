"""
ViewSet para Application.

Este módulo contiene el ViewSet para gestión de postulaciones.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.request import Request

from apps.recruitment.models import Application
from apps.recruitment.services import ApplicationService
from apps.recruitment.serializers import (
    ApplicationSerializer,
    ApplicationCreateSerializer,
)


class ApplicationViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de postulaciones."""

    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]
    service = ApplicationService()

    def get_permissions(self):
        """Permite creación pública (postulación externa)."""
        if self.action == 'create':
            return [AllowAny()]
        return super().get_permissions()

    def get_queryset(self):
        """Filtra postulaciones por tenant."""
        if not hasattr(self.request, 'tenant_id'):
            return Application.objects.none()
        return Application.objects.filter(tenant_id=self.request.tenant_id)

    def get_serializer_class(self):
        if self.action == 'create':
            return ApplicationCreateSerializer
        return ApplicationSerializer

    def create(self, request: Request) -> Response:
        """Registra una nueva postulación (público)."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        vacancy_id = data.pop('vacancy_id')
        source = data.pop('source', 'website')

        try:
            application = self.service.apply_to_vacancy(
                vacancy_id=vacancy_id,
                candidate_data=data,
                source=source
            )
            return Response(
                ApplicationSerializer(application).data,
                status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Actualiza el estado de una postulación."""
        new_status = request.data.get('status')
        notes = request.data.get('notes')

        if not new_status:
            return Response(
                {'error': 'Status requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        application = self.service.update_status(
            application_id=pk,
            new_status=new_status,
            notes=notes
        )

        if not application:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(ApplicationSerializer(application).data)
