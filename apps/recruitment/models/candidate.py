"""
Modelo Candidate.

Este módulo contiene el modelo de candidato.
"""

from django.db import models
from apps.tenants.models import Tenant


class Candidate(models.Model):
    """
    Modelo de Candidato.

    Representa a una persona que postula a vacantes dentro de un tenant.
    Los candidatos son específicos por tenant (aislamiento de datos).

    Attributes:
        tenant (FK): Tenant al que pertenece el candidato.
        first_name (str): Nombre.
        last_name (str): Apellido.
        email (str): Correo electrónico.
        phone (str): Teléfono.
        linkedin_url (str): Perfil de LinkedIn.
        resume_url (str): URL del CV (S3/Cloudinary).
        skills (JSON): Lista de habilidades detectadas.
        created_at (datetime): Fecha de creación.
        updated_at (datetime): Fecha de actualización.
    """

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="candidates",
        verbose_name="Tenant"
    )

    first_name = models.CharField(
        max_length=100,
        verbose_name="Nombre"
    )

    last_name = models.CharField(
        max_length=100,
        verbose_name="Apellido"
    )

    email = models.EmailField(
        verbose_name="Email"
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Teléfono"
    )

    linkedin_url = models.URLField(
        blank=True,
        verbose_name="LinkedIn URL"
    )

    resume_url = models.URLField(
        blank=True,
        verbose_name="CV URL",
        help_text="URL del archivo del CV"
    )

    skills = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Habilidades",
        help_text="Lista de habilidades extraídas o manuales"
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
        verbose_name = "Candidato"
        verbose_name_plural = "Candidatos"
        ordering = ["-created_at"]
        unique_together = ["tenant", "email"]  # Email único por tenant
        indexes = [
            models.Index(fields=["tenant", "email"]),
            models.Index(fields=["tenant", "last_name"]),
        ]

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self) -> str:
        """Retorna el nombre completo."""
        return f"{self.first_name} {self.last_name}"
