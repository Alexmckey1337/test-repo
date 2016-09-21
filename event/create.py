# -*- coding: utf-8
from __future__ import unicode_literals

import datetime
from datetime import timedelta

from event.models import Event, EventType, Week
from report.models import UserReport, WeekReport


def create_week():
    first_day_of_week = datetime.date.today()
    last_day_of_week = first_day_of_week + timedelta(days=6)
    try:
        current_week = Week.objects.get(week=datetime.date.today().isocalendar()[1])
        print("Current week is already created")
    except Week.DoesNotExist:
        current_week = Week.objects.create(week=datetime.date.today().isocalendar()[1],
                                           from_date=first_day_of_week,
                                           to_date=last_day_of_week)
        print("Current week is created")
    return current_week


def create_event_types():
    EventType.objects.create(title="Ночная", night=True)
    EventType.objects.create(title="Домашняя", home=True)
    EventType.objects.create(title="Служение", service=True)
    return "Event types: OK"


def create_events(week):
    night_type = EventType.objects.filter(night=True).first()
    home_type = EventType.objects.filter(home=True).first()
    service_type = EventType.objects.filter(service=True).first()
    from_date = week.from_date
    to_date = week.to_date

    _, created = Event.objects.get_or_create(week=week, event_type=night_type, defaults={
        'from_date': from_date,
        'to_date': to_date, })
    if not created:
        print("Current night event is already created")

    _, created = Event.objects.get(week=week, event_type=home_type, defaults={
        'from_date': from_date,
        'to_date': to_date, })
    if not created:
        print("Current home event is already created")

    _, created = Event.objects.get(week=week, event_type=service_type, defaults={
        'from_date': from_date,
        'to_date': to_date, })
    if not created:
        print("Current service event is already created")

    return "Events: OK"


def create_week_reports(week):
    from_date = week.from_date
    to_date = week.to_date
    user_reports = UserReport.objects.all()
    for user_report in user_reports:
        _, created = WeekReport.objects.get_or_create(week=week, user=user_report, defaults={
            'from_date': from_date,
            'to_date': to_date, })
        if not created:
            return "Users has reports for this week"
    return "Week reports were created"


def create():
    week = create_week()
    create_event_types()
    create_events(week)
    create_week_reports(week)
    return "I'm done"
