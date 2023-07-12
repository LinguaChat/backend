"""Маршруты для приложения chats."""

from rest_framework import routers

from .views import ChatViewSet

chat_router = routers.DefaultRouter()

chat_router.register('chats', ChatViewSet, basename='chats')

urlpatterns = []
