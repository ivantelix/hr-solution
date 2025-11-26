"""
Serializer para lectura de usuarios.

Este módulo contiene el serializer principal para operaciones
de lectura (GET) del modelo User.
"""

from rest_framework import serializers
from apps.users.models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer para lectura de usuarios.

    Proporciona una representación completa del usuario para
    operaciones de lectura (GET).
    """

    full_name = serializers.SerializerMethodField()
    active_tenants_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'phone',
            'avatar',
            'is_email_verified',
            'is_active',
            'is_staff',
            'date_joined',
            'last_login',
            'active_tenants_count',
        ]
        read_only_fields = [
            'id',
            'is_active',
            'is_staff',
            'date_joined',
            'last_login',
        ]

    def get_full_name(self, obj: User) -> str:
        """
        Obtiene el nombre completo del usuario.

        Args:
            obj: Instancia del usuario.

        Returns:
            str: Nombre completo del usuario.
        """
        return obj.get_full_name()

    def get_active_tenants_count(self, obj: User) -> int:
        """
        Obtiene el número de tenants activos del usuario.

        Args:
            obj: Instancia del usuario.

        Returns:
            int: Número de tenants activos.
        """
        return obj.get_active_tenants().count()
