"""Маршруты приложения users."""

from django.urls import include, path

from rest_framework import routers

from users.routers import CustomRouter
from users.views import CountryViewSet, LanguageViewSet, UserViewSet

router_user = CustomRouter()
router = routers.DefaultRouter()

router_user.register('users', UserViewSet, basename='users')

router.register('languages', LanguageViewSet, basename='languages')
router.register('countries', CountryViewSet, basename='countries')


router_user._urls = [
    url for url in router_user.urls
    if not any(
        url.name.endswith(bad) for bad in [
            'set-username', 'reset-username', 'reset-username-confirm',
            'users-activation', 'users-resend-activation',
            'users-reset-password', 'users-reset-password-confirm',
        ]
    )
]

print(router_user._urls)

urlpatterns = [
    path('auth/', include('djoser.urls.jwt')),
    path(
        'users/<str:slug>/',
        UserViewSet.as_view({'get': 'retrieve'}),
        name='user-detail'
    ),
    path('', include(router_user.urls)),
    path('', include(router.urls)),
]
