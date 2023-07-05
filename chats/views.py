from django.contrib.auth import get_user_model
from rest_framework import viewsets

User = get_user_model()


class ChatViewSet(viewsets.ModelViewSet):
    ...
