# -*- coding: utf-8
from __future__ import unicode_literals

from datetime import datetime


from edem.settings.celery import app
from event.models import Meeting, MeetingType, ChurchReport
from group.models import HomeGroup, Church


# HOME MEETING TASKS

@app.task(name='create_new_meetings', ignore_result=True,
          max_retries=5, default_retry_delay=60)
def create_new_meetings():
    current_date = datetime.now().date()
    active_home_groups = HomeGroup.objects.filter(active=True)
    meeting_types = MeetingType.objects.all()

    for home_group in active_home_groups:
        for meeting_type in meeting_types:
            Meeting.objects.get_or_create(home_group=home_group,
                                          owner=home_group.leader,
                                          date=current_date,
                                          type=meeting_type)


@app.task(name='meetings_to_expired', ignore_result=True,
          max_retries=5, default_retry_delay=55)
def meetings_to_expired():
    expired_reports = Meeting.objects.filter(status=Meeting.IN_PROGRESS)
    expired_reports.update(status=Meeting.EXPIRED)


# CHURCH REPORT TASKS

@app.task(name='create_new_church_reports', ignore_result=True,
          max_retries=5, default_retry_delay=60)
def create_church_reports():
    current_date = datetime.now().date()
    open_churches = Church.objects.filter(is_open=True)

    for church in open_churches:
        ChurchReport.objects.get_or_create(church=church,
                                           pastor=church.pastor,
                                           date=current_date,
                                           currency=church.report_currency)


@app.task(name='church_reports_to_expired', ignore_result=True,
          max_retries=5, default_retry_delay=55)
def church_reports_to_expire():
    expired_church_reports = ChurchReport.objects.filter(status=ChurchReport.IN_PROGRESS)
    expired_church_reports.update(status=ChurchReport.EXPIRED)
