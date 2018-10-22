from django.core.management.base import BaseCommand

from apps.group.models import HomeGroup
from apps.manager.models import Manager


class Command(BaseCommand):
    def handle(self):
        for group in HomeGroup.objects.all():
            Manager.objects.create(person=None, group=group)