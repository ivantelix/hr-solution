"""
Serializer para Candidate.

Este módulo contiene el serializer para lectura de candidatos.
"""

from rest_framework import serializers
from apps.recruitment.models import Candidate


class CandidateSerializer(serializers.ModelSerializer):
    """Serializer para lectura de candidatos."""

    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Candidate
        fields = [
            'id',
            'tenant',
            'first_name',
            'last_name',
            'full_name',
            'email',
            'phone',
            'linkedin_url',
            'resume_url',
            'skills',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'tenant',
            'created_at',
            'updated_at',
        ]
