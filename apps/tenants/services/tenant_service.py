"""
Servicio de aplicación para el modelo Tenant.

Este módulo contiene los casos de uso relacionados con tenants,
implementando la lógica de negocio y orquestando las operaciones
a través de repositorios.
"""

from typing import Any
from django.db import transaction
from django.utils.text import slugify

from apps.tenants.models import Tenant, PlanType
from apps.tenants.repositories import TenantRepository


class TenantService:
    """
    Servicio de aplicación para gestión de tenants.

    Implementa los casos de uso relacionados con tenants,
    orquestando la lógica de negocio y delegando la persistencia
    al repositorio.

    Attributes:
        repository: Repositorio de tenants para acceso a datos.
    """

    def __init__(
        self,
        repository: TenantRepository | None = None
    ):
        """
        Inicializa el servicio con el repositorio.

        Args:
            repository: Repositorio de tenants. Si no se
                proporciona, se crea una instancia por defecto.
        """
        self.repository = repository or TenantRepository()

    @transaction.atomic
    def create_tenant(
        self,
        name: str,
        slug: str | None = None,
        plan: PlanType = PlanType.BASIC,
        max_users: int = 5,
        **extra_fields: Any
    ) -> Tenant:
        """
        Crea un nuevo tenant.

        Args:
            name: Nombre de la empresa.
            slug: Slug único (se genera automáticamente si no se
                proporciona).
            plan: Plan de suscripción.
            max_users: Número máximo de usuarios permitidos.
            **extra_fields: Campos adicionales.

        Returns:
            Tenant: Tenant creado.

        Raises:
            ValueError: Si el slug ya existe.
        """
        # Generar slug si no se proporciona
        if not slug:
            slug = slugify(name)

        # Validar que el slug sea único
        if self.repository.get_by_slug(slug):
            raise ValueError(
                f"El slug '{slug}' ya está en uso."
            )

        # Crear el tenant
        tenant = self.repository.create(
            name=name,
            slug=slug,
            plan=plan,
            max_users=max_users,
            **extra_fields
        )

        return tenant

    @transaction.atomic
    def update_tenant(
        self,
        tenant_id: str,
        **update_data: Any
    ) -> Tenant | None:
        """
        Actualiza un tenant existente.

        Args:
            tenant_id: ID del tenant a actualizar.
            **update_data: Datos a actualizar.

        Returns:
            Tenant | None: Tenant actualizado o None si no existe.

        Raises:
            ValueError: Si se intenta actualizar el slug a uno que
                ya existe.
        """
        tenant = self.repository.get_by_id(tenant_id)
        if not tenant:
            return None

        # Validar slug si se está actualizando
        if 'slug' in update_data:
            new_slug = update_data['slug']
            existing = self.repository.get_by_slug(new_slug)
            if existing and str(existing.id) != tenant_id:
                raise ValueError(
                    f"El slug '{new_slug}' ya está en uso."
                )

        # Actualizar el tenant
        return self.repository.update(tenant, **update_data)

    @transaction.atomic
    def update_plan(
        self,
        tenant_id: str,
        new_plan: PlanType,
        new_max_users: int | None = None
    ) -> Tenant | None:
        """
        Actualiza el plan de suscripción de un tenant.

        Args:
            tenant_id: ID del tenant.
            new_plan: Nuevo plan de suscripción.
            new_max_users: Nuevo límite de usuarios (opcional).

        Returns:
            Tenant | None: Tenant actualizado o None si no existe.

        Note:
            Si se reduce el límite de usuarios, verificar que no
            exceda el número actual de miembros activos.
        """
        tenant = self.repository.get_by_id(tenant_id)
        if not tenant:
            return None

        update_data = {'plan': new_plan}

        if new_max_users is not None:
            # Verificar que no sea menor al número actual de
            # miembros
            current_members = tenant.get_active_members_count()
            if new_max_users < current_members:
                raise ValueError(
                    f"No se puede reducir el límite a {new_max_users} "
                    f"usuarios. Actualmente hay {current_members} "
                    f"miembros activos."
                )
            update_data['max_users'] = new_max_users

        return self.repository.update(tenant, **update_data)

    @transaction.atomic
    def deactivate_tenant(self, tenant_id: str) -> Tenant | None:
        """
        Desactiva un tenant (soft delete).

        Args:
            tenant_id: ID del tenant a desactivar.

        Returns:
            Tenant | None: Tenant desactivado o None si no existe.
        """
        tenant = self.repository.get_by_id(tenant_id)
        if not tenant:
            return None

        return self.repository.deactivate(tenant)

    @transaction.atomic
    def activate_tenant(self, tenant_id: str) -> Tenant | None:
        """
        Activa un tenant previamente desactivado.

        Args:
            tenant_id: ID del tenant a activar.

        Returns:
            Tenant | None: Tenant activado o None si no existe.
        """
        tenant = self.repository.get_by_id(tenant_id)
        if not tenant:
            return None

        return self.repository.activate(tenant)

    def get_tenant_by_id(self, tenant_id: str) -> Tenant | None:
        """
        Obtiene un tenant por ID.

        Args:
            tenant_id: ID del tenant.

        Returns:
            Tenant | None: Tenant si existe, None en caso contrario.
        """
        return self.repository.get_by_id(tenant_id)

    def get_tenant_by_slug(self, slug: str) -> Tenant | None:
        """
        Obtiene un tenant por slug.

        Args:
            slug: Slug del tenant.

        Returns:
            Tenant | None: Tenant si existe, None en caso contrario.
        """
        return self.repository.get_by_slug(slug)

    def get_user_tenants(self, user_id: int) -> list[Tenant]:
        """
        Obtiene todos los tenants de un usuario.

        Args:
            user_id: ID del usuario.

        Returns:
            list[Tenant]: Lista de tenants del usuario.
        """
        return self.repository.get_by_user(user_id)

    def get_active_user_tenants(self, user_id: int) -> list[Tenant]:
        """
        Obtiene todos los tenants activos de un usuario.

        Args:
            user_id: ID del usuario.

        Returns:
            list[Tenant]: Lista de tenants activos del usuario.
        """
        return self.repository.get_active_by_user(user_id)

    def get_ai_config(self, tenant_id: str):
        """
        Obtiene la configuración de IA de un tenant.

        Args:
            tenant_id: ID del tenant.

        Returns:
            TenantAIConfig | None: Configuración de IA si existe.
        """
        tenant = self.repository.get_by_id(tenant_id)
        if not tenant:
            return None

        return self.repository.get_ai_config(tenant)
