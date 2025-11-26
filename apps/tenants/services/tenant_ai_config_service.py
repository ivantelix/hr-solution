"""
Servicio de aplicación para TenantAIConfig.

Este módulo contiene los casos de uso relacionados con la
configuración de IA de los tenants (BYOK).
"""

from typing import Any
from django.db import transaction

from apps.tenants.models import TenantAIConfig, AIProvider
from apps.tenants.repositories import TenantRepository


class TenantAIConfigService:
    """
    Servicio de aplicación para configuración de IA de tenants.

    Implementa los casos de uso relacionados con la configuración
    de proveedores de IA y API Keys (BYOK - Bring Your Own Key).

    Attributes:
        tenant_repository: Repositorio de tenants.
    """

    def __init__(
        self,
        tenant_repository: TenantRepository | None = None
    ):
        """
        Inicializa el servicio con el repositorio.

        Args:
            tenant_repository: Repositorio de tenants.
        """
        self.tenant_repository = (
            tenant_repository or TenantRepository()
        )

    @transaction.atomic
    def configure_ai(
        self,
        tenant_id: str,
        provider: AIProvider,
        api_key: str,
        model_name: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> TenantAIConfig:
        """
        Configura o actualiza la configuración de IA de un tenant.

        Args:
            tenant_id: ID del tenant.
            provider: Proveedor de IA.
            api_key: API Key del proveedor.
            model_name: Nombre del modelo a usar.
            temperature: Temperatura para generación.
            max_tokens: Máximo de tokens por request.

        Returns:
            TenantAIConfig: Configuración creada o actualizada.

        Raises:
            ValueError: Si el tenant no existe o los parámetros
                son inválidos.
        """
        # Validar que el tenant exista
        tenant = self.tenant_repository.get_by_id(tenant_id)
        if not tenant:
            raise ValueError("El tenant no existe.")

        # Validar parámetros
        if temperature < 0.0 or temperature > 2.0:
            raise ValueError(
                "La temperatura debe estar entre 0.0 y 2.0"
            )

        if max_tokens < 1:
            raise ValueError(
                "El máximo de tokens debe ser al menos 1"
            )

        # Verificar si ya existe configuración
        try:
            config = tenant.ai_config
            # Actualizar configuración existente
            config.provider = provider
            config.update_api_key(api_key)
            config.model_name = model_name
            config.temperature = temperature
            config.max_tokens = max_tokens
            config.is_active = True
            config.save()
        except TenantAIConfig.DoesNotExist:
            # Crear nueva configuración
            config = TenantAIConfig.objects.create(
                tenant=tenant,
                provider=provider,
                api_key=api_key,
                model_name=model_name,
                temperature=temperature,
                max_tokens=max_tokens
            )

        return config

    @transaction.atomic
    def update_api_key(
        self,
        tenant_id: str,
        new_api_key: str
    ) -> TenantAIConfig | None:
        """
        Actualiza la API Key de un tenant.

        Args:
            tenant_id: ID del tenant.
            new_api_key: Nueva API Key.

        Returns:
            TenantAIConfig | None: Configuración actualizada o None
                si no existe.
        """
        tenant = self.tenant_repository.get_by_id(tenant_id)
        if not tenant:
            return None

        try:
            config = tenant.ai_config
            config.update_api_key(new_api_key)
            return config
        except TenantAIConfig.DoesNotExist:
            return None

    @transaction.atomic
    def update_model_settings(
        self,
        tenant_id: str,
        model_name: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None
    ) -> TenantAIConfig | None:
        """
        Actualiza la configuración del modelo de IA.

        Args:
            tenant_id: ID del tenant.
            model_name: Nombre del modelo (opcional).
            temperature: Temperatura (opcional).
            max_tokens: Máximo de tokens (opcional).

        Returns:
            TenantAIConfig | None: Configuración actualizada o None
                si no existe.

        Raises:
            ValueError: Si los parámetros son inválidos.
        """
        tenant = self.tenant_repository.get_by_id(tenant_id)
        if not tenant:
            return None

        try:
            config = tenant.ai_config

            if model_name is not None:
                config.model_name = model_name

            if temperature is not None:
                if temperature < 0.0 or temperature > 2.0:
                    raise ValueError(
                        "La temperatura debe estar entre 0.0 y 2.0"
                    )
                config.temperature = temperature

            if max_tokens is not None:
                if max_tokens < 1:
                    raise ValueError(
                        "El máximo de tokens debe ser al menos 1"
                    )
                config.max_tokens = max_tokens

            config.save()
            return config

        except TenantAIConfig.DoesNotExist:
            return None

    @transaction.atomic
    def change_provider(
        self,
        tenant_id: str,
        new_provider: AIProvider,
        new_api_key: str,
        new_model_name: str
    ) -> TenantAIConfig | None:
        """
        Cambia el proveedor de IA de un tenant.

        Args:
            tenant_id: ID del tenant.
            new_provider: Nuevo proveedor de IA.
            new_api_key: API Key del nuevo proveedor.
            new_model_name: Nombre del modelo del nuevo proveedor.

        Returns:
            TenantAIConfig | None: Configuración actualizada o None
                si no existe.
        """
        tenant = self.tenant_repository.get_by_id(tenant_id)
        if not tenant:
            return None

        try:
            config = tenant.ai_config
            config.provider = new_provider
            config.update_api_key(new_api_key)
            config.model_name = new_model_name
            config.save()
            return config

        except TenantAIConfig.DoesNotExist:
            return None

    def get_ai_config(
        self,
        tenant_id: str
    ) -> TenantAIConfig | None:
        """
        Obtiene la configuración de IA de un tenant.

        Args:
            tenant_id: ID del tenant.

        Returns:
            TenantAIConfig | None: Configuración si existe.
        """
        return self.tenant_repository.get_ai_config(
            self.tenant_repository.get_by_id(tenant_id)
        )

    @transaction.atomic
    def deactivate_ai_config(
        self,
        tenant_id: str
    ) -> TenantAIConfig | None:
        """
        Desactiva la configuración de IA de un tenant.

        Args:
            tenant_id: ID del tenant.

        Returns:
            TenantAIConfig | None: Configuración desactivada o None
                si no existe.
        """
        tenant = self.tenant_repository.get_by_id(tenant_id)
        if not tenant:
            return None

        try:
            config = tenant.ai_config
            config.deactivate()
            return config
        except TenantAIConfig.DoesNotExist:
            return None

    @transaction.atomic
    def activate_ai_config(
        self,
        tenant_id: str
    ) -> TenantAIConfig | None:
        """
        Activa la configuración de IA de un tenant.

        Args:
            tenant_id: ID del tenant.

        Returns:
            TenantAIConfig | None: Configuración activada o None
                si no existe.
        """
        tenant = self.tenant_repository.get_by_id(tenant_id)
        if not tenant:
            return None

        try:
            config = tenant.ai_config
            config.activate()
            return config
        except TenantAIConfig.DoesNotExist:
            return None
