from django.urls import include, path

from rest_framework import routers

from .views import ChatViewSet

router = routers.DefaultRouter()

router.register('chats', ChatViewSet, basename='chats')

urlpatterns = [
    path('', include(router.urls)),
]
