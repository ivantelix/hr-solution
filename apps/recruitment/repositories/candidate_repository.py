"""
Repositorio para Candidate.

Este módulo implementa el patrón Repository para Candidate.
"""

from typing import Protocol

from django.db.models import QuerySet

from apps.recruitment.models import Candidate


class CandidateRepositoryProtocol(Protocol):
    """Interface para el repositorio de candidatos."""

    def get_by_id(self, candidate_id: int) -> Candidate | None: ...

    def get_by_email(self, tenant_id: str, email: str) -> Candidate | None: ...

    def get_by_tenant(self, tenant_id: str) -> QuerySet[Candidate]: ...

    def create(self, **kwargs) -> Candidate: ...


class CandidateRepository:
    """Implementación del repositorio de candidatos."""

    def get_by_id(self, candidate_id: int) -> Candidate | None:
        try:
            return Candidate.objects.get(id=candidate_id)
        except Candidate.DoesNotExist:
            return None

    def get_by_email(self, tenant_id: str, email: str) -> Candidate | None:
        try:
            return Candidate.objects.get(tenant_id=tenant_id, email=email)
        except Candidate.DoesNotExist:
            return None

    def get_by_tenant(self, tenant_id: str) -> QuerySet[Candidate]:
        return Candidate.objects.filter(tenant_id=tenant_id)

    def create(self, **kwargs) -> Candidate:
        return Candidate.objects.create(**kwargs)

    def update(self, candidate: Candidate, **kwargs) -> Candidate:
        for key, value in kwargs.items():
            setattr(candidate, key, value)
        candidate.save()
        return candidate
