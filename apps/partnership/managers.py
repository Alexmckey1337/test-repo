from django.db import models
from django.db.models import Value as V, Sum, F
from django.db.models.functions import Concat, Coalesce


class DealQuerySet(models.query.QuerySet):
    def base_queryset(self):
        return self.select_related(
            'partnership', 'responsible',
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
                'responsible__last_name', V(' '),
                'responsible__first_name', V(' '),
                'responsible__middle_name')
            )

    def annotate_total_sum(self):
        return self.annotate(total_sum=Coalesce(Sum('payments__effective_sum'), V(0)))

    def for_user(self, user, extra_perms=True):
        if not user.is_authenticated or not user.has_partner_role:
            return self.none()
        if extra_perms and user.is_partner_supervisor_or_high:
            return self
        return self.filter(partnership__responsible=user)


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

    def for_user(self, user, extra_perms=True):
        return self.get_queryset().for_user(user=user, extra_perms=extra_perms)


class PartnerQuerySet(models.query.QuerySet):
    def base_queryset(self):
        return self.select_related(
            'user', 'user__hierarchy', 'user__master', 'responsible',
            'currency') \
            .prefetch_related('user__divisions', 'user__departments')

    def annotate_full_name(self):
        return self.annotate(
            full_name=Concat(
                'user__last_name', V(' '),
                'user__first_name', V(' '),
                'user__middle_name'))

    def for_user(self, user, extra_perms=True):
        if not user.is_authenticated or not user.has_partner_role:
            return self.none()
        if extra_perms and user.is_partner_supervisor_or_high:
            return self
        return self.filter(responsible=user)


class PartnerManager(models.Manager):
    def get_queryset(self):
        return PartnerQuerySet(self.model, using=self._db)

    def base_queryset(self):
        return self.get_queryset().base_queryset()

    def annotate_full_name(self):
        return self.get_queryset().annotate_full_name()

    def for_user(self, user, extra_perms=True):
        return self.get_queryset().for_user(user=user, extra_perms=extra_perms)


class ChurchDealQuerySet(models.query.QuerySet):
    def base_queryset(self):
        return self.select_related(
            'partnership', 'responsible',
            'partnership__church', 'currency')

    def annotate_full_name(self):
        return self.annotate(
            full_name=F('partnership__church__title'))

    def annotate_responsible_name(self):
        return self.annotate(
            responsible_name=Concat(
                'responsible__last_name', V(' '),
                'responsible__first_name'
            ))

    def annotate_total_sum(self):
        return self.annotate(total_sum=Coalesce(Sum('payments__effective_sum'), V(0)))

    def for_user(self, user, extra_perms=True):
        if not user.is_authenticated or not user.is_partner:
            return self.none()
        if extra_perms and user.is_partner_supervisor_or_high:
            return self
        return self.filter(partnership__responsible=user)


class ChurchDealManager(models.Manager):
    def get_queryset(self):
        return ChurchDealQuerySet(self.model, using=self._db)

    def base_queryset(self):
        return self.get_queryset().base_queryset()

    def annotate_full_name(self):
        return self.get_queryset().annotate_full_name()

    def annotate_responsible_name(self):
        return self.get_queryset().annotate_responsible_name()

    def annotate_total_sum(self):
        return self.get_queryset().annotate_total_sum()

    def for_user(self, user, extra_perms=True):
        return self.get_queryset().for_user(user=user, extra_perms=extra_perms)
