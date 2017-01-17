from django.core.management.base import BaseCommand

from payment.models import Payment


class Command(BaseCommand):

    def handle(self, *args, **options):
        payments = Payment.objects.all()

        for payment in payments:
            payment.update_effective_sum()
        self.stdout.write(
            'Successfully updated %s payments\n' % payments.count())
