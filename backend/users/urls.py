"""Маршруты приложения users."""

from django.urls import include, path

from rest_framework import routers

from users.views import UserViewSet

user_router = routers.DefaultRouter()

user_router.register('users', UserViewSet, basename='users')

user_router._urls = [
    r for r in user_router.urls
    if not any(
        r.name.endswith(bad) for bad in [
            'set-username', 'reset-username', 'reset-username-confirm',
        ]
    )
]

urlpatterns = [
    path('auth/', include('djoser.urls.jwt')),
]
