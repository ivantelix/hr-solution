"""
Serializer para JobVacancy.

Este módulo contiene el serializer para lectura de vacantes.
"""

from rest_framework import serializers

from apps.recruitment.models import JobVacancy


from .vacancy_social_post_serializer import VacancySocialPostSerializer


class JobVacancySerializer(serializers.ModelSerializer):
    """Serializer para lectura de vacantes."""

    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )

    created_by_name = serializers.CharField(
        source="created_by.get_full_name", read_only=True
    )
    social_posts = VacancySocialPostSerializer(many=True, read_only=True)
    interview_mode_display = serializers.CharField(
        source="get_interview_mode_display", read_only=True
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
            "interview_mode",
            "interview_mode_display",
            "social_posts",
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
            "manual_interview_guide",
        ]
        read_only_fields = [
            "id",
            "tenant",
            "created_by",
            "created_at",
            "updated_at",
            "closed_at",
            "social_posts",
        ]
