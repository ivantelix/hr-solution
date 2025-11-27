"""
Modelo TenantAIConfig.

Este módulo contiene el modelo de configuración de IA para cada tenant,
permitiendo BYOK (Bring Your Own Key) y selección de proveedor LLM.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from .tenant_model import Tenant
from .choices import AIProvider


class TenantAIConfig(models.Model):
    """
    Configuración de IA para un tenant.

    Permite a cada tenant configurar su propio proveedor de IA
    y API Key (BYOK - Bring Your Own Key), proporcionando
    independencia y control sobre los costos de IA.

    Attributes:
        tenant (OneToOne): Tenant al que pertenece la configuración.
        provider (str): Proveedor de IA seleccionado.
        api_key (str): API Key del proveedor (encriptada).
        model_name (str): Nombre del modelo específico a usar.
        temperature (float): Temperatura para generación de texto.
        max_tokens (int): Máximo de tokens por request.
        is_active (bool): Indica si la configuración está activa.
        created_at (datetime): Fecha de creación.
        updated_at (datetime): Fecha de última actualización.

    Note:
        La API Key debe ser encriptada antes de guardarla en la BD.
        Considerar usar django-encrypted-model-fields o similar.
    """

    tenant = models.OneToOneField(
        Tenant,
        on_delete=models.CASCADE,
        related_name="ai_config",
        verbose_name="Tenant"
    )

    provider = models.CharField(
        max_length=20,
        choices=AIProvider.choices,
        default=AIProvider.OPENAI,
        verbose_name="Proveedor de IA",
        help_text="Proveedor de IA a utilizar"
    )

    api_key = models.CharField(
        max_length=500,
        verbose_name="API Key",
        help_text="API Key del proveedor (será encriptada)"
    )

    model_name = models.CharField(
        max_length=100,
        default="gpt-4",
        verbose_name="Nombre del Modelo",
        help_text="Modelo específico a usar (ej: gpt-4, claude-3)"
    )

    temperature = models.FloatField(
        default=0.7,
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(2.0)
        ],
        verbose_name="Temperatura",
        help_text="Controla la creatividad (0.0 - 2.0)"
    )

    max_tokens = models.PositiveIntegerField(
        default=2000,
        validators=[MinValueValidator(1)],
        verbose_name="Máximo de Tokens",
        help_text="Máximo de tokens por request"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Activo",
        help_text="Indica si la configuración está activa"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de Actualización"
    )

    class Meta:
        verbose_name = "Configuración de IA"
        verbose_name_plural = "Configuraciones de IA"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        """
        Representación en string de la configuración.

        Returns:
            str: Descripción de la configuración.
        """
        return f"{self.tenant.name} - {self.get_provider_display()}"

    def get_safe_api_key(self) -> str:
        """
        Obtiene una versión parcialmente oculta de la API Key.

        Returns:
            str: API Key con caracteres ocultos (ej: sk-***xyz).

        Note:
            Útil para mostrar en UI sin exponer la key completa.
        """
        if len(self.api_key) <= 10:
            return "***"
        return f"{self.api_key[:3]}***{self.api_key[-3:]}"

    def update_api_key(self, new_api_key: str) -> None:
        """
        Actualiza la API Key de forma segura.

        Args:
            new_api_key: Nueva API Key a configurar.

        Note:
            Aquí se debe implementar la encriptación de la key
            antes de guardarla.
        """
        # TODO: Implementar encriptación
        self.api_key = new_api_key
        self.save(update_fields=["api_key", "updated_at"])

    def deactivate(self) -> None:
        """
        Desactiva la configuración de IA.
        """
        self.is_active = False
        self.save(update_fields=["is_active", "updated_at"])

    def activate(self) -> None:
        """
        Activa la configuración de IA.
        """
        self.is_active = True
        self.save(update_fields=["is_active", "updated_at"])
