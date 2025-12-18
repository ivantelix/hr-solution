"""
Serializer para invitación de usuarios.
"""

from rest_framework import serializers

from apps.tenants.models.choices import TenantRole


class InviteUserSerializer(serializers.Serializer):
    """
    Serializer para invitar usuarios a un tenant.
    """

    email = serializers.EmailField(
        help_text="Correo electrónico del usuario a invitar"
    )
    first_name = serializers.CharField(
        max_length=150, required=False, help_text="Nombre del usuario"
    )
    last_name = serializers.CharField(
        max_length=150, required=False, help_text="Apellido del usuario"
    )
    role = serializers.ChoiceField(
        choices=TenantRole.choices,
        default=TenantRole.MEMBER,
        help_text="Rol que tendrá el usuario en el tenant",
    )

    def validate_role(self, value):
        """El rol OWNER no se puede asignar por invitación normal."""
        if value == TenantRole.OWNER:
            raise serializers.ValidationError(
                "No se puede invitar con rol de Dueño."
            )
        return value
