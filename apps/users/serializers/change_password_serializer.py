"""
Serializer para cambio de contraseña.

Este módulo maneja la validación y procesamiento del cambio
de contraseña de un usuario.
"""

from rest_framework import serializers


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer para cambio de contraseña.

    Valida y procesa el cambio de contraseña de un usuario.
    """

    old_password = serializers.CharField(
        required=True, write_only=True, style={"input_type": "password"}
    )
    new_password = serializers.CharField(
        required=True, write_only=True, min_length=8, style={"input_type": "password"}
    )
    new_password_confirm = serializers.CharField(
        required=True, write_only=True, style={"input_type": "password"}
    )

    def validate(self, attrs: dict) -> dict:
        """
        Valida que las nuevas contraseñas coincidan.

        Args:
            attrs: Atributos a validar.

        Returns:
            dict: Atributos validados.

        Raises:
            ValidationError: Si las contraseñas no coinciden.
        """
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": "Las contraseñas no coinciden."}
            )
        return attrs
