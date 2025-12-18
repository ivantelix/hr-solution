"""
Serializer para creación de usuarios.

Este módulo maneja la validación y creación de nuevos usuarios,
incluyendo el hash de contraseñas y validaciones de unicidad.
"""

from rest_framework import serializers

from apps.users.models import User


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para creación de usuarios.

    Maneja la validación y creación de nuevos usuarios,
    incluyendo el hash de contraseñas.
    """

    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        min_length=8,
        help_text="Contraseña (mínimo 8 caracteres)",
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        help_text="Confirmación de contraseña",
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "phone",
        ]

    def validate_email(self, value: str) -> str:
        """
        Valida que el email sea único.

        Args:
            value: Email a validar.

        Returns:
            str: Email validado.

        Raises:
            ValidationError: Si el email ya está en uso.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email ya está registrado.")
        return value.lower()

    def validate_username(self, value: str) -> str:
        """
        Valida que el username sea único.

        Args:
            value: Username a validar.

        Returns:
            str: Username validado.

        Raises:
            ValidationError: Si el username ya está en uso.
        """
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este nombre de usuario ya está en uso.")
        return value

    def validate(self, attrs: dict) -> dict:
        """
        Valida que las contraseñas coincidan.

        Args:
            attrs: Atributos a validar.

        Returns:
            dict: Atributos validados.

        Raises:
            ValidationError: Si las contraseñas no coinciden.
        """
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Las contraseñas no coinciden."}
            )
        return attrs

    def create(self, validated_data: dict) -> User:
        """
        Crea un nuevo usuario con contraseña hasheada.

        Args:
            validated_data: Datos validados del usuario.

        Returns:
            User: Usuario creado.
        """
        # Remover password_confirm
        validated_data.pop("password_confirm")

        # Crear usuario con contraseña hasheada
        user = User.objects.create_user(**validated_data)

        return user
