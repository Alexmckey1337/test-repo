# -*- coding: utf-8
from __future__ import unicode_literals

from django.utils import timezone

from edem.settings.celery import app
from apps.event.models import Meeting, MeetingType, ChurchReport
from apps.group.models import HomeGroup, Church
from django.db import transaction, IntegrityError


# HOME MEETING TASKS

@app.task(name='processing_home_meetings', ignore_result=True,
          max_retries=10, default_retry_delay=1000)
def processing_home_meetings():
    current_date = timezone.now().date()
    active_home_groups = HomeGroup.objects.filter(active=True)
    meeting_types = MeetingType.objects.exclude(code='night')

    try:
        with transaction.atomic():
            expired_reports = Meeting.objects.filter(status=Meeting.IN_PROGRESS)
            expired_reports.update(status=Meeting.EXPIRED)

            for home_group in active_home_groups:
                for meeting_type in meeting_types:
                    Meeting.objects.get_or_create(home_group=home_group,
                                                  owner=home_group.leader,
                                                  date=current_date,
                                                  type=meeting_type)
    except IntegrityError as e:
        print(e)


# CHURCH REPORT TASKS

@app.task(name='processing_church_reports', ignore_result=True,
          max_retries=10, default_retry_delay=1000)
def processing_church_reports():
    current_date = timezone.now().date()
    open_churches = Church.objects.filter(is_open=True)

    try:
        with transaction.atomic():
            expired_church_reports = ChurchReport.objects.filter(status=ChurchReport.IN_PROGRESS)
            expired_church_reports.update(status=ChurchReport.EXPIRED)

            for church in open_churches:
                ChurchReport.objects.get_or_create(church=church,
                                                   pastor=church.pastor,
                                                   date=current_date,
                                                   currency_id=church.report_currency)

    except IntegrityError as e:
        print(e)
