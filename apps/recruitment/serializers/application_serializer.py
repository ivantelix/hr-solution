"""
Serializer para Application.

Este módulo contiene el serializer para lectura de postulaciones.
"""

from rest_framework import serializers

from apps.recruitment.models import Application

from .candidate_serializer import CandidateSerializer
from .job_vacancy_serializer import JobVacancySerializer


class ApplicationSerializer(serializers.ModelSerializer):
    """Serializer para lectura de postulaciones."""

    candidate = CandidateSerializer(read_only=True)
    vacancy = JobVacancySerializer(read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Application
        fields = [
            "id",
            "tenant",
            "vacancy",
            "candidate",
            "status",
            "status_display",
            "source",
            "score",
            "notes",
            "applied_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "tenant",
            "applied_at",
            "updated_at",
        ]
