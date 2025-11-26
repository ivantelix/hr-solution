"""
Repositorio para JobVacancy.

Este módulo implementa el patrón Repository para JobVacancy.
"""

from typing import Protocol
from django.db.models import QuerySet

from apps.recruitment.models import JobVacancy, JobStatus


class JobVacancyRepositoryProtocol(Protocol):
    """Interface para el repositorio de vacantes."""

    def get_by_id(self, vacancy_id: int) -> JobVacancy | None:
        ...

    def get_by_tenant(self, tenant_id: str) -> QuerySet[JobVacancy]:
        ...

    def create(self, **kwargs) -> JobVacancy:
        ...

    def update(self, vacancy: JobVacancy, **kwargs) -> JobVacancy:
        ...


class JobVacancyRepository:
    """Implementación del repositorio de vacantes."""

    def get_by_id(self, vacancy_id: int) -> JobVacancy | None:
        try:
            return JobVacancy.objects.get(id=vacancy_id)
        except JobVacancy.DoesNotExist:
            return None

    def get_by_tenant(self, tenant_id: str) -> QuerySet[JobVacancy]:
        return JobVacancy.objects.filter(tenant_id=tenant_id)

    def get_published_by_tenant(
        self,
        tenant_id: str
    ) -> QuerySet[JobVacancy]:
        return JobVacancy.objects.filter(
            tenant_id=tenant_id,
            status=JobStatus.PUBLISHED
        )

    def create(self, **kwargs) -> JobVacancy:
        return JobVacancy.objects.create(**kwargs)

    def update(self, vacancy: JobVacancy, **kwargs) -> JobVacancy:
        for key, value in kwargs.items():
            setattr(vacancy, key, value)
        vacancy.save()
        return vacancy

    def delete(self, vacancy: JobVacancy) -> None:
        vacancy.delete()
