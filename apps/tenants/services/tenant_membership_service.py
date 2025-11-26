"""
Servicio de aplicación para TenantMembership.

Este módulo contiene los casos de uso relacionados con membresías
de tenants, gestionando la relación entre usuarios y tenants.
"""

from django.db import transaction

from apps.tenants.models import TenantMembership, TenantRole
from apps.tenants.repositories import (
    TenantMembershipRepository,
    TenantRepository,
)


class TenantMembershipService:
    """
    Servicio de aplicación para gestión de membresías de tenant.

    Implementa los casos de uso relacionados con la gestión de
    miembros dentro de un tenant.

    Attributes:
        membership_repository: Repositorio de membresías.
        tenant_repository: Repositorio de tenants.
    """

    def __init__(
        self,
        membership_repository: TenantMembershipRepository | None = None,
        tenant_repository: TenantRepository | None = None
    ):
        """
        Inicializa el servicio con los repositorios.

        Args:
            membership_repository: Repositorio de membresías.
            tenant_repository: Repositorio de tenants.
        """
        self.membership_repository = (
            membership_repository or TenantMembershipRepository()
        )
        self.tenant_repository = (
            tenant_repository or TenantRepository()
        )

    @transaction.atomic
    def add_member(
        self,
        tenant_id: str,
        user_id: int,
        role: TenantRole = TenantRole.MEMBER,
        invited_by_id: int | None = None
    ) -> TenantMembership:
        """
        Agrega un nuevo miembro a un tenant.

        Args:
            tenant_id: ID del tenant.
            user_id: ID del usuario a agregar.
            role: Rol del usuario en el tenant.
            invited_by_id: ID del usuario que invita (opcional).

        Returns:
            TenantMembership: Membresía creada.

        Raises:
            ValueError: Si el tenant no existe, el usuario ya es
                miembro, o se alcanzó el límite de usuarios.
        """
        # Validar que el tenant exista
        tenant = self.tenant_repository.get_by_id(tenant_id)
        if not tenant:
            raise ValueError("El tenant no existe.")

        # Validar que el usuario no sea ya miembro
        existing = self.membership_repository.get_by_user_and_tenant(
            user_id=user_id,
            tenant_id=tenant_id
        )
        if existing and existing.is_active:
            raise ValueError(
                "El usuario ya es miembro de este tenant."
            )

        # Validar límite de usuarios
        if not tenant.can_add_member():
            raise ValueError(
                f"Se alcanzó el límite de {tenant.max_users} usuarios "
                f"para este tenant."
            )

        # Si existe pero está inactivo, reactivar
        if existing and not existing.is_active:
            existing.role = role
            existing.activate()
            return existing

        # Crear nueva membresía
        membership = self.membership_repository.create(
            tenant_id=tenant_id,
            user_id=user_id,
            role=role,
            invited_by_id=invited_by_id
        )

        return membership

    @transaction.atomic
    def remove_member(
        self,
        tenant_id: str,
        user_id: int
    ) -> TenantMembership | None:
        """
        Remueve un miembro de un tenant (soft delete).

        Args:
            tenant_id: ID del tenant.
            user_id: ID del usuario a remover.

        Returns:
            TenantMembership | None: Membresía desactivada o None
                si no existe.

        Raises:
            ValueError: Si es el último administrador del tenant.
        """
        membership = self.membership_repository.get_by_user_and_tenant(
            user_id=user_id,
            tenant_id=tenant_id
        )

        if not membership:
            return None

        # Validar que no sea el último admin
        if membership.is_admin():
            admins_count = self.membership_repository.get_admins(
                tenant_id
            ).count()
            if admins_count <= 1:
                raise ValueError(
                    "No se puede remover el último administrador "
                    "del tenant."
                )

        return self.membership_repository.deactivate(membership)

    @transaction.atomic
    def update_role(
        self,
        tenant_id: str,
        user_id: int,
        new_role: TenantRole
    ) -> TenantMembership | None:
        """
        Actualiza el rol de un miembro en un tenant.

        Args:
            tenant_id: ID del tenant.
            user_id: ID del usuario.
            new_role: Nuevo rol a asignar.

        Returns:
            TenantMembership | None: Membresía actualizada o None
                si no existe.

        Raises:
            ValueError: Si se intenta degradar al último admin.
        """
        membership = self.membership_repository.get_by_user_and_tenant(
            user_id=user_id,
            tenant_id=tenant_id
        )

        if not membership:
            return None

        # Si se está degradando de admin a member
        if (membership.is_admin() and
                new_role == TenantRole.MEMBER):
            # Validar que no sea el último admin
            admins_count = self.membership_repository.get_admins(
                tenant_id
            ).count()
            if admins_count <= 1:
                raise ValueError(
                    "No se puede degradar el último administrador "
                    "del tenant."
                )

        return self.membership_repository.update(
            membership,
            role=new_role
        )

    def get_tenant_members(self, tenant_id: str) -> list[TenantMembership]:
        """
        Obtiene todos los miembros de un tenant.

        Args:
            tenant_id: ID del tenant.

        Returns:
            list[TenantMembership]: Lista de membresías del tenant.
        """
        return list(
            self.membership_repository.get_tenant_members(tenant_id)
        )

    def get_active_members(
        self,
        tenant_id: str
    ) -> list[TenantMembership]:
        """
        Obtiene los miembros activos de un tenant.

        Args:
            tenant_id: ID del tenant.

        Returns:
            list[TenantMembership]: Lista de membresías activas.
        """
        return list(
            self.membership_repository.get_active_members(tenant_id)
        )

    def get_tenant_admins(
        self,
        tenant_id: str
    ) -> list[TenantMembership]:
        """
        Obtiene los administradores de un tenant.

        Args:
            tenant_id: ID del tenant.

        Returns:
            list[TenantMembership]: Lista de administradores.
        """
        return list(
            self.membership_repository.get_admins(tenant_id)
        )

    def user_is_admin(
        self,
        user_id: int,
        tenant_id: str
    ) -> bool:
        """
        Verifica si un usuario es administrador de un tenant.

        Args:
            user_id: ID del usuario.
            tenant_id: ID del tenant.

        Returns:
            bool: True si el usuario es admin del tenant.
        """
        return self.membership_repository.user_is_admin(
            user_id=user_id,
            tenant_id=tenant_id
        )

    def user_is_member(
        self,
        user_id: int,
        tenant_id: str
    ) -> bool:
        """
        Verifica si un usuario es miembro de un tenant.

        Args:
            user_id: ID del usuario.
            tenant_id: ID del tenant.

        Returns:
            bool: True si el usuario es miembro del tenant.
        """
        return self.membership_repository.user_is_member(
            user_id=user_id,
            tenant_id=tenant_id
        )
