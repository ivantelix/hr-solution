"""
Serializer para creación de Tenant.

Este módulo maneja la validación y creación de nuevos tenants.
"""

from rest_framework import serializers
from django.utils.text import slugify

from apps.tenants.models import Tenant, PlanType


class TenantCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para creación de tenants.

    Maneja la validación y creación de nuevos tenants,
    generando automáticamente el slug si no se proporciona.
    """

    slug = serializers.SlugField(
        required=False,
        allow_blank=True,
        help_text="Slug único (se genera automáticamente si no se "
                  "proporciona)"
    )

    class Meta:
        model = Tenant
        fields = [
            'name',
            'slug',
            'plan',
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
        if value and Tenant.objects.filter(slug=value).exists():
            raise serializers.ValidationError(
                "Este slug ya está en uso."
            )
        return value

    def validate_max_users(self, value: int) -> int:
        """
        Valida que el número máximo de usuarios sea válido.

        Args:
            value: Número máximo de usuarios.

        Returns:
            int: Valor validado.

        Raises:
            ValidationError: Si el valor es inválido.
        """
        if value < 1:
            raise serializers.ValidationError(
                "El máximo de usuarios debe ser al menos 1."
            )
        return value

    def create(self, validated_data: dict) -> Tenant:
        """
        Crea un nuevo tenant con slug auto-generado si es necesario.

        Args:
            validated_data: Datos validados del tenant.

        Returns:
            Tenant: Tenant creado.
        """
        # Generar slug si no se proporcionó
        if not validated_data.get('slug'):
            validated_data['slug'] = slugify(validated_data['name'])

            # Asegurar unicidad del slug
            base_slug = validated_data['slug']
            counter = 1
            while Tenant.objects.filter(
                slug=validated_data['slug']
            ).exists():
                validated_data['slug'] = f"{base_slug}-{counter}"
                counter += 1

        return Tenant.objects.create(**validated_data)
