from django.core.management.base import BaseCommand, CommandError
from django.conf.locale import LANG_INFO

from users.models import Language


class Command(BaseCommand):
    help = 'Imports language codes and names from django.conf.locale.LANG_INFO'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        cnt = 0
        for lang in LANG_INFO:
            if len(lang) == 2:
                #we only care about the 2 letter iso codes
                try:
                    l = Language(isocode=lang,
                                 name=LANG_INFO[lang]['name'],
                                 name_local=LANG_INFO[lang]['name_local'])
                    l.save()
                    cnt += 1
                except Exception as e:
                    raise CommandError('Error adding language %s' % lang)
        self.stdout.write('Added %d languages to users' % cnt)
