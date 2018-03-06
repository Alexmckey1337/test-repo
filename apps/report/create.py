# -*- coding: utf-8
from __future__ import unicode_literals

from django.utils import timezone
from datetime import date

from apps.account.models import CustomUser as User
from apps.report.models import WeekReport, MonthReport, YearReport, UserReport


def months(user_id):
    try:
        master = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return "No fucking user"
    else:
        if MonthReport.objects.filter(user=master.user_report, date__month=timezone.now().month).exists():
            return "This user has already a report fot this month"
        MonthReport.objects.create(user=master.user_report, date=timezone.now())
        disciples = User.objects.filter(master=master)
        for disciple in disciples.all():
            if MonthReport.objects.filter(user=disciple.user_report,
                                          date__month=timezone.now().month).exists():
                print("This user has already a report fot this month")
                continue
            MonthReport.objects.create(user=disciple.user_report, date=timezone.now())
            disciples_of_disciple = User.objects.filter(master=disciple)
            for disciple_of_disciple in disciples_of_disciple.all():
                if MonthReport.objects.filter(user=disciple_of_disciple.user_report,
                                              date__month=timezone.now().month).exists():
                    print("This user has already a report fot this month")
                    continue
                MonthReport.objects.create(user=disciple_of_disciple.user_report,
                                           date=timezone.now())
    return "I'm done"


def years(user_id):
    try:
        master = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return "No fucking user"
    else:
        if YearReport.objects.filter(user=master.user_report, date__year=timezone.now().year).exists():
            return "This user has already a report fot this month"
        YearReport.objects.create(user=master.user_report, date=timezone.now())
        disciples = User.objects.filter(master=master)
        for disciple in disciples.all():
            if YearReport.objects.filter(user=disciple.user_report,
                                         date__year=timezone.now().year).exists():
                print("This user has already a report fot this month")
                continue
            YearReport.objects.create(user=disciple.user_report, date=timezone.now())
            disciples_of_disciple = User.objects.filter(master=disciple)
            for disciple_of_disciple in disciples_of_disciple.all():
                if YearReport.objects.filter(user=disciple_of_disciple.user_report,
                                             date__year=timezone.now().year).exists():
                    print("This user has already a report fot this year")
                    continue
                YearReport.objects.create(user=disciple_of_disciple.user_report,
                                          date=timezone.now())
    return "I'm done"


def user_reports():
    from apps.report.models import UserReport
    from apps.account.models import CustomUser as User
    users = User.objects.all()
    i = 0
    for user in users.all():
        _, created = UserReport.objects.get_or_create(user=user)
        if created:
            i += 1
    print("Created %i user reports" % i)
    return None


def check(id):
    ur = UserReport.objects.get(user__id=id)
    w = WeekReport.objects.filter(user=ur).last()
    w.get_stat()
    print("home_count %i" % w.home_count)
    print("home_value %i" % w.home_value)
    print("home_as_leader_count %i" % w.home_as_leader_count)
    print("home_as_leader_value %i" % w.home_as_leader_value)
    print("night_count %i" % w.night_count)
    print("night_as_leader_count %i" % w.night_as_leader_count)
    print("service_count %i" % w.service_count)
    print("service_as_leader_count %i" % w.service_as_leader_count)


def create_months():
    for user_report in UserReport.objects.all():
        if MonthReport.objects.filter(user=user_report, date__month=timezone.now().month).exists():
            return "This user has already a report fot this month"
        else:
            MonthReport.objects.create(user=user_report, date=timezone.now())
    return "Month reports: OK"


def create_years():
    for user_report in UserReport.objects.all():
        if YearReport.objects.filter(user=user_report, date__year=timezone.now().year).exists():
            return "This user has already a report fot this year"
        else:
            YearReport.objects.create(user=user_report, date=timezone.now())
    return "Year reports: OK"
