"""URLs de la app users."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.users.views import AuthViewSet, UserViewSet
from apps.users.views.token_views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
)

# Router para ViewSets
router = DefaultRouter()
router.register(r"auth", AuthViewSet, basename="auth")
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "auth/login/",
        CustomTokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    path(
        "auth/token/refresh/",
        CustomTokenRefreshView.as_view(),
        name="token_refresh",
    ),
]
