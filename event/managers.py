from django.db import models
from django.db.models import Sum, Value as V, F
from django.db.models.functions import Concat
from rest_framework.compat import is_authenticated
from django.db.models.functions import Coalesce


class MeetingQuerySet(models.query.QuerySet):
    def base_queryset(self):
        return self

    def for_user(self, user):
        if not is_authenticated(user):
            return self.none()
        if user.is_staff:
            return self.base_queryset()
        return self.filter(owner__in=user.__class__.get_tree(user))

    def annotate_owner_name(self):
        return self.annotate(
            owner_name=Concat(
                'owner__last_name', V(' '),
                'owner__first_name', V(' '),
                'owner__middle_name'))


class MeetingManager(models.Manager):
    def get_queryset(self):
        return MeetingQuerySet(self.model, using=self._db)

    def base_queryset(self):
        return self.get_queryset().base_queryset()

    def for_user(self, user):
        return self.get_queryset().for_user(user=user)

    def annotate_owner_name(self):
        return self.get_queryset().annotate_owner_name()


class ChurchReportQuerySet(models.query.QuerySet):
    def base_queryset(self):
        return self

    def for_user(self, user):
        if not is_authenticated(user):
            return self.none()
        if user.is_staff:
            return self.base_queryset()
        return self.filter(pastor__in=user.__class__.get_tree(user))

    def annotate_total_sum(self):
        return self.annotate(total_sum=Coalesce(Sum('payments__effective_sum'), V(0)))

    def annotate_value(self):
        return self.annotate(value=F('transfer_payments') + F('pastor_tithe'))


class ChurchReportManager(models.Manager):
    def get_queryset(self):
        return ChurchReportQuerySet(self.model, using=self._db)

    def base_queryset(self):
        return self.get_queryset().base_queryset()

    def for_user(self, user):
        return self.get_queryset().for_user(user=user)
