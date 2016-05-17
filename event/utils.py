from event.models import Week, Participation
from report.models import WeekReport, UserReport


def create_week_reports(int):
    try:
        week = Week.objects.get(id=int)
        from_date = week.from_date
        to_date = week.to_date
        i = 0
        if not week.week_reports.all():
            user_reports = UserReport.objects.all()
            for user_report in user_reports.all():
                try:
                    week_report = WeekReport.objects.get(user=user_report,
                                                         week=week)
                except WeekReport.DoesNotExist:
                    week_report = WeekReport.objects.create(user=user_report,
                                                            week=week,
                                                            from_date=from_date,
                                                            to_date=to_date)
                    i += 1
    except Week.DoesNotExist:
        print u"Week doesn't exist"
        return None
    print u"Created %i" % i
    return None


def get_disciple_participations(user):
    queryset = user.event_anket.participations.all()
    disciples = user.disciples
    for disciple in disciples.all():
        if disciple.event_anket.participations.all():
            queryset = queryset | get_disciple_participations(disciple)
    return queryset
