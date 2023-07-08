from django.contrib.auth import get_user_model

from core.models import DateCreatedModel, DateEditedModel

# from django.db import models


User = get_user_model()


class Chat(DateCreatedModel, DateEditedModel):
    '''Модель чата'''
    ...