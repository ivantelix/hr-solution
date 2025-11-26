"""Serializers de la app recruitment."""

from .job_vacancy_serializer import JobVacancySerializer
from .job_vacancy_create_serializer import JobVacancyCreateSerializer
from .candidate_serializer import CandidateSerializer
from .application_serializer import ApplicationSerializer
from .application_create_serializer import ApplicationCreateSerializer

__all__ = [
    "JobVacancySerializer",
    "JobVacancyCreateSerializer",
    "CandidateSerializer",
    "ApplicationSerializer",
    "ApplicationCreateSerializer",
]
