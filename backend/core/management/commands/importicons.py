"""Кастомная команда загрузки интересов и целей."""

import shutil
from os import listdir
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from countries.conf import FLAGS_URLS


class Command(BaseCommand):
    """Команда загрузки базовых интересов и целей пользователей"""

    help = (
        'Заружает названия и иконки целей, а также названия базовых интересов '
        ' из core constants'
    )

    def add_arguments(self, parser):
        pass

    def load_icons(self, from_path, to_path):
        cnt = 0
        for icon_name in listdir(from_path):
            try:
                Path(to_path).mkdir(parents=True, exist_ok=True)
                shutil.copy(from_path + icon_name, to_path)
                cnt += 1
            except Exception as e:
                raise CommandError(
                    'Error importing icon %s{icon}: %s{error}'.format(
                        icon=icon_name, error=e
                    ),
                    '\tSkipping...'
                )
        return cnt


    def handle(self, *args, **options):
        self.stdout.write('Importing goals icons...\n')
        goals_path = "core/icons/goals/"
        cnt = self.load_icons(goals_path, "media/icons/goals/")
        self.stdout.write('\n{cnt} icons was imported'.format(cnt=cnt))
        self.stdout.write('*********')
        self.stdout.write('Importing users icons...\n')
        users_path = "core/icons/users/"
        cnt = self.load_icons(users_path, "media/icons/goals/")
        self.stdout.write('\n{cnt} icons was imported'.format(cnt=cnt))
        self.stdout.write('*********')
        self.stdout.write('Importing countries flags icons...\n')
        cnt = self.load_icons(FLAGS_URLS, "media/icons/countries/")
        self.stdout.write('\n{cnt} icons was imported'.format(cnt=cnt))
