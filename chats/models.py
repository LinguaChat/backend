from django.contrib.auth import get_user_model

from core.models import CreatedModifiedModel

# from django.db import models


User = get_user_model()


class Chat(CreatedModifiedModel):
    ...
