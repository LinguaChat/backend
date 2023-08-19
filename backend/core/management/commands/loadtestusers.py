"""Кастомная команда загрузки тестовых пользователей."""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from users.models import Country, Language, UserLanguage

User = get_user_model()

USERS_INFO = [
    {
        "password": "ML7kwFXh9o",
        "username": "Dyah",
        "first_name": "Dyah",
        "email": "dyah@yandex.ru",
        "birth_date": "1992-06-01",
        "about": "Hello! I’m Dyah from Indonesia. I like to make new friends. Feel free to chat me!",
        "gender": "Female",
        "interests": [],
        "languages": [{"isocode": "Id", "skill_level": "Native"}, {"isocode": "En", "skill_level": "Native"}, {"isocode": "Ru", "skill_level": "Amateur"}],
        "country": Country.objects.get(code="id"),
        "avatar": "icons/users/Dyah.png",
    },
    {
        "password": "ML7kwFXh9o",
        "username": "Elek",
        "first_name": "Elek",
        "email": "elek@yandex.ru",
        "birth_date": "1999-06-01",
        "about": "Hello from Turkey!",
        "gender": "Male",
        "interests": [],
        "languages": [{"isocode": "Tr", "skill_level": "Native"}, {"isocode": "En", "skill_level": "Native"}, {"isocode": "Ru", "skill_level": "Amateur"}],
        "country": Country.objects.get(code="tr"),
        "avatar": "icons/users/Elek.png",
    },
    {
        "password": "ML7kwFXh9o",
        "username": "Jay",
        "first_name": "Jay",
        "email": "jay@yandex.ru",
        "birth_date": "1980-06-01",
        "about": "Hi ! I’m Jay! I’m university student! I’m asian american! I can help you with English!",
        "gender": "Female",
        "interests": [],
        "languages": [{"isocode": "Id", "skill_level": "Native"}, {"isocode": "En", "skill_level": "Native"}, {"isocode": "Ru", "skill_level": "Amateur"}],
        "country": Country.objects.get(code="us"),
        "avatar": "icons/users/Jay.png",
    },
    {
        "password": "ML7kwFXh9o",
        "username": "Andrew",
        "first_name": "Andrew",
        "email": "andrew@yandex.ru",
        "birth_date": "1983-06-01",
        "about": "Hello everyone! My name is Andrew, I’m open to make more friends. Let’s go to talk!",
        "gender": "Male",
        "interests": [],
        "languages": [{"isocode": "Nl", "skill_level": "Native"}, {"isocode": "En", "skill_level": "Native"}, {"isocode": "Pt", "skill_level": "Profi"}, {"isocode": "Ru", "skill_level": "Amateur"}],
        "country": Country.objects.get(code="nl"),
        "avatar": "icons/users/Andrew.png",
    },
    {
        "password": "ML7kwFXh9o",
        "username": "Matey",
        "first_name": "Matey",
        "email": "matey@yandex.ru",
        "birth_date": "1987-06-01",
        "about": "Всем привет! Я хочу выучить русский язык, чтобы свободно говорить и открыть свой бизнес в России",
        "gender": "Male",
        "interests": [],
        "languages": [{"isocode": "Ro", "skill_level": "Native"}, {"isocode": "En", "skill_level": "Native"}, {"isocode": "Ru", "skill_level": "Expert"}],
        "country": Country.objects.get(code="ro"),
        "avatar": "icons/users/Matey.png",
    },
    {
        "password": "ML7kwFXh9o",
        "username": "Sheena",
        "first_name": "Sheena",
        "email": "sheena@yandex.ru",
        "birth_date": "2004-06-01",
        "about": "I’m a student and my hobby is learning language. I'm very friendly yet shy at first.",
        "gender": "Female",
        "interests": [],
        "languages": [{"isocode": "It", "skill_level": "Native"}, {"isocode": "En", "skill_level": "Native"}, {"isocode": "Es", "skill_level": "Profi"}, {"isocode": "Ru", "skill_level": "Amateur"}],
        "country": Country.objects.get(code="it"),
        "avatar": "icons/users/Sheena.png",
    },
    {
        "password": "ML7kwFXh9o",
        "username": "Omar",
        "first_name": "Omar",
        "email": "omar@yandex.ru",
        "birth_date": "2000-09-01",
        "about": "Omar еще не заполнил информацию о себе",
        "gender": "Male",
        "interests": [],
        "languages": [{"isocode": "Ar", "skill_level": "Native"}, {"isocode": "En", "skill_level": "Native"}, {"isocode": "Ru", "skill_level": "Amateur"}],
        "country": Country.objects.get(code="ar"),
        "avatar": "icons/users/Omar.png",
    },
    {
        "password": "ML7kwFXh9o",
        "username": "Iorrain",
        "first_name": "Iorrain",
        "email": "iorrain@yandex.ru",
        "birth_date": "1993-06-01",
        "about": "Привет! Я учу русский полгода. Живу в Австралии. I would love to help anyone learning English btw.",
        "gender": "Female",
        "interests": [],
        "languages": [{"isocode": "En", "skill_level": "Native"}, {"isocode": "Ja", "skill_level": "Profi"}, {"isocode": "Ru", "skill_level": "Amateur"}],
        "country": Country.objects.get(code="au"),
        "avatar": "icons/users/Iorrain.png",
    },
    {
        "password": "ML7kwFXh9o",
        "username": "Ahmed",
        "first_name": "Ahmed",
        "email": "ahmed@yandex.ru",
        "birth_date": "1995-06-01",
        "about": "Hello in my world",
        "gender": "Male",
        "interests": [],
        "languages": [{"isocode": "Ar", "skill_level": "Native"}, {"isocode": "En", "skill_level": "Native"}, {"isocode": "Ru", "skill_level": "Amateur"}],
        "country": Country.objects.get(code="ar"),
        "avatar": "icons/users/Ahmed.png",
    },
    {
        "password": "ML7kwFXh9o",
        "username": "Daniel",
        "first_name": "Daniel",
        "email": "daniel@yandex.ru",
        "birth_date": "1998-09-01",
        "about": "If you’d like practice English or Spanish and help me with Russian, feel free to say hello!",
        "gender": "Male",
        "interests": [],
        "languages": [{"isocode": "Es", "skill_level": "Native"}, {"isocode": "En", "skill_level": "Native"}, {"isocode": "Ru", "skill_level": "Amateur"}],
        "country": Country.objects.get(code="es"),
        "avatar": "icons/users/Daniel.png",
    },
    {
        "password": "ML7kwFXh9o",
        "username": "Sara",
        "first_name": "Sara",
        "email": "sara@yandex.ru",
        "birth_date": "1982-06-01",
        "about": "I’ve just started to learn Russian. So far only know the alphabet and a few basic words.",
        "gender": "Female",
        "interests": [],
        "languages": [{"isocode": "En", "skill_level": "Native"}, {"isocode": "Ru", "skill_level": "Newbie"}],
        "country": Country.objects.get(code="gb"),
        "avatar": "icons/users/Sara.png",
    },
    {
        "password": "ML7kwFXh9o",
        "username": "Chris",
        "first_name": "Chris",
        "email": "chris@yandex.ru",
        "birth_date": "2002-06-01",
        "about": "Всем привет! Меня зовут Крис",
        "gender": "Female",
        "interests": [],
        "languages": [{"isocode": "De", "skill_level": "Native"}, {"isocode": "En", "skill_level": "Native"}, {"isocode": "Ru", "skill_level": "Amateur"}],
        "country": Country.objects.get(code="de"),
        "avatar": "icons/users/Chris.png",
    },
    {
        "password": "ML7kwFXh9o",
        "username": "Kadir",
        "first_name": "Kadir",
        "email": "kadir@yandex.ru",
        "birth_date": "2001-06-01",
        "about": "Хочу выучить русский язык для работы.",
        "gender": "Male",
        "interests": [],
        "languages": [{"isocode": "Tr", "skill_level": "Native"}, {"isocode": "En", "skill_level": "Native"}, {"isocode": "Ru", "skill_level": "Amateur"}],
        "country": Country.objects.get(code="tr"),
        "avatar": "icons/users/Kadir.png",
    },
    {
        "password": "ML7kwFXh9o",
        "username": "Josi",
        "first_name": "Josi",
        "email": "josi@yandex.ru",
        "birth_date": "2003-06-01",
        "about": "Hi you! If you help i learning English or German i can help you, feel free to text me",
        "gender": "Female",
        "interests": [],
        "languages": [{"isocode": "De", "skill_level": "Native"}, {"isocode": "En", "skill_level": "Native"}, {"isocode": "Ru", "skill_level": "Amateur"}],
        "country": Country.objects.get(code="de"),
        "avatar": "icons/users/Josi.png",
    },
    {
        "password": "ML7kwFXh9o",
        "username": "Korren",
        "first_name": "Korren",
        "email": "korren@yandex.ru",
        "birth_date": "1990-06-01",
        "about": "Я могу немного говорить и понимать, но мне нужно улучшить свои навыки чтения и письма.",
        "gender": "Female",
        "interests": [],
        "languages": [{"isocode": "En", "skill_level": "Native"}, {"isocode": "Ru", "skill_level": "Expert"}],
        "country": Country.objects.get(code="us"),
        "avatar": "icons/users/Korren.png",
    },
    {
        "password": "ML7kwFXh9o",
        "username": "Jiang",
        "first_name": "Jiang",
        "email": "jiang@yandex.ru",
        "birth_date": "1986-06-01",
        "about": "Hi there! I’m glad you came to my page. I want to improve my speaking with native speakers.",
        "gender": "Male",
        "interests": [],
        "languages": [{"isocode": "Nl", "skill_level": "Native"}, {"isocode": "En", "skill_level": "Native"}, {"isocode": "Ru", "skill_level": "Newbie"}, {"isocode": "Ko", "skill_level": "Profi"}],
        "country": Country.objects.get(code="us"),
        "avatar": "icons/users/Jiang.png",
    },
    {
        "password": "ML7kwFXh9o",
        "username": "Pulkit",
        "first_name": "Pulkit",
        "email": "pulkit@yandex.ru",
        "birth_date": "1996-06-01",
        "about": "I want to learn russian and make good friends here.",
        "gender": "Male",
        "interests": [],
        "languages": [{"isocode": "Hi", "skill_level": "Native"}, {"isocode": "En", "skill_level": "Native"}, {"isocode": "Ru", "skill_level": "Newbie"}],
        "country": Country.objects.get(code="us"),
        "avatar": "icons/users/Pulkit.png",
    },
    {
        "password": "ML7kwFXh9o",
        "username": "Pulkit2",
        "first_name": "Pulkit",
        "email": "pulkit2@yandex.ru",
        "birth_date": "1996-06-01",
        "about": "I want to move to Russia. Help me lern russian please)",
        "gender": "Female",
        "interests": [],
        "languages": [{"isocode": "Th", "skill_level": "Native"}, {"isocode": "En", "skill_level": "Native"}, {"isocode": "Ru", "skill_level": "Expert"}],
        "country": Country.objects.get(code="th"),
        "avatar": "icons/users/PulkitTh.png",
    },
]

class Command(BaseCommand):
    """Команда загрузки тестовых данных"""

    help = (
        'Загружает 18 тестовых пользователей. '
    )

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        self.stdout.write('Adding test users...')
        cnt = 0
        try:
            for data in USERS_INFO:
                interests = data.pop('interests', [])
                languages = data.pop('languages', [])
                user = User.objects.create(**data)
                user.interests.set(interests)
                for language in languages:
                    UserLanguage.objects.create(
                        user=user,
                        language=Language.objects.get(
                            isocode=language['isocode']
                        ),
                        skill_level=language['skill_level']
                    )
                cnt += 1
        except Exception as e:
            raise CommandError(
                'Error adding users: %s' % (e,)
            )
        self.stdout.write('Added %d test users' % cnt)
