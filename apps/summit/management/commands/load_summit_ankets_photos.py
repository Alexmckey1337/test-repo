import os
import shutil
import tarfile

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.summit.models import SummitAnket


def _mkdir(dir_name):
    try:
        os.makedirs(dir_name)
    except OSError as err:
        raise CommandError(err)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('summit_id', type=int)
        parser.add_argument('--field_by_name', default='id')
        parser.add_argument('--image_field', default='user__image_source')

    def handle(self, *args, **options):
        summit_id = options.get('summit_id')
        name = options.get('field_by_name')
        image = options.get('image_field')
        dir_name = 'ankets_images/{}'.format(summit_id)

        ankets = list(SummitAnket.objects.filter(summit_id=summit_id).values(name, image))

        _mkdir(dir_name)

        for anket in ankets:
            if anket[image]:
                try:
                    shutil.copyfile(
                        '{}/{}'.format(settings.MEDIA_ROOT, anket[image]),
                        '{}/{}.{}'.format(dir_name, anket[name], anket[image].split('.')[-1])
                    )
                except FileNotFoundError:  # noqa
                    pass
        with tarfile.open('anket_images_{}.tar.gz'.format(summit_id), 'w:gz') as tar:
            tar.add(dir_name)
        shutil.rmtree(dir_name)
