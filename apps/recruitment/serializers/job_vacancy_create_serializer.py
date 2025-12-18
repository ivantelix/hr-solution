"""
Serializer para creación de JobVacancy.

Este módulo maneja la validación y creación de vacantes.
"""

from rest_framework import serializers

from apps.recruitment.models import JobVacancy


class JobVacancyCreateSerializer(serializers.ModelSerializer):
    """Serializer para creación de vacantes."""

    class Meta:
        model = JobVacancy
        fields = [
            "title",
            "description",
            "requirements",
            "location",
            "salary_min",
            "salary_max",
            "currency",
            "is_remote",
        ]

    def validate(self, data):
        """Valida rangos de salario."""
        salary_min = data.get("salary_min")
        salary_max = data.get("salary_max")

        if salary_min and salary_max and salary_min > salary_max:
            raise serializers.ValidationError(
                "El salario mínimo no puede ser mayor al máximo."
            )
        return data
