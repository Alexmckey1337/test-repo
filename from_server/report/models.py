from __future__ import unicode_literals
from django.utils import timezone
from datetime import timedelta
from django.db import models
from django.db.models import Sum, Value as V
from django.db.models.functions import Coalesce
from collections import OrderedDict


class UserReport(models.Model):
    user = models.ForeignKey('account.CustomUser', related_name='reports')
    date = models.DateField()
    event = models.ForeignKey('event.Event', related_name='reports')
    count = models.IntegerField(blank=True, null=True, default=0)

    class Meta:
        ordering = ['date']

    def get_count(self):
        count = 0
        if self.user.hierarchy.level > 1:
            sum = UserReport.objects.filter(user__master=self.user, event=self.event, date=self.date).aggregate(Sum('count'))
            count = sum.values()[0]
        self.count = count
        self.save()
        return self


class DayReport(models.Model):
    date = models.DateField()
    event = models.ForeignKey('event.Event', related_name='day_reports')
    department = models.ForeignKey('hierarchy.department', related_name='day_reports', null=True)

    @property
    def count(self):
        count = UserReport.objects.filter(user__hierarchy__level=1, date=self.date, user__department=self.department).count()
        return count


class MonthReport(models.Model):
    date = models.DateField()
    department = models.ForeignKey('hierarchy.department', related_name='month_reports', null=True)

    @property
    def count(self):
        month = self.date.month
        year = self.date.year
        sum = DayReport.objects.filter(date__month=month, date__year=year, department=self.department).aggregate(Sum('count'))
        count = sum.values()[0]
        return count


class YearReport(models.Model):
    date = models.DateField()
    department = models.ForeignKey('hierarchy.department', related_name='year_reports', null=True)
    @property
    def count(self):
        year = self.date.year
        sum = DayReport.objects.filter(date__year=year, department=self.department).aggregate(Sum('count'))
        count = sum.values()[0]
        return count
