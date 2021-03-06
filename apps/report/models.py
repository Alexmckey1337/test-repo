from django.db import models
from django.db.models import Sum

from apps.event.models import Participation
from common import date_utils


class UserReport(models.Model):
    user = models.OneToOneField('account.CustomUser', on_delete=models.PROTECT,
                                related_name='user_report', null=True, blank=True)

    def __str__(self):
        return self.user.get_full_name()


class AbstractReport(models.Model):
    home_count = models.IntegerField(default=0)
    home_value = models.IntegerField(default=0)
    night_count = models.IntegerField(default=0)
    service_count = models.IntegerField(default=0)
    service_coming_count = models.IntegerField(default=0)
    service_repentance_count = models.IntegerField(default=0)
    home_as_leader_count = models.IntegerField(default=0)
    home_as_leader_value = models.IntegerField(default=0)
    night_as_leader_count = models.IntegerField(default=0)
    service_as_leader_count = models.IntegerField(default=0)
    service_as_leader_coming_count = models.IntegerField(default=0)
    service_as_leader_repentance_count = models.IntegerField(default=0)

    class Meta:
        abstract = True

    def __str__(self):
        return self.fullname

    @property
    def fullname(self):
        s = ''
        if len(self.user.user.last_name) > 0:
            s = s + self.user.user.last_name + ' '
        if len(self.user.user.first_name) > 0:
            s = s + self.user.user.first_name[0] + '.'
        if len(self.user.user.middle_name) > 0:
            s = s + self.user.user.middle_name[0] + '.'
        return s.strip()

    @property
    def uid(self):
        return self.user.user.id

    @property
    def mid(self):
        return self.user.user.master.id


class WeekReport(AbstractReport):
    week = models.ForeignKey('event.Week', on_delete=models.PROTECT, null=True, blank=True, related_name='week_reports')
    from_date = models.DateField(default=date_utils.today)
    to_date = models.DateField(default=date_utils.today)
    user = models.ForeignKey(UserReport, on_delete=models.PROTECT, related_name='week_reports')

    def __str__(self):
        return "%s, week  %i" % (self.user.user.get_full_name(), self.week.week)

    def get_home(self):
        week = self.week
        user = self.user.user
        participations = Participation.objects.filter(event__week=week,
                                                      user__user=user,
                                                      event__event_type__home=True).all()
        sum_count = participations.aggregate(Sum('count'))
        sum_value = participations.aggregate(Sum('result_value'))
        leader_sum_count = participations.aggregate(Sum('count_as_leader'))
        leader_sum_value = participations.aggregate(Sum('value_as_leader'))
        count = sum_count.values()[0]
        value = sum_value.values()[0]
        home_as_leader_count = leader_sum_count.values()[0]
        home_as_leader_value = leader_sum_value.values()[0]
        self.home_count = count
        self.home_value = value
        self.home_as_leader_count = home_as_leader_count
        self.home_as_leader_value = home_as_leader_value
        self.save()

    def get_night(self):
        week = self.week
        user = self.user.user
        participations = Participation.objects.filter(event__week=week,
                                                      user__user=user,
                                                      event__event_type__night=True).all()
        sum_count = participations.aggregate(Sum('count'))
        leader_sum_count = participations.aggregate(Sum('count_as_leader'))
        count = sum_count.values()[0]
        night_as_leader_count = leader_sum_count.values()[0]
        self.night_count = count
        self.night_as_leader_count = night_as_leader_count
        self.save()

    def get_service(self):
        week = self.week
        user = self.user.user
        participations = Participation.objects.filter(event__week=week,
                                                      user__user=user,
                                                      event__event_type__service=True).all()
        sum_count = participations.aggregate(Sum('count'))
        leader_sum_count = participations.aggregate(Sum('count_as_leader'))
        count = sum_count.values()[0]
        service_as_leader_count = leader_sum_count.values()[0]
        self.service_count = count
        self.service_as_leader_count = service_as_leader_count
        self.save()


class MonthReport(AbstractReport):
    date = models.DateField()
    user = models.ForeignKey(UserReport, on_delete=models.PROTECT, related_name='month_reports', null=True, blank=True)

    def get_stat(self):
        month = self.date.month
        weeks = WeekReport.objects.filter(from_date__month=month)
        self.home_count = weeks.aggregate(Sum('home_count'))
        self.home_value = weeks.aggregate(Sum('home_value'))
        self.night_count = weeks.aggregate(Sum('night_count'))
        self.service_count = weeks.aggregate(Sum('service_count'))
        self.service_coming_count = weeks.aggregate(Sum('service_coming_count'))
        self.service_repentance_count = weeks.aggregate(Sum('service_repentance_count'))
        self.home_as_leader_count = weeks.aggregate(Sum('home_as_leader_count'))
        self.home_as_leader_value = weeks.aggregate(Sum('home_as_leader_value'))
        self.night_as_leader_count = weeks.aggregate(Sum('night_as_leader_count'))
        self.service_as_leader_count = weeks.aggregate(Sum('service_as_leader_count'))
        self.service_as_leader_coming_count = weeks.aggregate(Sum('service_as_leader_coming_count'))
        self.service_as_leader_repentance_count = weeks.aggregate(Sum('service_as_leader_repentance_count'))
        self.save()


class YearReport(AbstractReport):
    date = models.DateField()
    user = models.ForeignKey(UserReport, on_delete=models.PROTECT, related_name='year_reports', null=True, blank=True)

    def get_stat(self):
        year = self.date.year
        months = MonthReport.objects.filter(date__year=year)
        self.home_count = months.aggregate(Sum('home_count'))
        self.home_value = months.aggregate(Sum('home_value'))
        self.night_count = months.aggregate(Sum('night_count'))
        self.service_count = months.aggregate(Sum('service_count'))
        self.service_coming_count = months.aggregate(Sum('service_coming_count'))
        self.service_repentance_count = months.aggregate(Sum('service_repentance_count'))
        self.home_as_leader_count = months.aggregate(Sum('home_as_leader_count'))
        self.home_as_leader_value = months.aggregate(Sum('home_as_leader_value'))
        self.night_as_leader_count = months.aggregate(Sum('night_as_leader_count'))
        self.service_as_leader_count = months.aggregate(Sum('service_as_leader_count'))
        self.service_as_leader_coming_count = months.aggregate(Sum('service_as_leader_coming_count'))
        self.service_as_leader_repentance_count = months.aggregate(Sum('service_as_leader_repentance_count'))
        self.save()

# @receiver(signals.post_save, sender=WeekReport)
# def sync_event(sender, instance, **kwargs):
#    instance.get_stat()
