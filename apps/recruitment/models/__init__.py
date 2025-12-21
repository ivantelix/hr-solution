"""Modelos de la app recruitment."""

from .application import Application
from .candidate import Candidate
from .choices import (
    ApplicationSource,
    CandidateStatus,
    JobStatus,
    SocialPlatform,
    SocialPostStatus,
)
from .job_vacancy import JobVacancy
from .social_post import VacancySocialPost

__all__ = [
    "Application",
    "ApplicationSource",
    "Candidate",
    "CandidateStatus",
    "JobStatus",
    "JobVacancy",
    "SocialPlatform",
    "SocialPostStatus",
    "VacancySocialPost",
]
