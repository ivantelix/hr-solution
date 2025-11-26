"""
Modelo TenantMembership.

Este módulo contiene el modelo intermedio que conecta usuarios
con tenants y define sus roles.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone

from .choices import TenantRole
from .tenant_model import Tenant


class TenantMembership(models.Model):
    """
    Tabla intermedia que conecta User con Tenant y define su rol.

    Representa la relación entre un usuario y un tenant, incluyendo
    el rol que desempeña el usuario dentro del tenant.

    Attributes:
        tenant (FK): Tenant al que pertenece el usuario.
        user (FK): Usuario miembro del tenant.
        role (str): Rol del usuario en el tenant.
        is_active (bool): Indica si la membresía está activa.
        joined_at (datetime): Fecha en que el usuario se unió.
        invited_by (FK): Usuario que invitó a este miembro.

    Note:
        Un usuario puede pertenecer a múltiples tenants con
        diferentes roles.
    """

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        verbose_name="Tenant"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Usuario"
    )

    role = models.CharField(
        max_length=20,
        choices=TenantRole.choices,
        default=TenantRole.MEMBER,
        verbose_name="Rol",
        help_text="Rol del usuario dentro del tenant"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Activo",
        help_text="Indica si la membresía está activa"
    )

    joined_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Ingreso"
    )

    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invited_members",
        verbose_name="Invitado Por",
        help_text="Usuario que invitó a este miembro"
    )

    class Meta:
        verbose_name = "Membresía de Tenant"
        verbose_name_plural = "Membresías de Tenant"
        unique_together = ('tenant', 'user')
        ordering = ["-joined_at"]
        indexes = [
            models.Index(fields=["tenant", "is_active"]),
            models.Index(fields=["user", "is_active"]),
        ]

    def __str__(self) -> str:
        """
        Representación en string de la membresía.

        Returns:
            str: Descripción de la membresía.
        """
        return (
            f"{self.user.username} en {self.tenant.name} "
            f"({self.get_role_display()})"
        )

    def is_admin(self) -> bool:
        """
        Verifica si el usuario es administrador del tenant.

        Returns:
            bool: True si el rol es ADMIN.
        """
        return self.role == TenantRole.ADMIN

    def promote_to_admin(self) -> None:
        """
        Promueve al usuario a administrador del tenant.
        """
        self.role = TenantRole.ADMIN
        self.save(update_fields=["role"])

    def demote_to_member(self) -> None:
        """
        Degrada al usuario a miembro regular del tenant.
        """
        self.role = TenantRole.MEMBER
        self.save(update_fields=["role"])

    def deactivate(self) -> None:
        """
        Desactiva la membresía (soft delete).

        Note:
            El usuario sigue existiendo pero ya no tiene acceso
            al tenant.
        """
        self.is_active = False
        self.save(update_fields=["is_active"])

    def activate(self) -> None:
        """
        Reactiva una membresía previamente desactivada.
        """
        self.is_active = True
        self.save(update_fields=["is_active"])
