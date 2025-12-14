"""
Serializer para JobVacancy.

Este módulo contiene el serializer para lectura de vacantes.
"""

from rest_framework import serializers

from apps.recruitment.models import JobVacancy


class JobVacancySerializer(serializers.ModelSerializer):
    """Serializer para lectura de vacantes."""

    status_display = serializers.CharField(source="get_status_display", read_only=True)
    created_by_name = serializers.CharField(
        source="created_by.get_full_name", read_only=True
    )

    class Meta:
        model = JobVacancy
        fields = [
            "id",
            "tenant",
            "title",
            "description",
            "requirements",
            "status",
            "status_display",
            "location",
            "salary_min",
            "salary_max",
            "currency",
            "is_remote",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
            "closed_at",
        ]
        read_only_fields = [
            "id",
            "tenant",
            "created_by",
            "created_at",
            "updated_at",
            "closed_at",
        ]
