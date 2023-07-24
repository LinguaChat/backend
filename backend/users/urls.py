"""Маршруты приложения users."""

from django.urls import include, path

from rest_framework import routers

from users.views import LanguageViewSet, UserViewSet

router = routers.DefaultRouter()

router.register('users', UserViewSet, basename='users')
router.register('languages', LanguageViewSet, basename='languages')

urlpatterns = [
    path('auth/', include('djoser.urls.jwt')),
    path('', include(router.urls)),
]
