"""Кастомная команда загрузки интересов."""

from django.core.management.base import BaseCommand, CommandError

from core.constants import USERS_BASE_INTERESTS
from users.models import Interest


class Command(BaseCommand):
    """Команда загрузки базовых интересов пользователей"""

    help = 'Заружает названия базовых интересов пользователей из core'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        self.stdout.write('Importing interest...')
        cnt = 0
        for interest_name in USERS_BASE_INTERESTS:
            try:
                interest, created = Interest.objects.get_or_create(
                    name=interest_name
                )
                if created:
                    cnt += 1
            except Exception as e:
                raise CommandError(
                    'Error adding interest %s{interest}: %s{error}'.format(
                        interest=interest, error=e
                    )
                )
        self.stdout.write('Added %d interest' % cnt)
