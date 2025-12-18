"""URLs de la app users."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.users.views import AuthViewSet, UserViewSet

# Router para ViewSets
router = DefaultRouter()
router.register(r"auth", AuthViewSet, basename="auth")
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    path("", include(router.urls)),
]
