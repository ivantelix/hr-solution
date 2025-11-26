"""
Serializer para lectura de Tenant.

Este módulo contiene el serializer principal para operaciones
de lectura (GET) del modelo Tenant.
"""

from rest_framework import serializers
from apps.tenants.models import Tenant


class TenantSerializer(serializers.ModelSerializer):
    """
    Serializer para lectura de tenants.

    Proporciona una representación completa del tenant para
    operaciones de lectura (GET).
    """

    active_members_count = serializers.SerializerMethodField()
    can_add_members = serializers.SerializerMethodField()
    plan_display = serializers.CharField(
        source='get_plan_display',
        read_only=True
    )

    class Meta:
        model = Tenant
        fields = [
            'id',
            'name',
            'slug',
            'plan',
            'plan_display',
            'is_active',
            'max_users',
            'active_members_count',
            'can_add_members',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
        ]

    def get_active_members_count(self, obj: Tenant) -> int:
        """
        Obtiene el número de miembros activos del tenant.

        Args:
            obj: Instancia del tenant.

        Returns:
            int: Número de miembros activos.
        """
        return obj.get_active_members_count()

    def get_can_add_members(self, obj: Tenant) -> bool:
        """
        Verifica si se pueden agregar más miembros al tenant.

        Args:
            obj: Instancia del tenant.

        Returns:
            bool: True si se pueden agregar más miembros.
        """
        return obj.can_add_member()
