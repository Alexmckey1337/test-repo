from django.core.management.base import BaseCommand

from account.models import CustomUser
from navigation.models import Table


class Command(BaseCommand):
    def handle(self, *args, **options):
        users = CustomUser.objects.all()

        for user in users:
            Table.objects.update_or_create(user=user)

        self.stdout.write(
            'Successfully updated %s users\n' % users.count())
