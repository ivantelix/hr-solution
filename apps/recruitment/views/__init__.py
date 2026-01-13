"""Views de la app recruitment."""

from .application_views import ApplicationViewSet
from .job_vacancy_views import JobVacancyViewSet
from .social_post_views import SocialPostViewSet

__all__ = [
    "ApplicationViewSet",
    "JobVacancyViewSet",
    "SocialPostViewSet",
]
