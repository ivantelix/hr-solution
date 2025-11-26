"""
Serializer para creación de Application.

Este módulo maneja la creación de postulaciones y candidatos.
"""

from rest_framework import serializers


class ApplicationCreateSerializer(serializers.Serializer):
    """
    Serializer para crear postulación.

    Recibe datos del candidato y el ID de la vacante.
    """

    vacancy_id = serializers.IntegerField(required=True)
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20, required=False)
    linkedin_url = serializers.URLField(required=False)
    resume_url = serializers.URLField(required=False)
    source = serializers.CharField(default="website")
