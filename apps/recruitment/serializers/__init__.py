"""Serializers de la app recruitment."""

from .application_create_serializer import ApplicationCreateSerializer
from .application_serializer import ApplicationSerializer
from .candidate_serializer import CandidateSerializer
from .job_vacancy_create_serializer import JobVacancyCreateSerializer
from .job_vacancy_serializer import JobVacancySerializer
from .vacancy_social_post_serializer import VacancySocialPostSerializer

__all__ = [
    "ApplicationCreateSerializer",
    "ApplicationSerializer",
    "CandidateSerializer",
    "JobVacancyCreateSerializer",
    "JobVacancySerializer",
    "VacancySocialPostSerializer",
]
