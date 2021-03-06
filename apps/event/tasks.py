from django.utils import timezone

from apps.payment.models import Currency
from edem.settings.celery import app
from apps.event.models import Meeting, MeetingType, ChurchReport
from apps.group.models import HomeGroup, Church
from django.db import transaction, IntegrityError


# HOME MEETING TASKS

def make_reports_expired(meeting_type):
    expired_reports = Meeting.objects.filter(
        status=Meeting.IN_PROGRESS,
        type=meeting_type
    )
    expired_reports.update(status=Meeting.EXPIRED)


def create_meeting_with_church(home_group, current_date, meeting_type):
    Meeting.objects.get_or_create(
        home_group=home_group, owner=home_group.leader,
        date=current_date, type=meeting_type
    )


def create_meeting_without_church(home_group, current_date, meeting_type, currency):
    Meeting.objects.get_or_create(
        home_group=home_group, owner=home_group.leader, date=current_date,
        type=meeting_type, tithe=0, donation=0, currency=currency
    )


@app.task(name='processing_home_meetings', ignore_result=True,
          max_retries=10, default_retry_delay=1000)
def processing_home_meetings():
    """
    Report for home meeting type "home"
    """
    current_date = timezone.now().date()
    active_home_groups = HomeGroup.objects.filter(active=True)
    meeting_type = MeetingType.objects.get(code='home')
    currency = Currency.objects.get(code='uah')

    try:
        with transaction.atomic():
            make_reports_expired(meeting_type)

            for home_group in active_home_groups:
                if home_group.church:
                    create_meeting_with_church(home_group, current_date, meeting_type)
                else:
                    create_meeting_without_church(home_group, current_date, meeting_type, currency)

    except IntegrityError as e:
        print(e)


@app.task(name='processing_home_service_meetings', ignore_result=True,
          max_retries=10, default_retry_delay=1000)
def processing_home_service_meetings():
    """
    Report for home meeting type "service"
    """
    current_date = timezone.now().date()
    active_home_groups = HomeGroup.objects.filter(active=True)
    meeting_type = MeetingType.objects.get(code='service')
    currency = Currency.objects.get(code='uah')

    try:
        with transaction.atomic():
            make_reports_expired(meeting_type)

            for home_group in active_home_groups:
                if home_group.church:
                    create_meeting_with_church(home_group, current_date, meeting_type)
                else:
                    create_meeting_without_church(home_group, current_date, meeting_type, currency)

    except IntegrityError as e:
        print(e)


@app.task(name='processing_home_night_meetings', ignore_result=True,
          max_retries=10, default_retry_delay=1000)
def processing_home_night_meetings():
    """
    Report for home meeting type "night"
    """
    current_date = timezone.now().date()
    active_home_groups = HomeGroup.objects.filter(active=True)
    meeting_type = MeetingType.objects.get(code='night')
    currency = Currency.objects.get(code='uah')

    try:
        with transaction.atomic():
            for home_group in active_home_groups:
                if home_group.church:
                    create_meeting_with_church(home_group, current_date, meeting_type)
                else:
                    create_meeting_without_church(home_group, current_date, meeting_type, currency)

    except IntegrityError as e:
        print(e)


@app.task(name='make_home_night_meetings_expired', ignore_result=True,
          max_retries=10, default_retry_delay=1000)
def make_home_night_meetings_expired():
    """
    Make home meetings type 'night' expired
    """
    try:
        with transaction.atomic():
            meeting_type = MeetingType.objects.get(code='night')

            make_reports_expired(meeting_type)

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
