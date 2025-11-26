"""Repositorios de la app recruitment."""

from .job_vacancy_repository import (
    JobVacancyRepository,
    JobVacancyRepositoryProtocol,
)
from .candidate_repository import (
    CandidateRepository,
    CandidateRepositoryProtocol,
)
from .application_repository import (
    ApplicationRepository,
    ApplicationRepositoryProtocol,
)

__all__ = [
    "JobVacancyRepository",
    "JobVacancyRepositoryProtocol",
    "CandidateRepository",
    "CandidateRepositoryProtocol",
    "ApplicationRepository",
    "ApplicationRepositoryProtocol",
]
