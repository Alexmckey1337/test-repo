# -*- coding: utf-8
from __future__ import unicode_literals

from datetime import datetime

from edem.settings.celery import app
from event.models import Meeting, MeetingType
from group.models import HomeGroup
from django.db import transaction


@app.task(name='create_new_meetings', ignore_result=True, max_retries=5,
          default_retry_delay=10 * 50)
def create_new_meetings():
    current_date = datetime.now().date()
    home_groups_without_reports = HomeGroup.objects.filter(active=True).filter()
    meeting_types = MeetingType.objects.all()

    for home_group in home_groups_without_reports:
        with transaction.atomic():
            for meeting_type in meeting_types:
                Meeting.objects.create(home_group=home_group,
                                       owner=home_group.leader,
                                       date=current_date,
                                       type=meeting_type)


@app.task(name='meetings_to_expired', ignore_result=True, max_retries=5,
          default_retry_delay=10 * 50)
def meetings_to_expired():
    expired_reports = Meeting.objects.filter(status=Meeting.IN_PROGRESS)
    expired_reports.update(status=Meeting.EXPIRED)
