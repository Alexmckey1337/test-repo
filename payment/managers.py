from django.db import models
from django.db.models import Q

from rest_framework.compat import is_authenticated


class PaymentQuerySet(models.query.QuerySet):
    def base_queryset(self):
        return self.select_related(
            'currency_sum', 'currency_rate', 'manager')

    def for_user_by_all(self, user):
        from partnership.models import Deal, Partnership
        from summit.models import SummitAnket
        if not is_authenticated(user):
            return self.none()
        deal_ids = Deal.objects.for_user(user).values_list('id', flat=True)
        partner_ids = Partnership.objects.for_user(user).values_list('id', flat=True)
        anket_ids = SummitAnket.objects.for_user(user).values_list('id', flat=True)

        return self.filter(
            (Q(content_type__model='deal') & Q(object_id__in=deal_ids)) |
            (Q(content_type__model='partnership') & Q(object_id__in=partner_ids)) |
            (Q(content_type__model='summitanket') & Q(object_id__in=anket_ids))
        )

    def for_user_by_deal(self, user):
        from partnership.models import Deal
        if not is_authenticated(user):
            return self.none()
        deal_ids = Deal.objects.for_user(user).values_list('id', flat=True)

        return self.filter(
            (Q(content_type__model='deal') & Q(object_id__in=deal_ids))
        )

    def for_user_by_summit_anket(self, user):
        from summit.models import SummitAnket
        if not is_authenticated(user):
            return self.none()
        anket_ids = SummitAnket.objects.for_user(user).values_list('id', flat=True)

        return self.filter(
            (Q(content_type__model='summitanket') & Q(object_id__in=anket_ids))
        )

    def add_deal_fio(self):
        return self.extra(
            select={
                'purpose_fio': '''
                    SELECT CONCAT(auth_user.last_name, ' ', auth_user.first_name, ' ', account_customuser.middle_name) as purpose_fio
                    FROM partnership_deal
                    JOIN partnership_partnership ON partnership_deal.partnership_id = partnership_partnership.id
                    JOIN account_customuser ON partnership_partnership.user_id = account_customuser.user_ptr_id
                    JOIN auth_user ON account_customuser.user_ptr_id = auth_user.id
                    WHERE partnership_deal.id = payment_payment.object_id'''
            })


class PaymentManager(models.Manager):
    def get_queryset(self):
        return PaymentQuerySet(self.model, using=self._db)

    def base_queryset(self):
        return self.get_queryset().base_queryset()

    def for_user_by_all(self, user):
        return self.get_queryset().for_user_by_all(user=user)

    def for_user_by_deal(self, user):
        return self.get_queryset().for_user_by_deal(user=user)

    def for_user_by_summit_anket(self, user):
        return self.get_queryset().for_user_by_summit_anket(user=user)

    def add_deal_fio(self):
        return self.get_queryset().add_deal_fio()
