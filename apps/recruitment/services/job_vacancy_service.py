"""
Servicio de aplicación para JobVacancy.

Este módulo contiene los casos de uso relacionados con vacantes.
"""

from typing import Any

from django.db import transaction

from apps.recruitment.models import JobVacancy
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
    def publish_vacancy(self, vacancy_id: int) -> JobVacancy | None:
        """
        Publica una vacante.

        Args:
            vacancy_id: ID de la vacante.

        Returns:
            JobVacancy | None: Vacante publicada o None.
        """
        vacancy = self.repository.get_by_id(vacancy_id)
        if not vacancy:
            return None

        vacancy.publish()
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
        return list(self.repository.get_published_by_tenant(tenant_id))
