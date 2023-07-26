"""Маршруты приложения chats."""

from django.urls import include, path

from rest_framework import routers

from chats.views import ChatViewSet

router = routers.DefaultRouter()

router.register('chats', ChatViewSet, basename='chats')

urlpatterns = [
    path('', include(router.urls)),
]
