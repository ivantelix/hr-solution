from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Modelo de Usuario Personalizado del Sistema.

    Extiende AbstractUser de Django para proporcionar funcionalidad
    de autenticación completa con campos adicionales específicos
    del negocio.

    Attributes:
        username (str): Nombre de usuario único (heredado).
        email (str): Correo electrónico único (heredado).
        first_name (str): Nombre del usuario (heredado).
        last_name (str): Apellido del usuario (heredado).
        phone (str | None): Número de teléfono del usuario.
        avatar (str | None): URL o path del avatar del usuario.
        is_email_verified (bool): Indica si el email ha sido
            verificado.
        is_superuser (bool): Flag de Super Admin para Backoffice
            (heredado).

    Note:
        Los usuarios pueden pertenecer a múltiples tenants a través
        de TenantMembership. El campo is_superuser se usa para
        administradores del sistema (backoffice).
    """

    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Teléfono",
        help_text="Número de teléfono del usuario"
    )

    avatar = models.URLField(
        blank=True,
        null=True,
        verbose_name="Avatar",
        help_text="URL del avatar del usuario"
    )

    is_email_verified = models.BooleanField(
        default=False,
        verbose_name="Email Verificado",
        help_text="Indica si el correo ha sido verificado"
    )

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ["-date_joined"]

    def __str__(self) -> str:
        """
        Representación en string del usuario.

        Returns:
            str: Email del usuario si está disponible, sino el
                username.
        """
        return self.email if self.email else self.username

    def get_full_name(self) -> str:
        """
        Obtiene el nombre completo del usuario.

        Returns:
            str: Nombre completo (first_name + last_name) o
                username si no hay nombre.
        """
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.username

    def get_active_tenants(self):
        """
        Obtiene los tenants activos a los que pertenece el usuario.

        Returns:
            QuerySet: QuerySet de Tenant donde el usuario es
                miembro activo.

        Note:
            Requiere que la app tenants esté instalada y el modelo
            TenantMembership exista.
        """
        return self.tenants.filter(
            tenantmembership__is_active=True
        ).distinct()

