from django.core.management.base import BaseCommand, CommandError
from apps.event.models import MeetingAttend, Meeting
from django.db.models import Count


class Command(BaseCommand):
    help = 'Remove duplications in meeting attends'

    def handle(self, *args, **options):
        meeting_qs = Meeting.objects.all()
        meeting_count = meeting_qs.count()
        errors = 0
        removed = 0
        self.stdout.write('Start processing fix_meeting_duplications [0/%d]' % meeting_count)
        for index, m in enumerate(meeting_qs):
            if index % 100 == 0 and index != 0:
                self.stdout.write('Processing fix_meeting_duplications [%d/%d]' % (index, meeting_count))
            try:
                attends = m.attends.all()
                duplications = attends.values('user__pk')\
                    .annotate(Count('user__pk')) \
                    .order_by()\
                    .filter(user__pk__count__gt=1)
                if duplications:
                    for user_ids in duplications.values_list('user__pk'):
                        for user in user_ids:
                            qs = attends.filter(user__pk=user, attended=True)
                            if qs.count() > 1:
                                first = qs[0].pk
                                qs_attended = qs.exclude(pk=first)
                                removed += qs_attended.count()
                                qs_attended.delete()
                                qs_not_attended = attends.filter(user__pk=user, attended=False)
                                removed += qs_not_attended.count()
                                qs_not_attended.delete()
                            elif qs.count() == 1:
                                qs_not_attended = attends.filter(user__pk=user, attended=False)
                                removed += qs_not_attended.count()
                                qs_not_attended.delete()
                            else:
                                qs = attends.filter(user__pk=user, attended=False)
                                first = qs[0].pk
                                qs = qs.exclude(pk=first)
                                removed += qs.count()
                                qs.delete()
            except Exception as e:
                self.stdout.write(self.style.ERROR("ERROR ON {}: {}".format(index, str(e))))
                errors += 1
        self.stdout.write(self.style.SUCCESS('Successfully removed duplications (with %d errors). \nRemoved: %d' % (errors, removed)))