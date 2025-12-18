"""
Serializer para actualización de email.

Este módulo maneja la validación y procesamiento del cambio
de email de un usuario.
"""

from rest_framework import serializers

from apps.users.models import User


class UpdateEmailSerializer(serializers.Serializer):
    """
    Serializer para actualización de email.

    Valida y procesa el cambio de email de un usuario.
    """

    new_email = serializers.EmailField(required=True)

    def validate_new_email(self, value: str) -> str:
        """
        Valida que el nuevo email sea único.

        Args:
            value: Nuevo email.

        Returns:
            str: Email validado.

        Raises:
            ValidationError: Si el email ya está en uso.
        """
        user = self.context.get("request").user
        if User.objects.filter(email=value).exclude(id=user.id).exists():
            raise serializers.ValidationError("Este email ya está en uso.")
        return value.lower()
