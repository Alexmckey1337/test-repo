from django.conf import settings
from django.db import models
from django.db.models import Sum, Value as V
from django.db.models.functions import Coalesce, Concat
from rest_framework.compat import is_authenticated


class ProfileQuerySet(models.query.QuerySet):
    def base_queryset(self):
        return self.select_related(
            'user', 'user__hierarchy', 'user__master', 'summit', 'summit__type'). \
            prefetch_related('user__divisions', 'user__departments')

    def annotate_total_sum(self):
        return self.annotate(
            total_sum=Coalesce(Sum('payments__effective_sum'), V(0)))

    def annotate_full_name(self):
        return self.annotate(
            full_name=Concat(
                'last_name', V(' '),
                'first_name', V(' '),
                'middle_name'))

    def for_user(self, user):
        if not is_authenticated(user):
            return self.none()
        if user.is_staff:
            return self
        summit_ids = set(user.summit_profiles.filter(
            role__gte=settings.SUMMIT_ANKET_ROLES['consultant']).values_list('summit_id', flat=True))
        return self.filter(summit__in=summit_ids)


class ProfileManager(models.Manager):
    def get_queryset(self):
        return ProfileQuerySet(self.model, using=self._db)

    def base_queryset(self):
        return self.get_queryset().base_queryset()

    def annotate_total_sum(self):
        return self.get_queryset().annotate_total_sum()

    def annotate_full_name(self):
        return self.get_queryset().annotate_full_name()

    def for_user(self, user):
        return self.get_queryset().for_user(user=user)


class SummitQuerySet(models.query.QuerySet):
    def base_queryset(self):
        return self.select_related(
            'type', 'currency')

    def for_user(self, user):
        if not is_authenticated(user):
            return self.none()
        if user.is_staff:
            return self
        summit_ids = set(user.summit_profiles.filter(
            role__gte=settings.SUMMIT_ANKET_ROLES['consultant']).values_list('summit_id', flat=True))
        return self.filter(pk__in=summit_ids)


class SummitManager(models.Manager):
    def get_queryset(self):
        return SummitQuerySet(self.model, using=self._db)

    def base_queryset(self):
        return self.get_queryset().base_queryset()

    def for_user(self, user):
        return self.get_queryset().for_user(user=user)
