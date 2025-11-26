"""
Serializer para actualización de Tenant.

Este módulo maneja la actualización de campos del tenant.
"""

from rest_framework import serializers
from apps.tenants.models import Tenant


class TenantUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para actualización de tenants.

    Permite actualizar campos del tenant, excluyendo campos
    sensibles como el plan.
    """

    class Meta:
        model = Tenant
        fields = [
            'name',
            'slug',
            'max_users',
        ]

    def validate_slug(self, value: str) -> str:
        """
        Valida que el slug sea único.

        Args:
            value: Slug a validar.

        Returns:
            str: Slug validado.

        Raises:
            ValidationError: Si el slug ya está en uso.
        """
        tenant = self.instance
        if Tenant.objects.filter(slug=value).exclude(
            id=tenant.id
        ).exists():
            raise serializers.ValidationError(
                "Este slug ya está en uso."
            )
        return value

    def validate_max_users(self, value: int) -> int:
        """
        Valida que el nuevo límite no sea menor al número actual
        de miembros.

        Args:
            value: Nuevo límite de usuarios.

        Returns:
            int: Valor validado.

        Raises:
            ValidationError: Si el límite es menor al número actual
                de miembros.
        """
        tenant = self.instance
        current_members = tenant.get_active_members_count()

        if value < current_members:
            raise serializers.ValidationError(
                f"No se puede reducir el límite a {value} usuarios. "
                f"Actualmente hay {current_members} miembros activos."
            )

        return value
