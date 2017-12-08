import os
import csv

from django.core.management.base import BaseCommand, CommandError

from apps.summit.models import SummitAnket


def _mkdir(dir_name):
    try:
        os.makedirs(dir_name)
    except OSError as err:
        raise CommandError(err)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('filename')

    def handle(self, *args, **options):
        filename = options.get('filename')

        with open(filename, newline='') as csvfile:
            spamwriter = csv.reader(csvfile)
            for row in spamwriter:
                master_path = row[1].split('.') if row[1] else []
                SummitAnket.objects.filter(pk=row[0]).update(master_path=master_path)
