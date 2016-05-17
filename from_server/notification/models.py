from __future__ import unicode_literals
from django.db import models
from event.models import DayOfTheWeekField

class Notification(models.Model):
    common = models.BooleanField(default=True)
    theme = models.CharField(max_length=100)
    description = models.TextField()
    date = models.DateField(null=True, blank=True)
    day = DayOfTheWeekField(null=True, blank=True)
    user = models.ForeignKey('account.CustomUser', null=True, blank=True)
