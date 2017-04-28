# -*- coding: utf-8
from __future__ import unicode_literals

from datetime import datetime, date
from decimal import Decimal

from edem.settings.celery import app
from event.models import Meeting, ChurchReport
from group.models import HomeGroup


@app.task(name='create_new_meetings')
def create_new_meetings():
    current_date = datetime.now().date()
    active_home_groups = HomeGroup.objects.filter(active=True)

    """
    Meeting.objects.bulk_create([
        Meeting(home_group=)
    ])
    """


@app.task(name='meetings_to_expired')
def meetings_to_expired():
    pass
