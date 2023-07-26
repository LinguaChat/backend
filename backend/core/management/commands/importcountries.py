"""Кастомные команды управления."""

from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand, CommandError

from countries.conf import COUNTRIES, FLAGS_URLS
from users.models import Country


class Command(BaseCommand):
    """Команда загрузки стран"""

    help = 'Заружает коды, названия и иконки флагов стран из countries'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        if not Country.objects.exists():
            self.stdout.write('Countries not found, creating ones')
            cnt = 0
            ignored = []
            for code, name in COUNTRIES.items():
                try:
                    flag_url = FLAGS_URLS + code.lower() + '.svg'
                    flag = ImageFile(open(flag_url, 'rb'))
                    country = Country(
                        code=code,
                        name=name,
                        flag_icon=flag
                    )
                    country.save()
                    cnt += 1
                except FileNotFoundError:
                    ignored.append(flag_url)
                except Exception as e:
                    raise CommandError(
                        'Error adding country %s: %s' % (country, e)
                    )
            self.stdout.write('Added %d countries' % cnt)
            if ignored:
                self.stdout.write('Ignored: \n %s' % '\n'.join(ignored))
        else:
            self.stdout.write('Countries were found, exiting')
