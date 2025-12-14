"""
Repositorio para Application.

Este módulo implementa el patrón Repository para Application.
"""

from typing import Protocol

from django.db.models import QuerySet

from apps.recruitment.models import Application, CandidateStatus


class ApplicationRepositoryProtocol(Protocol):
    """Interface para el repositorio de postulaciones."""

    def get_by_id(self, application_id: int) -> Application | None: ...

    def get_by_vacancy(self, vacancy_id: int) -> QuerySet[Application]: ...

    def create(self, **kwargs) -> Application: ...


class ApplicationRepository:
    """Implementación del repositorio de postulaciones."""

    def get_by_id(self, application_id: int) -> Application | None:
        try:
            return Application.objects.get(id=application_id)
        except Application.DoesNotExist:
            return None

    def get_by_vacancy(self, vacancy_id: int) -> QuerySet[Application]:
        return Application.objects.filter(vacancy_id=vacancy_id)

    def get_by_candidate(self, candidate_id: int) -> QuerySet[Application]:
        return Application.objects.filter(candidate_id=candidate_id)

    def get_by_candidate_and_vacancy(
        self, candidate_id: int, vacancy_id: int
    ) -> Application | None:
        try:
            return Application.objects.get(
                candidate_id=candidate_id, vacancy_id=vacancy_id
            )
        except Application.DoesNotExist:
            return None

    def create(self, **kwargs) -> Application:
        return Application.objects.create(**kwargs)

    def update(self, application: Application, **kwargs) -> Application:
        for key, value in kwargs.items():
            setattr(application, key, value)
        application.save()
        return application

    def update_status(
        self, application: Application, status: CandidateStatus
    ) -> Application:
        application.status = status
        application.save(update_fields=["status", "updated_at"])
        return application
