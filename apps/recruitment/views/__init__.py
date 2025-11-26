"""Views de la app recruitment."""

from .job_vacancy_views import JobVacancyViewSet
from .application_views import ApplicationViewSet

__all__ = [
    "JobVacancyViewSet",
    "ApplicationViewSet",
]
