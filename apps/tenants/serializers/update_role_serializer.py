"""
Serializer para actualizar el rol de un miembro.

Este módulo maneja la validación para actualizar el rol
de un miembro en un tenant.
"""

from rest_framework import serializers

from apps.tenants.models import TenantRole


class UpdateRoleSerializer(serializers.Serializer):
    """
    Serializer para actualizar el rol de un miembro.

    Valida el nuevo rol a asignar a un miembro del tenant.
    """

    role = serializers.ChoiceField(
        choices=TenantRole.choices, required=True, help_text="Nuevo rol a asignar"
    )
