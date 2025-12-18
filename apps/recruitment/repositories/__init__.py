"""Repositorios de la app recruitment."""

from .application_repository import (
    ApplicationRepository,
    ApplicationRepositoryProtocol,
)
from .candidate_repository import (
    CandidateRepository,
    CandidateRepositoryProtocol,
)
from .job_vacancy_repository import (
    JobVacancyRepository,
    JobVacancyRepositoryProtocol,
)

__all__ = [
    "ApplicationRepository",
    "ApplicationRepositoryProtocol",
    "CandidateRepository",
    "CandidateRepositoryProtocol",
    "JobVacancyRepository",
    "JobVacancyRepositoryProtocol",
]
