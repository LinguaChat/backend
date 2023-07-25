"""Кастомные команды управления."""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    """Команда очистки все пользователей, кроме админов"""

    help = 'Удаляет всех пользователей, кроме админов'

    def handle(self, *args, **options):
        try:
            User.objects.all().exclude(is_staff=True).delete()
        except Exception as e:
            raise CommandError(
                'Error dropping users: %s' % (e,)
            )
        self.stdout.write('All users droped. Only staff users left')
