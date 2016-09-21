# -*- coding: utf-8
from __future__ import unicode_literals

from event.models import Week
from report.models import WeekReport, UserReport


def create_week_reports(int):
    try:
        week = Week.objects.get(id=int)
    except Week.DoesNotExist:
        print("Week doesn't exist")
        return None
    else:
        from_date = week.from_date
        to_date = week.to_date
        i = 0
        if not week.week_reports.all():
            user_reports = UserReport.objects.all()
            for user_report in user_reports.all():
                _, created = WeekReport.objects.get_or_create(user=user_report, week=week, defaults={
                    'from_date': from_date,
                    'to_date': to_date,
                })
                if created:
                    i += 1
        print("Created %i" % i)
        return None


def get_disciple_participations(user):
    queryset = user.event_anket.participations.all()
    disciples = user.disciples
    for disciple in disciples.all():
        if disciple.event_anket.participations.all():
            queryset = queryset | get_disciple_participations(disciple)
    return queryset
