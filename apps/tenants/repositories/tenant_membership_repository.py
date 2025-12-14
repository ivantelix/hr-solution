"""
Repositorio para el modelo TenantMembership.

Este módulo implementa el patrón Repository para abstraer el acceso
a datos del modelo TenantMembership.
"""

from typing import Protocol

from django.db.models import QuerySet

from apps.tenants.models import Tenant, TenantMembership, TenantRole


class TenantMembershipRepositoryProtocol(Protocol):
    """
    Interface (Protocol) para el repositorio de membresías.

    Define el contrato que debe cumplir cualquier implementación
    del repositorio de membresías de tenant.
    """

    def get_by_id(self, membership_id: int) -> TenantMembership | None:
        """Obtiene una membresía por ID."""
        ...

    def get_user_tenants(self, user_id: int) -> list[Tenant]:
        """Obtiene todos los tenants de un usuario."""
        ...

    def get_tenant_members(self, tenant_id: str) -> QuerySet:
        """Obtiene todos los miembros de un tenant."""
        ...

    def create(self, **kwargs) -> TenantMembership:
        """Crea una nueva membresía."""
        ...


class TenantMembershipRepository:
    """
    Implementación del repositorio de membresías de tenant.

    Proporciona métodos para realizar operaciones CRUD sobre el
    modelo TenantMembership.
    """

    def get_by_id(self, membership_id: int) -> TenantMembership | None:
        """
        Obtiene una membresía por su ID.

        Args:
            membership_id: ID de la membresía a buscar.

        Returns:
            TenantMembership | None: Membresía si existe, None en
                caso contrario.
        """
        try:
            return TenantMembership.objects.get(id=membership_id)
        except TenantMembership.DoesNotExist:
            return None

    def get_by_user_and_tenant(
        self, user_id: int, tenant_id: str
    ) -> TenantMembership | None:
        """
        Obtiene la membresía de un usuario en un tenant específico.

        Args:
            user_id: ID del usuario.
            tenant_id: ID del tenant.

        Returns:
            TenantMembership | None: Membresía si existe.
        """
        try:
            return TenantMembership.objects.get(user_id=user_id, tenant_id=tenant_id)
        except TenantMembership.DoesNotExist:
            return None

    def get_user_tenants(self, user_id: int) -> list[Tenant]:
        """
        Obtiene todos los tenants a los que pertenece un usuario.

        Args:
            user_id: ID del usuario.

        Returns:
            list[Tenant]: Lista de tenants del usuario.
        """
        memberships = TenantMembership.objects.filter(
            user_id=user_id, is_active=True
        ).select_related("tenant")

        return [m.tenant for m in memberships]

    def get_tenant_members(self, tenant_id: str) -> QuerySet[TenantMembership]:
        """
        Obtiene todas las membresías de un tenant.

        Args:
            tenant_id: ID del tenant.

        Returns:
            QuerySet[TenantMembership]: QuerySet con las membresías.
        """
        return TenantMembership.objects.filter(tenant_id=tenant_id).select_related(
            "user"
        )

    def get_active_members(self, tenant_id: str) -> QuerySet[TenantMembership]:
        """
        Obtiene las membresías activas de un tenant.

        Args:
            tenant_id: ID del tenant.

        Returns:
            QuerySet[TenantMembership]: QuerySet con membresías
                activas.
        """
        return TenantMembership.objects.filter(
            tenant_id=tenant_id, is_active=True
        ).select_related("user")

    def get_admins(self, tenant_id: str) -> QuerySet[TenantMembership]:
        """
        Obtiene los administradores de un tenant.

        Args:
            tenant_id: ID del tenant.

        Returns:
            QuerySet[TenantMembership]: QuerySet con admins.
        """
        return TenantMembership.objects.filter(
            tenant_id=tenant_id, role=TenantRole.ADMIN, is_active=True
        ).select_related("user")

    def create(self, **kwargs) -> TenantMembership:
        """
        Crea una nueva membresía.

        Args:
            **kwargs: Campos de la membresía a crear.

        Returns:
            TenantMembership: Membresía creada.
        """
        return TenantMembership.objects.create(**kwargs)

    def update(self, membership: TenantMembership, **kwargs) -> TenantMembership:
        """
        Actualiza una membresía existente.

        Args:
            membership: Instancia de la membresía a actualizar.
            **kwargs: Campos a actualizar.

        Returns:
            TenantMembership: Membresía actualizada.
        """
        for key, value in kwargs.items():
            setattr(membership, key, value)
        membership.save()
        return membership

    def delete(self, membership: TenantMembership) -> None:
        """
        Elimina una membresía.

        Args:
            membership: Instancia de la membresía a eliminar.

        Note:
            Considera usar soft delete (is_active=False).
        """
        membership.delete()

    def deactivate(self, membership: TenantMembership) -> TenantMembership:
        """
        Desactiva una membresía (soft delete).

        Args:
            membership: Instancia de la membresía a desactivar.

        Returns:
            TenantMembership: Membresía desactivada.
        """
        membership.deactivate()
        return membership

    def activate(self, membership: TenantMembership) -> TenantMembership:
        """
        Activa una membresía previamente desactivada.

        Args:
            membership: Instancia de la membresía a activar.

        Returns:
            TenantMembership: Membresía activada.
        """
        membership.activate()
        return membership

    def user_is_admin(self, user_id: int, tenant_id: str) -> bool:
        """
        Verifica si un usuario es administrador de un tenant.

        Args:
            user_id: ID del usuario.
            tenant_id: ID del tenant.

        Returns:
            bool: True si el usuario es admin del tenant.
        """
        return TenantMembership.objects.filter(
            user_id=user_id, tenant_id=tenant_id, role=TenantRole.ADMIN, is_active=True
        ).exists()

    def user_is_member(self, user_id: int, tenant_id: str) -> bool:
        """
        Verifica si un usuario es miembro de un tenant.

        Args:
            user_id: ID del usuario.
            tenant_id: ID del tenant.

        Returns:
            bool: True si el usuario es miembro del tenant.
        """
        return TenantMembership.objects.filter(
            user_id=user_id, tenant_id=tenant_id, is_active=True
        ).exists()
