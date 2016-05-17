# -*- coding: utf-8
from event.models import Event, EventType, Week
from report.models import UserReport, WeekReport
import datetime
from datetime import timedelta


def create_week():
    first_day_of_week = datetime.date.today()
    last_day_of_week = first_day_of_week + timedelta(days=6)
    try:
        current_week = Week.objects.get(week=datetime.date.today().isocalendar()[1])
        print u"Current week is already created"
    except Week.DoesNotExist:
        current_week = Week.objects.create(week=datetime.date.today().isocalendar()[1],
                                           from_date=first_day_of_week,
                                           to_date=last_day_of_week)
        print u"Current week is created"
    return current_week


def create_event_types():
    night = EventType.objects.create(title=u"Ночная", night=True)
    home = EventType.objects.create(title=u"Домашняя", home=True)
    service = EventType.objects.create(title=u"Служение", service=True)
    return u"Event types: OK"


def create_events(week):
    night_type = EventType.objects.filter(night=True).first()
    home_type = EventType.objects.filter(home=True).first()
    service_type = EventType.objects.filter(service=True).first()
    from_date = week.from_date
    to_date = week.to_date
    try:
        night = Event.objects.get(week=week, event_type=night_type)
        print u"Current night event is already created"
    except Event.DoesNotExist:
        night = Event.objects.create(week=week, event_type=night_type, from_date=from_date, to_date=to_date)
    try:
        home = Event.objects.get(week=week, event_type=home_type)
        print u"Current home event is already created"
    except Event.DoesNotExist:
        home = Event.objects.create(week=week, event_type=home_type, from_date=from_date, to_date=to_date)
    try:
        service = Event.objects.get(week=week, event_type=service_type)
        print u"Current service event is already created"
    except Event.DoesNotExist:
        service = Event.objects.create(week=week, event_type=service_type, from_date=from_date, to_date=to_date)
    return u"Events: OK"


def create_week_reports(week):
    from_date = week.from_date
    to_date = week.to_date
    user_reports = UserReport.objects.all()
    for user_report in user_reports:
        try:
            week_report = WeekReport.objects.get(week=week, user=user_report)
            return u"Users has reports for this week"
        except WeekReport.DoesNotExist:
            week_report = WeekReport.objects.create(week=week, user=user_report,
                                                    from_date=from_date, to_date=to_date)
    return u"Week reports were created"


def create():
    week = create_week()
    create_event_types()
    create_events(week)
    create_week_reports(week)
    return u"I'm done"
