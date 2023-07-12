"""Маршруты для приложения chats."""

from rest_framework import routers

from chats.views import ChatViewSet

chat_router = routers.DefaultRouter()

chat_router.register('users', ChatViewSet, basename='chats')

urlpatterns = []
