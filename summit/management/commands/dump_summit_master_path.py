import os
import csv

from django.core.management.base import BaseCommand, CommandError

from summit.models import SummitAnket


def _mkdir(dir_name):
    try:
        os.makedirs(dir_name)
    except OSError as err:
        raise CommandError(err)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('summit_id', type=int)
        parser.add_argument('--filename', default='summit_{}_master_path.csv')

    def handle(self, *args, **options):
        summit_id = options.get('summit_id')
        filename = options.get('filename')

        with open(filename.format(summit_id), 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile)

            for profile in SummitAnket.objects.filter(summit_id=summit_id):
                master_path = ".".join(map(lambda p: str(p), profile.user.get_ancestors().values_list('pk', flat=True)))
                spamwriter.writerow([profile.id, master_path])
