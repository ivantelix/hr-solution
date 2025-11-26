"""
Serializer para actualización de usuarios.

Este módulo maneja la actualización de campos del perfil del usuario,
excluyendo campos sensibles como username y password.
"""

from rest_framework import serializers
from apps.users.models import User


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para actualización de usuarios.

    Permite actualizar campos del perfil del usuario,
    excluyendo campos sensibles como username y password.
    """

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'phone',
            'avatar',
        ]

    def validate_phone(self, value: str | None) -> str | None:
        """
        Valida el formato del teléfono.

        Args:
            value: Número de teléfono.

        Returns:
            str | None: Teléfono validado.

        Note:
            Aquí puedes agregar validación de formato específico
            según tus necesidades (ej: regex para formato
            internacional).
        """
        if value and len(value) < 7:
            raise serializers.ValidationError(
                "El número de teléfono debe tener al menos "
                "7 caracteres."
            )
        return value
