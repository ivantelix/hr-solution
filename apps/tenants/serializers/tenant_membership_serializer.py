"""
Serializer para TenantMembership.

Este módulo contiene el serializer para operaciones de lectura
de membresías de tenant.
"""

from rest_framework import serializers
from apps.tenants.models import TenantMembership
from apps.users.serializers import UserSerializer


class TenantMembershipSerializer(serializers.ModelSerializer):
    """
    Serializer para lectura de membresías de tenant.

    Proporciona una representación completa de la membresía
    incluyendo información del usuario.
    """

    user = UserSerializer(read_only=True)
    tenant_name = serializers.CharField(
        source='tenant.name',
        read_only=True
    )
    role_display = serializers.CharField(
        source='get_role_display',
        read_only=True
    )
    is_admin_user = serializers.SerializerMethodField()

    class Meta:
        model = TenantMembership
        fields = [
            'id',
            'tenant',
            'tenant_name',
            'user',
            'role',
            'role_display',
            'is_active',
            'is_admin_user',
            'joined_at',
            'invited_by',
        ]
        read_only_fields = [
            'id',
            'joined_at',
        ]

    def get_is_admin_user(self, obj: TenantMembership) -> bool:
        """
        Verifica si el usuario es administrador.

        Args:
            obj: Instancia de la membresía.

        Returns:
            bool: True si el usuario es admin.
        """
        return obj.is_admin()
