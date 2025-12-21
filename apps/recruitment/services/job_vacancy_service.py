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
        **extra_fields: Any,
    ) -> JobVacancy:
        """
        Crea una nueva vacante.

        Args:
            tenant_id: ID del tenant.
            title: Título del puesto.
            description: Descripción.
            user_id: ID del usuario creador.
            **extra_fields: Campos adicionales.

        Returns:
            JobVacancy: Vacante creada.

        Raises:
            ValueError: Si el tenant no existe.
        """
        tenant = self.tenant_repository.get_by_id(tenant_id)
        if not tenant:
            raise ValueError("El tenant no existe.")

        return self.repository.create(
            tenant=tenant,
            title=title,
            description=description,
            created_by_id=user_id,
            **extra_fields,
        )

    @transaction.atomic
    def generate_social_previews(
        self, vacancy_id: int, platforms: list[str]
    ) -> list[VacancySocialPost]:
        """
        Genera previsualizaciones de posts para redes sociales.

        Args:
            vacancy_id: ID de la vacante.
            platforms: Lista de plataformas (linkedin, twitter, etc).

        Returns:
            list[VacancySocialPost]: Lista de posts generados.
        """
        vacancy = self.repository.get_by_id(vacancy_id)
        if not vacancy:
            raise ValueError("La vacante no existe.")

        # Limpiar borradores existentes para estas plataformas
        VacancySocialPost.objects.filter(
            vacancy=vacancy,
            platform__in=platforms,
            status=SocialPostStatus.DRAFT,
        ).delete()

        created_posts = []
        for platform in platforms:
            content = self._generate_content_template(vacancy, platform)
            post = VacancySocialPost.objects.create(
                vacancy=vacancy,
                platform=platform,
                content=content,
                status=SocialPostStatus.DRAFT,
            )
            created_posts.append(post)

        return created_posts

    def _generate_content_template(self, vacancy: JobVacancy, platform: str) -> str:
        """Genera contenido base según la plataforma."""
        if platform == SocialPlatform.LINKEDIN:
            return (
                f"🚀 ¡Estamos contratando!\n\n"
                f"En {vacancy.tenant.name} buscamos un {vacancy.title} "
                f"para unirse a nuestro equipo.\n\n"
                f"{vacancy.description[:200]}...\n\n"
                f"📍 {vacancy.location}\n"
                f"apply here!"
            )
        elif platform == SocialPlatform.TWITTER:
            return (
                f"Estamos buscando un {vacancy.title}! 🌟\n"
                f"Ubicación: {vacancy.location}\n"
                f"Apply now! #hiring #job #tech"
            )
        elif platform == SocialPlatform.FACEBOOK:
            return (
                f"📢 Oportunidad Laboral en {vacancy.tenant.name}\n\n"
                f"Buscamos: {vacancy.title}\n\n"
                f"{vacancy.description[:150]}...\n\n"
                f"¡Postúlate ahora!"
            )
        return f"New Job: {vacancy.title}"

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
