from django.core.management.base import BaseCommand

from apps.summit.models import SummitAnket


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('summit_id', nargs='?', type=int)

    def handle(self, *args, **options):
        ankets = SummitAnket.objects.all()

        summit_id = options.get('summit_id')
        if summit_id:
            ankets = ankets.filter(summit_id=summit_id)

        for anket in ankets:
            anket.update_value()
        self.stdout.write(
            'Successfully updated %s ankets\n' % ankets.count())
