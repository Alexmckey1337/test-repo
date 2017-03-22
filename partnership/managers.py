from django.conf import settings
from django.db import models
from django.db.models import Value as V, Sum
from django.db.models.functions import Concat, Coalesce
#
from rest_framework.compat import is_authenticated


class DealQuerySet(models.query.QuerySet):
    def base_queryset(self):
        return self.select_related(
            'partnership', 'responsible', 'responsible__user',
            'partnership__user', 'currency')

    def annotate_full_name(self):
        return self.annotate(
            full_name=Concat(
                'partnership__user__last_name', V(' '),
                'partnership__user__first_name', V(' '),
                'partnership__user__middle_name'))

    def annotate_responsible_name(self):
        return self.annotate(
            responsible_name=Concat(
                'responsible__user__last_name', V(' '),
                'responsible__user__first_name'
            ))

    def annotate_total_sum(self):
        return self.annotate(total_sum=Coalesce(Sum('payments__effective_sum'), V(0)))

    def for_user(self, user):
        if not is_authenticated(user) or not hasattr(user, 'partnership'):
            return self.none()
        if user.partnership.level < settings.PARTNER_LEVELS['manager']:
            return self
        return self.filter(partnership__responsible__user=user)


class DealManager(models.Manager):
    def get_queryset(self):
        return DealQuerySet(self.model, using=self._db)

    def base_queryset(self):
        return self.get_queryset().base_queryset()

    def annotate_full_name(self):
        return self.get_queryset().annotate_full_name()

    def annotate_responsible_name(self):
        return self.get_queryset().annotate_responsible_name()

    def annotate_total_sum(self):
        return self.get_queryset().annotate_total_sum()

    def for_user(self, user):
        return self.get_queryset().for_user(user=user)


class PartnerQuerySet(models.query.QuerySet):
    def base_queryset(self):
        return self.select_related(
            'user', 'user__hierarchy', 'user__master', 'responsible__user',
            'currency') \
            .prefetch_related('user__divisions', 'user__departments')

    def annotate_full_name(self):
        return self.annotate(
            full_name=Concat(
                'user__last_name', V(' '),
                'user__first_name', V(' '),
                'user__middle_name'))

    def for_user(self, user):
        if not is_authenticated(user) or not hasattr(user, 'partnership'):
            return self.none()
        if user.partnership.level < settings.PARTNER_LEVELS['manager']:
            return self
        return self.filter(responsible__user=user)


class PartnerManager(models.Manager):
    def get_queryset(self):
        return PartnerQuerySet(self.model, using=self._db)

    def base_queryset(self):
        return self.get_queryset().base_queryset()

    def annotate_full_name(self):
        return self.get_queryset().annotate_full_name()

    def for_user(self, user):
        return self.get_queryset().for_user(user=user)
