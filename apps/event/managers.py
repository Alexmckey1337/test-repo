from django.db import models
from django.db.models import Sum, Value as V, F
from django.db.models.functions import Concat
from django.db.models.functions import Coalesce


class MeetingQuerySet(models.query.QuerySet):
    def base_queryset(self):
        return self

    def for_user(self, user, extra_perms=True):
        if not user.is_authenticated:
            return self.none()
        if extra_perms and (user.is_staff or user.has_operator_perm):
            return self.base_queryset()
        return self.filter(owner__in=user.__class__.get_tree(user))

    def annotate_owner_name(self, alias='owner_name'):
        return self.annotate(
            **{alias: Concat(
                'owner__last_name', V(' '),
                'owner__first_name', V(' '),
                'owner__middle_name')})


class MeetingManager(models.Manager):
    def get_queryset(self):
        return MeetingQuerySet(self.model, using=self._db)

    def base_queryset(self):
        return self.get_queryset().base_queryset()

    def for_user(self, user, extra_perms=True):
        return self.get_queryset().for_user(user=user, extra_perms=extra_perms)

    def annotate_owner_name(self, alias='owner_name'):
        return self.get_queryset().annotate_owner_name(alias=alias)


class ChurchReportQuerySet(models.query.QuerySet):
    def base_queryset(self):
        return self

    def for_user(self, user, extra_perms=True):
        if not user.is_authenticated:
            return self.none()
        if extra_perms and (user.is_staff or user.has_operator_perm):
            return self.base_queryset()
        return self.filter(pastor__in=user.__class__.get_tree(user))

    def annotate_total_sum(self, alias='total_sum'):
        return self.annotate(**{alias: Coalesce(Sum('payments__effective_sum'), V(0))})

    def annotate_value(self, alias='value'):
        return self.annotate(**{alias: F('transfer_payments') + F('pastor_tithe')})


class ChurchReportManager(models.Manager):
    def get_queryset(self):
        return ChurchReportQuerySet(self.model, using=self._db)

    def base_queryset(self):
        return self.get_queryset().base_queryset()

    def for_user(self, user, extra_perms=True):
        return self.get_queryset().for_user(user=user, extra_perms=extra_perms)

    def annotate_total_sum(self, alias='total_sum'):
        return self.get_queryset().annotate_total_sum(alias=alias)

    def annotate_value(self, alias='value'):
        return self.get_queryset().annotate_value(alias=alias)
