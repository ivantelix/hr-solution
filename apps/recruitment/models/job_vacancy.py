"""
Modelo JobVacancy.

Este módulo contiene el modelo de vacante de empleo.
"""

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.tenants.models import Tenant

from .choices import JobStatus


class JobVacancy(models.Model):
    """
    Modelo de Vacante de Empleo.

    Representa una posición abierta en una empresa (tenant).

    Attributes:
        tenant (FK): Tenant al que pertenece la vacante.
        title (str): Título del puesto.
        description (str): Descripción detallada.
        requirements (str): Requisitos del puesto.
        status (str): Estado actual de la vacante.
        location (str): Ubicación del puesto.
        salary_min (Decimal): Salario mínimo (opcional).
        salary_max (Decimal): Salario máximo (opcional).
        currency (str): Moneda del salario.
        is_remote (bool): Si es trabajo remoto.
        created_by (FK): Usuario que creó la vacante.
        created_at (datetime): Fecha de creación.
        updated_at (datetime): Fecha de actualización.
        closed_at (datetime): Fecha de cierre.
    """

    class InterviewMode(models.TextChoices):
        AUTO = "auto", "Entrevista por IA"
        MANUAL = "manual", "Entrevista Manual (Humano)"

    interview_mode = models.CharField(
        max_length=10,
        choices=InterviewMode.choices,
        default=InterviewMode.AUTO
    )

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="vacancies",
        verbose_name="Tenant",
    )

    title = models.CharField(max_length=255, verbose_name="Título del Puesto")

    description = models.TextField(verbose_name="Descripción")

    requirements = models.TextField(
        verbose_name="Requisitos",
        help_text="Lista de requisitos técnicos y habilidades blandas",
    )

    status = models.CharField(
        max_length=20,
        choices=JobStatus.choices,
        default=JobStatus.DRAFT,
        verbose_name="Estado",
    )

    location = models.CharField(max_length=100, blank=True, verbose_name="Ubicación")

    salary_min = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Salario Mínimo",
    )

    salary_max = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Salario Máximo",
    )

    currency = models.CharField(max_length=3, default="USD", verbose_name="Moneda")

    is_remote = models.BooleanField(default=False, verbose_name="Remoto")

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_vacancies",
        verbose_name="Creado Por",
    )

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creación"
    )

    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de Actualización"
    )

    closed_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Fecha de Cierre"
    )

    manual_interview_guide = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Vacante"
        verbose_name_plural = "Vacantes"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["tenant", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.get_status_display()})"

    def publish(self) -> None:
        """Publica la vacante."""
        self.status = JobStatus.PUBLISHED
        self.save(update_fields=["status", "updated_at"])

    def close(self) -> None:
        """Cierra la vacante."""
        self.status = JobStatus.CLOSED
        self.closed_at = timezone.now()
        self.save(update_fields=["status", "closed_at", "updated_at"])
