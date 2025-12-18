"""Modelos de la app recruitment."""

from .application import Application
from .candidate import Candidate
from .choices import ApplicationSource, CandidateStatus, JobStatus
from .job_vacancy import JobVacancy

__all__ = [
    "Application",
    "ApplicationSource",
    "Candidate",
    "CandidateStatus",
    "JobStatus",
    "JobVacancy",
]
