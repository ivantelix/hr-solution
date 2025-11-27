"""
Modelo Tenant.

Este módulo contiene el modelo principal de Tenant que representa
a un cliente/empresa en el sistema SaaS multitenant.
"""

import uuid
from django.db import models
from django.conf import settings


from .choices import PlanType


class Tenant(models.Model):
    """
    Modelo de Tenant (Cuenta del Cliente/Empresa).

    Representa a una empresa cliente en el sistema SaaS multitenant.
    Cada tenant tiene su propio plan de suscripción y conjunto de
    miembros.

    Attributes:
        id (UUID): Identificador único del tenant.
        name (str): Nombre de la empresa.
        slug (str): Slug único para URLs amigables.
        plan (str): Plan de suscripción actual.
        is_active (bool): Indica si el tenant está activo.
        max_users (int): Número máximo de usuarios permitidos.
        created_at (datetime): Fecha de creación del tenant.
        updated_at (datetime): Fecha de última actualización.
        members (ManyToMany): Usuarios que pertenecen al tenant.

    Note:
        El campo is_active se usa para soft delete y suspensión
        de cuentas.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID"
    )

    name = models.CharField(
        max_length=255,
        verbose_name="Nombre de la Empresa",
        help_text="Nombre legal o comercial de la empresa"
    )

    slug = models.SlugField(
        max_length=255,
        unique=True,
        verbose_name="Slug",
        help_text="Identificador único para URLs (ej: empresa-abc)"
    )

    plan = models.CharField(
        max_length=20,
        choices=PlanType.choices,
        default=PlanType.BASIC,
        verbose_name="Plan Actual",
        help_text="Plan de suscripción del tenant"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Activo",
        help_text="Indica si el tenant está activo"
    )

    max_users = models.PositiveIntegerField(
        default=5,
        verbose_name="Máximo de Usuarios",
        help_text="Número máximo de usuarios permitidos"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de Actualización"
    )

    # Relaciona a los usuarios (miembros) con este tenant
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="TenantMembership",
        through_fields=("tenant", "user"),
        related_name="tenants",
        verbose_name="Miembros"
    )

    class Meta:
        verbose_name = "Tenant"
        verbose_name_plural = "Tenants"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self) -> str:
        """
        Representación en string del tenant.

        Returns:
            str: Nombre del tenant.
        """
        return self.name

    def get_active_members_count(self) -> int:
        """
        Obtiene el número de miembros activos del tenant.

        Returns:
            int: Cantidad de miembros activos.
        """
        return self.tenantmembership_set.filter(
            is_active=True
        ).count()

    def can_add_member(self) -> bool:
        """
        Verifica si se puede agregar un nuevo miembro al tenant.

        Returns:
            bool: True si no se ha alcanzado el límite de usuarios.
        """
        return self.get_active_members_count() < self.max_users

    def get_admins(self):
        """
        Obtiene todos los administradores del tenant.

        Returns:
            QuerySet: QuerySet de usuarios con rol de administrador.
        """
        from .choices import TenantRole
        return self.members.filter(
            tenantmembership__role=TenantRole.ADMIN,
            tenantmembership__is_active=True
        )

    def deactivate(self) -> None:
        """
        Desactiva el tenant (soft delete).

        Note:
            Esto no elimina el tenant de la base de datos,
            solo lo marca como inactivo.
        """
        self.is_active = False
        self.save(update_fields=["is_active", "updated_at"])

    def activate(self) -> None:
        """
        Activa un tenant previamente desactivado.
        """
        self.is_active = True
        self.save(update_fields=["is_active", "updated_at"])
