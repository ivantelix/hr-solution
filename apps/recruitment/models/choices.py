"""
Choices para la app recruitment.

Este módulo contiene las definiciones de choices (enumeraciones)
utilizadas en los modelos de reclutamiento.
"""

from django.db import models


class JobStatus(models.TextChoices):
    """Estado de la vacante."""

    DRAFT = "draft", "Borrador"
    PUBLISHED = "published", "Publicada"
    CLOSED = "closed", "Cerrada"
    ARCHIVED = "archived", "Archivada"


class CandidateStatus(models.TextChoices):
    """Estado del candidato en el proceso."""

    NEW = "new", "Nuevo"
    SCREENING = "screening", "En Screening"
    INTERVIEW = "interview", "En Entrevista"
    OFFER = "offer", "Oferta Enviada"
    HIRED = "hired", "Contratado"
    REJECTED = "rejected", "Rechazado"
    WITHDRAWN = "withdrawn", "Retirado"


class ApplicationSource(models.TextChoices):
    """Fuente de la postulación."""

    LINKEDIN = "linkedin", "LinkedIn"
    WEBSITE = "website", "Sitio Web"
    REFERRAL = "referral", "Referido"
    AGENCY = "agency", "Agencia"
    OTHER = "other", "Otro"
