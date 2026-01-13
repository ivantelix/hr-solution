"""URLs de la app recruitment."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.recruitment.views import (
    ApplicationViewSet,
    JobVacancyViewSet,
    SocialPostViewSet,
)

router = DefaultRouter()
router.register(r"vacancies", JobVacancyViewSet, basename="vacancy")
router.register(r"applications", ApplicationViewSet, basename="application")
router.register(r"social-posts", SocialPostViewSet, basename="social-post")

urlpatterns = [
    path("", include(router.urls)),
]

