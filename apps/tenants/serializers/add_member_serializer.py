"""
Serializer para agregar miembros a un tenant.

Este módulo maneja la validación para agregar nuevos miembros
a un tenant.
"""

from rest_framework import serializers

from apps.tenants.models import TenantRole


class AddMemberSerializer(serializers.Serializer):
    """
    Serializer para agregar un miembro a un tenant.

    Valida los datos necesarios para agregar un nuevo miembro
    a un tenant.
    """

    user_id = serializers.IntegerField(
        required=True, help_text="ID del usuario a agregar"
    )

    role = serializers.ChoiceField(
        choices=TenantRole.choices,
        default=TenantRole.MEMBER,
        help_text="Rol del usuario en el tenant",
    )

    def validate_user_id(self, value: int) -> int:
        """
        Valida que el user_id sea válido.

        Args:
            value: ID del usuario.

        Returns:
            int: ID validado.

        Raises:
            ValidationError: Si el ID es inválido.
        """
        if value < 1:
            raise serializers.ValidationError(
                "El ID del usuario debe ser un número positivo."
            )
        return value
