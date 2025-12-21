"""
Modelo VacancySocialPost.

Este módulo contiene el modelo para gestionar las publicaciones
en redes sociales asociadas a una vacante.
"""

from django.db import models
from .choices import SocialPlatform, SocialPostStatus
from .job_vacancy import JobVacancy


class VacancySocialPost(models.Model):
    """
    Representa una publicación en una red social para una vacante.
    Actúa como un registro de previsualización (staging) y de historial.
    """

    vacancy = models.ForeignKey(
        JobVacancy,
        on_delete=models.CASCADE,
        related_name="social_posts",
        verbose_name="Vacante",
    )

    platform = models.CharField(
        max_length=20,
        choices=SocialPlatform.choices,
        verbose_name="Plataforma",
    )

    content = models.TextField(
        verbose_name="Contenido del Post",
        help_text="Contenido personalizable para esta red social específico.",
    )

    status = models.CharField(
        max_length=20,
        choices=SocialPostStatus.choices,
        default=SocialPostStatus.DRAFT,
        verbose_name="Estado",
    )

    posted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de Publicación",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Publicación en Red Social"
        verbose_name_plural = "Publicaciones en Redes Sociales"
        unique_together = ["vacancy", "platform"]  # Una vacante, un post por red?? Revisar si permitir múltiples.
        # Por ahora asumo uno por red para simplificar el "preview".

    def __str__(self):
        return f"{self.get_platform_display()} - {self.vacancy.title}"
