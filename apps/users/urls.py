"""URLs de la app users."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.users.views import UserViewSet

# Router para ViewSets
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
]
