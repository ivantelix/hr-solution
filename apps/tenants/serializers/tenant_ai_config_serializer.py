"""
Serializer para TenantAIConfig.

Este módulo contiene serializers para la configuración de IA
de los tenants (BYOK).
"""

from rest_framework import serializers

from apps.tenants.models import TenantAIConfig


class TenantAIConfigSerializer(serializers.ModelSerializer):
    """
    Serializer para lectura de configuración de IA.

    Proporciona una representación de la configuración de IA
    con la API Key parcialmente oculta por seguridad.
    """

    provider_display = serializers.CharField(
        source="get_provider_display", read_only=True
    )
    api_key_safe = serializers.SerializerMethodField()

    class Meta:
        model = TenantAIConfig
        fields = [
            "id",
            "tenant",
            "provider",
            "provider_display",
            "api_key_safe",
            "model_name",
            "temperature",
            "max_tokens",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "tenant",
            "created_at",
            "updated_at",
        ]

    def get_api_key_safe(self, obj: TenantAIConfig) -> str:
        """
        Obtiene una versión parcialmente oculta de la API Key.

        Args:
            obj: Instancia de la configuración.

        Returns:
            str: API Key parcialmente oculta.
        """
        return obj.get_safe_api_key()


class TenantAIConfigCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para creación/actualización de configuración de IA.

    Maneja la validación completa de la configuración de IA
    incluyendo la API Key.
    """

    class Meta:
        model = TenantAIConfig
        fields = [
            "provider",
            "api_key",
            "model_name",
            "temperature",
            "max_tokens",
        ]

    def validate_api_key(self, value: str) -> str:
        """
        Valida que la API Key no esté vacía.

        Args:
            value: API Key a validar.

        Returns:
            str: API Key validada.

        Raises:
            ValidationError: Si la API Key está vacía.
        """
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("La API Key no puede estar vacía.")
        return value.strip()

    def validate_temperature(self, value: float) -> float:
        """
        Valida que la temperatura esté en el rango correcto.

        Args:
            value: Temperatura a validar.

        Returns:
            float: Temperatura validada.

        Raises:
            ValidationError: Si está fuera del rango.
        """
        if value < 0.0 or value > 2.0:
            raise serializers.ValidationError(
                "La temperatura debe estar entre 0.0 y 2.0"
            )
        return value

    def validate_max_tokens(self, value: int) -> int:
        """
        Valida que el máximo de tokens sea válido.

        Args:
            value: Máximo de tokens.

        Returns:
            int: Valor validado.

        Raises:
            ValidationError: Si es menor a 1.
        """
        if value < 1:
            raise serializers.ValidationError(
                "El máximo de tokens debe ser al menos 1."
            )
        return value
