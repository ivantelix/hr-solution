"""
Servicio de aplicación para JobVacancy.

Este módulo contiene los casos de uso relacionados con vacantes.
"""

from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.recruitment.models import (
    JobVacancy,
    SocialPlatform,
    SocialPostStatus,
    VacancySocialPost,
)
from apps.recruitment.repositories import JobVacancyRepository
from apps.tenants.repositories import TenantRepository


class JobVacancyService:
    """
    Servicio de aplicación para gestión de vacantes.

    Implementa los casos de uso relacionados con vacantes.
    """

    def __init__(
        self,
        repository: JobVacancyRepository | None = None,
        tenant_repository: TenantRepository | None = None,
    ):
        self.repository = repository or JobVacancyRepository()
        self.tenant_repository = tenant_repository or TenantRepository()

    @transaction.atomic
    def create_vacancy(
        self,
        tenant_id: str,
        title: str,
        description: str,
        user_id: int,
        social_platforms: list[str] | None = None,
        **extra_fields: Any,
    ) -> tuple[JobVacancy, list[VacancySocialPost]]:
        """
        Crea una nueva vacante y opcionalmente genera posts sociales.

        Args:
            tenant_id: ID del tenant.
            title: Título del puesto.
            description: Descripción.
            user_id: ID del usuario creador.
            social_platforms: Lista de plataformas para generar posts (opcional).
            **extra_fields: Campos adicionales.

        Returns:
            tuple: (JobVacancy creada, lista de posts generados).

        Raises:
            ValueError: Si el tenant no existe.
        """
        tenant = self.tenant_repository.get_by_id(tenant_id)
        if not tenant:
            raise ValueError("El tenant no existe.")

        vacancy = self.repository.create(
            tenant=tenant,
            title=title,
            description=description,
            created_by_id=user_id,
            **extra_fields,
        )

        # Generar posts sociales si se especificaron plataformas
        social_posts = []
        if social_platforms:
            social_posts = self.generate_social_previews(vacancy.id, social_platforms)

        return vacancy, social_posts

    @transaction.atomic
    def generate_social_previews(
        self, vacancy_id: int, platforms: list[str]
    ) -> list[VacancySocialPost]:
        """
        Genera previsualizaciones de posts para redes sociales usando IA.

        Args:
            vacancy_id: ID de la vacante.
            platforms: Lista de plataformas (linkedin, twitter, facebook).

        Returns:
            list[VacancySocialPost]: Lista de posts generados.
        """
        from apps.recruitment.services import SocialMediaContentGenerator

        vacancy = self.repository.get_by_id(vacancy_id)
        if not vacancy:
            raise ValueError("La vacante no existe.")

        # Limpiar borradores existentes para estas plataformas
        VacancySocialPost.objects.filter(
            vacancy=vacancy,
            platform__in=platforms,
            status=SocialPostStatus.DRAFT,
        ).delete()

        # Usar el generador de IA
        generator = SocialMediaContentGenerator()
        created_posts = generator.generate_posts_for_vacancy(vacancy, platforms)

        return created_posts

    @transaction.atomic
    def publish_vacancy(self, vacancy_id: int) -> JobVacancy | None:
        """
        Publica una vacante y sus posts programados.

        Args:
            vacancy_id: ID de la vacante.

        Returns:
            JobVacancy | None: Vacante publicada o None.
        """
        vacancy = self.repository.get_by_id(vacancy_id)
        if not vacancy:
            return None

        vacancy.publish()

        # Publicar los posts que estén en borrador (Simulación)
        posts = vacancy.social_posts.filter(status=SocialPostStatus.DRAFT)
        for post in posts:
            post.status = SocialPostStatus.PUBLISHED
            post.posted_at = timezone.now()
            post.save()

        return vacancy

    @transaction.atomic
    def close_vacancy(self, vacancy_id: int) -> JobVacancy | None:
        """
        Cierra una vacante.

        Args:
            vacancy_id: ID de la vacante.

        Returns:
            JobVacancy | None: Vacante cerrada o None.
        """
        vacancy = self.repository.get_by_id(vacancy_id)
        if not vacancy:
            return None

        vacancy.close()
        return vacancy

    def get_tenant_vacancies(self, tenant_id: str) -> list[JobVacancy]:
        """Obtiene todas las vacantes de un tenant."""
        return list(self.repository.get_by_tenant(tenant_id))

    def get_published_vacancies(self, tenant_id: str) -> list[JobVacancy]:
        """Obtiene vacantes publicadas de un tenant."""
        return list(
            self.repository.get_published_by_tenant(tenant_id)
        )
