from django.core.management.base import BaseCommand, CommandError
from apps.summit.models import SummitAnket


class Command(BaseCommand):
    help = 'Populate field device_code (copy it by device_id)'

    def handle(self, *args, **options):
        queryset = SummitAnket.objects.all()
        queryset_count = queryset.count()
        errors = 0
        for index, anket in enumerate(queryset):
            try:
                anket.device_code = anket.device_id if anket.device_id else ''
                anket.save()
                if index % 100 == 0:
                    self.stdout.write("Processing %d of %d" % (index, queryset_count))
            except Exception as e:
                self.stdout.write(self.style.ERROR('(Error on %d) %s' % (anket.id, e)))
                errors += 1

        self.stdout.write(self.style.SUCCESS("Successfully populate all device_code's (%d errors)." % errors))