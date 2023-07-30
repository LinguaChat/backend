"""Маршруты приложения users."""

from django.urls import include, path
from rest_framework import routers
from users.views import CountryViewSet, LanguageViewSet, UserViewSet

router = routers.DefaultRouter()

router.register('users', UserViewSet, basename='users')
router.register('languages', LanguageViewSet, basename='languages')
router.register('countries', CountryViewSet, basename='countries')

router._urls = [
    url for url in router.urls
    if not any(
        url.name.endswith(bad) for bad in [
            'set-username', 'reset-username', 'reset-username-confirm',
        ]
    )
]

urlpatterns = [
    path('auth/', include('djoser.urls.jwt')),
    path('', include(router.urls)),
]
