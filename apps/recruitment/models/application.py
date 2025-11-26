"""
Modelo Application.

Este módulo contiene el modelo de postulación que vincula
un candidato con una vacante.
"""

from django.db import models
from apps.tenants.models import Tenant
from .job_vacancy import JobVacancy
from .candidate import Candidate
from .choices import CandidateStatus, ApplicationSource


class Application(models.Model):
    """
    Modelo de Postulación (Application).

    Vincula a un candidato con una vacante específica y rastrea
    su progreso en el proceso de selección.

    Attributes:
        tenant (FK): Tenant (redundante pero útil para queries directos).
        vacancy (FK): Vacante a la que postula.
        candidate (FK): Candidato que postula.
        status (str): Estado actual en el proceso.
        source (str): Fuente de la postulación.
        score (float): Puntaje de evaluación (0-100).
        notes (str): Notas internas.
        applied_at (datetime): Fecha de postulación.
        updated_at (datetime): Fecha de actualización.
    """

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="applications",
        verbose_name="Tenant"
    )

    vacancy = models.ForeignKey(
        JobVacancy,
        on_delete=models.CASCADE,
        related_name="applications",
        verbose_name="Vacante"
    )

    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name="applications",
        verbose_name="Candidato"
    )

    status = models.CharField(
        max_length=20,
        choices=CandidateStatus.choices,
        default=CandidateStatus.NEW,
        verbose_name="Estado"
    )

    source = models.CharField(
        max_length=20,
        choices=ApplicationSource.choices,
        default=ApplicationSource.WEBSITE,
        verbose_name="Fuente"
    )

    score = models.FloatField(
        default=0.0,
        verbose_name="Puntaje",
        help_text="Puntaje de evaluación (0-100)"
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Notas Internas"
    )

    applied_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Postulación"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de Actualización"
    )

    class Meta:
        verbose_name = "Postulación"
        verbose_name_plural = "Postulaciones"
        ordering = ["-applied_at"]
        unique_together = ["vacancy", "candidate"]
        indexes = [
            models.Index(fields=["tenant", "status"]),
            models.Index(fields=["vacancy", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.candidate} - {self.vacancy}"
