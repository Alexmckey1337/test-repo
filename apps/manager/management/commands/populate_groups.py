from django.core.management.base import BaseCommand

from apps.group.models import HomeGroup
from apps.manager.models import GroupsManager


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        home_groups = HomeGroup.objects.all()
        group_count = home_groups.count()
        error_count = 0
        self.stdout.write('Start populating fields (0 / %d)' % group_count)
        for index, group in enumerate(home_groups):
           try:
                m = GroupsManager.objects.create(person=None, group=group)

                if index % 100 == 0 and index > 0:
                    self.stdout.write('Populating in progress (%d / %d)' % (index, group_count))

           except Exception as e:
               self.stdout.write(self.style.ERROR('ERROR %s' % str(e)))
               error_count += 1
        self.stdout.write(self.style.SUCCESS('Populating finished successfully (with %d errors).' % error_count))

