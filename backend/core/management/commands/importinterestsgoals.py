"""Кастомная команда загрузки интересов и целей."""

from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand, CommandError

from core.constants import GOALS_ICONS_URLS, USERS_BASE_INTERESTS, USERS_GOALS
from users.models import Goal, Interest


class Command(BaseCommand):
    """Команда загрузки базовых интересов и целей пользователей"""

    help = (
        'Заружает названия и иконки целей, а также названия базовых интересов '
        ' из core constants'
    )

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        self.stdout.write('1. Importing interest...')
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

        self.stdout.write('2. Importing goals...')
        ignored = []
        for icon_code, name in USERS_GOALS.items():
            try:
                icon_url = GOALS_ICONS_URLS + icon_code + '.svg'
                icon = ImageFile(open(icon_url, 'rb'))
                goal, created = Goal.objects.get_or_create(
                    name=name,
                    icon=icon
                )
                if created:
                    cnt += 1
            except FileNotFoundError:
                ignored.append(icon_url)
            except Exception as e:
                raise CommandError(
                    'Error adding goal %s{goal}: %s{error}'.format(
                        goal=goal, error=e
                    )
                )
        self.stdout.write('Added %d goals' % cnt)
        if ignored:
            self.stdout.write('Files not found: \n %s' % '\n'.join(ignored))
