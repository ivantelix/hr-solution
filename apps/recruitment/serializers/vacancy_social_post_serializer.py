"""Serializer para VacancySocialPost."""

from rest_framework import serializers

from apps.recruitment.models import VacancySocialPost


class VacancySocialPostSerializer(serializers.ModelSerializer):
    """Serializer para el modelo VacancySocialPost."""

    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )
    platform_display = serializers.CharField(
        source="get_platform_display", read_only=True
    )

    class Meta:
        model = VacancySocialPost
        fields = [
            "id",
            "vacancy",
            "platform",
            "platform_display",
            "content",
            "status",
            "status_display",
            "posted_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "vacancy",
            # Usually generated via nested logic or separate endpoint,
            # but keeping RO for now in this serializer
            "status",   # Controlled by system actions (publish/schedule)
            "posted_at",
            "created_at",
            "updated_at",
        ]
