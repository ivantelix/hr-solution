"""Views de la app recruitment."""

from .application_views import ApplicationViewSet
from .job_vacancy_views import JobVacancyViewSet

__all__ = [
    "ApplicationViewSet",
    "JobVacancyViewSet",
]
