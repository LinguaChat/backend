"""Кастомные команды управления."""

import datetime as dt
import random
import tempfile

from django.contrib.auth import get_user_model
from django.core import files
from django.core.management.base import BaseCommand, CommandError

import factory
import requests

from core.constants import (GENDERS, LANGUAGE_SKILL_LEVELS,
                            MAX_FOREIGN_LANGUAGES, MAX_NATIVE_LANGUAGES,
                            USERNAME_MAX_LENGTH)
from users.models import Country, Language, UserForeignLanguage

User = get_user_model()
GENDERS_IDS = [x[0] for x in GENDERS]
SKILL_LEVELS_IDS = [x[0] for x in LANGUAGE_SKILL_LEVELS]


def generate_username(*args):
    """ returns a random username """
    faker = factory.Faker
    return faker._get_faker().profile(
        fields=['username']
    )['username'][:USERNAME_MAX_LENGTH]


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('email', 'username')

    email = factory.faker.Faker('email')
    username = factory.LazyAttribute(generate_username)
    birth_date = factory.Faker('date_between', end_date=dt.date(2005, 7, 24))
    password = factory.django.Password('pw')
    gender = factory.Faker('random_element', elements=GENDERS_IDS)
    country = factory.Faker('random_element', elements=Country.objects.all())
    about = factory.faker.Faker('text', max_nb_chars=255)

    @factory.post_generation
    def first_name(self, create, extracted, **kwargs):
        if create:
            faker = factory.Faker
            if self.gender == 'Male':
                first_name = faker._get_faker().first_name_male()
            else:
                first_name = faker._get_faker().first_name_female()
            self.first_name = first_name
            self.save()
        else:
            return

    @factory.post_generation
    def avatar(self, create, extracted, **kwargs):
        if create and not extracted == 'no-avatar':
            gender = self.gender.lower()
            url = f"https://xsgames.co/randomusers/avatar.php?g={gender}"
            response = requests.get(url, stream=True)
            if response.status_code != requests.codes.ok:
                # Skip file
                return
            # Create a temporary file
            lf = tempfile.NamedTemporaryFile()
            for block in response.iter_content(1024 * 8):
                # If no more file then stop
                if not block:
                    break
                # Write image block to temporary file
                lf.write(block)
            # This saves the model so be sure that it is valid
            self.avatar.save(self.slug + '.jpg', files.File(lf))
        else:
            return

    @factory.post_generation
    def native_languages(self, create, extracted, **kwargs):
        if create:
            try:
                random_languages = random.choices(
                    Language.objects.all(),
                    k=random.randrange(1, MAX_NATIVE_LANGUAGES + 1)
                )
            except IndexError:
                random_languages = []
            for native_language in random_languages:
                self.native_languages.add(native_language)
        else:
            return

    @factory.post_generation
    def foreign_languages(self, create, extracted, **kwargs):
        if create:
            try:
                random_languages = random.choices(
                    Language.objects.all(),
                    k=random.randrange(1, MAX_FOREIGN_LANGUAGES + 1)
                )
            except IndexError:
                random_languages = []
            foreign_languages = [UserForeignLanguage(
                user=self,
                language=random_language,
                skill_level=random.choice(SKILL_LEVELS_IDS)
            ) for random_language in random_languages]
            UserForeignLanguage.objects.bulk_create(foreign_languages)
        else:
            return


class Command(BaseCommand):
    """Команда загрузки тестовых данных"""

    help = (
        'Загружает 16 случайных пользователей. '
        'Чтобы изменить кол-во пользователей, используйте параметр --count'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '-c',
            '--count',
            help='Кол-во',
        )
        parser.add_argument(
            '--no-avatar',
            action="store_true",
            help="Добавить пользователя(-ей) без фото",
        )

    def handle(self, *args, **options):
        self.stdout.write('Adding random users...')
        cnt = int(options.get('count') or '16')
        try:
            if options['no_avatar']:
                UserFactory.create_batch(cnt, avatar='no-avatar')
            else:
                UserFactory.create_batch(cnt)
        except Exception as e:
            raise CommandError(
                'Error adding users: %s' % (e,)
            )
        self.stdout.write('Added %d test users' % cnt)
