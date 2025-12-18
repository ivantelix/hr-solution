"""
Repositorio para el modelo Tenant.

Este módulo implementa el patrón Repository para abstraer el acceso
a datos del modelo Tenant.
"""

from typing import Protocol

from django.db.models import QuerySet

from apps.tenants.models import PlanType, Tenant


class TenantRepositoryProtocol(Protocol):
    """
    Interface (Protocol) para el repositorio de tenants.

    Define el contrato que debe cumplir cualquier implementación
    del repositorio de tenants.
    """

    def get_by_id(self, tenant_id: str) -> Tenant | None:
        """Obtiene un tenant por ID."""
        ...

    def get_by_slug(self, slug: str) -> Tenant | None:
        """Obtiene un tenant por slug."""
        ...

    def get_by_user(self, user_id: int) -> list[Tenant]:
        """Obtiene todos los tenants de un usuario."""
        ...

    def create(self, **kwargs) -> Tenant:
        """Crea un nuevo tenant."""
        ...

    def update(self, tenant: Tenant, **kwargs) -> Tenant:
        """Actualiza un tenant existente."""
        ...

    def delete(self, tenant: Tenant) -> None:
        """Elimina un tenant."""
        ...


class TenantRepository:
    """
    Implementación del repositorio de tenants.

    Proporciona métodos para realizar operaciones CRUD sobre el
    modelo Tenant, abstrayendo la lógica de acceso a datos.
    """

    def get_by_id(self, tenant_id: str) -> Tenant | None:
        """
        Obtiene un tenant por su ID (UUID).

        Args:
            tenant_id: ID del tenant a buscar.

        Returns:
            Tenant | None: Tenant si existe, None en caso contrario.
        """
        try:
            return Tenant.objects.get(id=tenant_id)
        except Tenant.DoesNotExist:
            return None

    def get_by_slug(self, slug: str) -> Tenant | None:
        """
        Obtiene un tenant por su slug.

        Args:
            slug: Slug del tenant a buscar.

        Returns:
            Tenant | None: Tenant si existe, None en caso contrario.
        """
        try:
            return Tenant.objects.get(slug=slug)
        except Tenant.DoesNotExist:
            return None

    def get_by_user(self, user_id: int) -> list[Tenant]:
        """
        Obtiene todos los tenants a los que pertenece un usuario.

        Args:
            user_id: ID del usuario.

        Returns:
            list[Tenant]: Lista de tenants del usuario.
        """
        return list(
            Tenant.objects.filter(
                tenantmembership__user_id=user_id, tenantmembership__is_active=True
            ).distinct()
        )

    def get_active_by_user(self, user_id: int) -> list[Tenant]:
        """
        Obtiene todos los tenants activos de un usuario.

        Args:
            user_id: ID del usuario.

        Returns:
            list[Tenant]: Lista de tenants activos del usuario.
        """
        return list(
            Tenant.objects.filter(
                tenantmembership__user_id=user_id,
                tenantmembership__is_active=True,
                is_active=True,
            ).distinct()
        )

    def create(self, **kwargs) -> Tenant:
        """
        Crea un nuevo tenant.

        Args:
            **kwargs: Campos del tenant a crear.

        Returns:
            Tenant: Tenant creado.
        """
        return Tenant.objects.create(**kwargs)

    def update(self, tenant: Tenant, **kwargs) -> Tenant:
        """
        Actualiza un tenant existente.

        Args:
            tenant: Instancia del tenant a actualizar.
            **kwargs: Campos a actualizar.

        Returns:
            Tenant: Tenant actualizado.
        """
        for key, value in kwargs.items():
            setattr(tenant, key, value)
        tenant.save()
        return tenant

    def delete(self, tenant: Tenant) -> None:
        """
        Elimina un tenant.

        Args:
            tenant: Instancia del tenant a eliminar.

        Note:
            Considera usar soft delete (is_active=False) en lugar
            de eliminación física.
        """
        tenant.delete()

    def deactivate(self, tenant: Tenant) -> Tenant:
        """
        Desactiva un tenant (soft delete).

        Args:
            tenant: Instancia del tenant a desactivar.

        Returns:
            Tenant: Tenant desactivado.
        """
        tenant.deactivate()
        return tenant

    def activate(self, tenant: Tenant) -> Tenant:
        """
        Activa un tenant previamente desactivado.

        Args:
            tenant: Instancia del tenant a activar.

        Returns:
            Tenant: Tenant activado.
        """
        tenant.activate()
        return tenant

    def all(self) -> QuerySet[Tenant]:
        """
        Obtiene todos los tenants.

        Returns:
            QuerySet[Tenant]: QuerySet con todos los tenants.
        """
        return Tenant.objects.all()

    def filter_active(self) -> QuerySet[Tenant]:
        """
        Obtiene todos los tenants activos.

        Returns:
            QuerySet[Tenant]: QuerySet con tenants activos.
        """
        return Tenant.objects.filter(is_active=True)

    def filter_by_plan(self, plan: PlanType) -> QuerySet[Tenant]:
        """
        Obtiene todos los tenants con un plan específico.

        Args:
            plan: Tipo de plan a filtrar.

        Returns:
            QuerySet[Tenant]: QuerySet con tenants del plan.
        """
        return Tenant.objects.filter(plan=plan)

    def get_ai_config(self, tenant: Tenant):
        """
        Obtiene la configuración de IA de un tenant.

        Args:
            tenant: Instancia del tenant.

        Returns:
            TenantAIConfig | None: Configuración de IA si existe.
        """
        try:
            return tenant.ai_config
        except Exception:
            return None
