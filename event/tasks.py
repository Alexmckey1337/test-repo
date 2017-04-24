# -*- coding: utf-8
from __future__ import unicode_literals

from datetime import datetime, date
from decimal import Decimal

from edem.settings.celery import app
from event.models import Meeting, ChurchReport


@app.task(name='create_week_reports')
def create_week_reports():
    pass


@app.task(name='week_reports_verification')
def week_reports_verification():
    pass
