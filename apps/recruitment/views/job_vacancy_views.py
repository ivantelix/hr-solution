"""
ViewSet para JobVacancy.

Este módulo contiene el ViewSet para gestión de vacantes.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request

from apps.recruitment.models import JobVacancy
from apps.recruitment.services import JobVacancyService
from apps.recruitment.serializers import (
    JobVacancySerializer,
    JobVacancyCreateSerializer,
)


class JobVacancyViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de vacantes."""

    serializer_class = JobVacancySerializer
    permission_classes = [IsAuthenticated]
    service = JobVacancyService()

    def get_queryset(self):
        """Filtra vacantes por tenant del usuario."""
        if not hasattr(self.request, 'tenant_id'):
            return JobVacancy.objects.none()
        return self.service.get_tenant_vacancies(self.request.tenant_id)

    def get_serializer_class(self):
        if self.action == 'create':
            return JobVacancyCreateSerializer
        return JobVacancySerializer

    def create(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            vacancy = self.service.create_vacancy(
                tenant_id=request.tenant_id,
                user_id=request.user.id,
                **serializer.validated_data
            )
            return Response(
                JobVacancySerializer(vacancy).data,
                status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publica una vacante."""
        vacancy = self.service.publish_vacancy(pk)
        if not vacancy:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(JobVacancySerializer(vacancy).data)

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Cierra una vacante."""
        vacancy = self.service.close_vacancy(pk)
        if not vacancy:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(JobVacancySerializer(vacancy).data)
