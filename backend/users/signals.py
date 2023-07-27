from chats.models import Message
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

User = get_user_model()

ONLINE_THRESHOLD = 5


def update_user_activity(user):
    last_activity = user.last_activity
    now = timezone.now()

    # Проверяем, был ли пользователь активен в течение последних 5 минут
    if last_activity and (now - last_activity).seconds > ONLINE_THRESHOLD * 60:
        user.is_online = False
    else:
        user.is_online = True

    user.save()


# Сигнал при входе пользователя
@receiver(user_logged_in)
def user_logged_in_handler(sender, request, user, **kwargs):
    # Обновляем статус пользователя на "онлайн"
    user.is_online = True
    update_user_activity(user)


# Сигнал при выходе пользователя
@receiver(user_logged_out)
def user_logged_out_handler(sender, request, user, **kwargs):
    # Обновляем статус пользователя на "оффлайн"
    user.is_online = False
    update_user_activity(user)
