"""URLs de la app recruitment."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.recruitment.views import (
    ApplicationViewSet,
    JobVacancyViewSet,
)

router = DefaultRouter()
router.register(r"vacancies", JobVacancyViewSet, basename="vacancy")
router.register(r"applications", ApplicationViewSet, basename="application")

urlpatterns = [
    path("", include(router.urls)),
]
