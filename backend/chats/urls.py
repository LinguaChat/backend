"""Маршруты приложения chats."""

from rest_framework import routers

from chats.views import ChatViewSet

chat_router = routers.DefaultRouter()

chat_router.register('chats', ChatViewSet, basename='chats')

urlpatterns = []
