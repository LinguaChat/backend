"""Кастомная команда быстрого создания админа."""

import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.utils.crypto import get_random_string

from dotenv import load_dotenv

load_dotenv()

User = get_user_model()


class Command(BaseCommand):
    """Команда создания админа с заданным или случайным паролем"""

    help = (
        'Создаёт админа с username=admin и email=admin@example.com. '
        'Чтобы пароль не был случайным, добавьте в окружение параметр '
        'DJANGO_SUPERUSER_PASSWORD'
    )

    def handle(self, *args, **options):
        username = 'admin'
        email = 'admin@example.com'
        try:
            u = None
            if (
                not User.objects.filter(username=username).exists()
                and not User.objects.filter(is_superuser=True).exists()
            ):
                self.stdout.write("admin user not found, creating one...")

                new_password = os.getenv(
                    'DJANGO_SUPERUSER_PASSWORD', default=get_random_string(10)
                )
                u = User.objects.create_superuser(
                    username, email, new_password
                )

                self.stdout.write("===================================")
                self.stdout.write(
                    'A superuser `%s` was created with email '
                    '`%s` and password `%s`'
                    % (username, email, new_password)
                )
                self.stdout.write("===================================")
            else:
                self.stdout.write(
                    "admin user found. Skipping super user creation"
                )
                self.stdout.write(u)
        except Exception as e:
            raise CommandError(
                'There was an error: %s' % (e,)
            )
