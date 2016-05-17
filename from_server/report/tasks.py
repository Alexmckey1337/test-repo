# -*- coding: utf-8
from hierarchy.models import Hierarchy, Department
from account.models import CustomUser as User
from event.models import Event, Participation
from report.models import UserReport as Report
from report.models import DayReport, MonthReport, YearReport
import random
import hashlib
from django.utils import timezone
from datetime import timedelta
from celery.utils.log import get_task_logger
from edem.celery import app
logger = get_task_logger(__name__)
from hierarchy.models import Department


@app.task(name='create')
def create():
    departments = Department.objects.all()
    date = timezone.now().date()
    weekday = timezone.now().weekday()+1
    users = User.objects.all()
    date_events = Event.objects.filter(date=date).all()
    weekday_events = Event.objects.filter(day=weekday).all()
    events = date_events | weekday_events
    for event in events:
        for user in users:
            participation = Participation.objects.filter(user=user, event=event).first()
            if not participation:
                participation = Participation.objects.create(user=user, event=event, check=False)
                participation.save()
                report = Report.objects.create(user=user, event=event, date=date)
                report.save()
            else:
                participation.check = False
                participation.save()
                report = Report.objects.create(user=user, event=event, date=date)
                report.save()
        for department in departments:
            day_report = DayReport.objects.create(department=department, event=event, date=date)
            day_report.save()
    return True


def create_reports():
    date = timezone.now().date()
    weekday = timezone.now().weekday()+1
    day_report = DayReport.objects.filter(date=date).first()
    if not day_report:
        events = Event.objects.filter(day=weekday).all()
        for event in events:
            day_report = DayReport.objects.create(date=date, event=event)
            day_report.save()
    month_report = MonthReport.objects.filter(date__month=date.month, date__year=date.year).first()
    if not month_report:
        month_report = MonthReport.objects.create(date=date)
        month_report.save()
    year_report = YearReport.objects.filter(date__year=date.year).first()
    if not year_report:
        year_report = YearReport.objects.create(date=date)
        year_report.save()
    return 'Ok'