from django.core.management.base import BaseCommand

from apps.partnership.models import Partnership, PartnershipLogs


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write('Logging partners\n')
        partners = Partnership.objects.all()

        for partner in partners:
            PartnershipLogs.log_partner(partner)
        self.stdout.write(
            'Successfully logging %s partners\n' % partners.count())
