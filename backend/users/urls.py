"""Маршруты приложения users."""

from django.urls import include, path
from rest_framework import routers

from users.views import UserViewSet

user_router = routers.DefaultRouter()

user_router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('auth/', include('djoser.urls.jwt')),
]
