"""URLs de la app recruitment."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.recruitment.views import (
    JobVacancyViewSet,
    ApplicationViewSet,
)

router = DefaultRouter()
router.register(r'vacancies', JobVacancyViewSet, basename='vacancy')
router.register(r'applications', ApplicationViewSet, basename='application')

urlpatterns = [
    path('', include(router.urls)),
]
