from django.db import models
from django.db.models import Q

from rest_framework.compat import is_authenticated
from django.db.models import Value as V, F
from django.db.models.functions import Concat


class PaymentQuerySet(models.query.QuerySet):
    def base_queryset(self):
        return self.select_related(
            'currency_sum', 'currency_rate', 'manager', 'content_type')

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
        from partnership.models import Deal, ChurchDeal
        if not is_authenticated(user):
            return self.none()
        deal_ids = Deal.objects.for_user(user).values_list('id', flat=True)
        church_deal_ids = ChurchDeal.objects.for_user(user).values_list('id', flat=True)

        return self.filter(
            (Q(content_type__model='deal') & Q(object_id__in=deal_ids)) |
            (Q(content_type__model='churchdeal') & Q(object_id__in=church_deal_ids))
        )

    def for_user_by_summit_anket(self, user):
        from summit.models import SummitAnket
        if not is_authenticated(user):
            return self.none()
        anket_ids = SummitAnket.objects.for_user(user).values_list('id', flat=True)

        return self.filter(
            (Q(content_type__model='summitanket') & Q(object_id__in=anket_ids))
        )

    def for_user_by_church_report(self, user):
        from event.models import ChurchReport
        if not is_authenticated(user):
            return self.none()
        church_report_ids = ChurchReport.objects.for_user(user).values_list('id', flat=True)

        return self.filter(
            (Q(content_type__model='churchreport') & Q(object_id__in=church_report_ids))
        )


    """
        CONCAT(auth_user.last_name, ' ', auth_user.first_name, ' ', account_customuser.middle_name) as purpose_fio,
        partnership_deal.date_created as purpose_date,
        CONCAT(au2.last_name, ' ', au2.first_name, ' ', a2.middle_name) as purpose_manager_fio
    """

    def add_deal_fio(self):
        return self.extra(
            select={
                'purpose_fio': '''
                    SELECT
                    CONCAT(auth_user.last_name, ' ', auth_user.first_name, ' ', account_customuser.middle_name)
                    as purpose_fio
                    FROM partnership_deal

                    JOIN partnership_partnership ON partnership_deal.partnership_id = partnership_partnership.id
                    JOIN account_customuser ON partnership_partnership.user_id = account_customuser.user_ptr_id
                    JOIN auth_user ON account_customuser.user_ptr_id = auth_user.id

                    WHERE partnership_deal.id = payment_payment.object_id and payment_payment.content_type_id = 40
                    UNION ALL
                    SELECT
                    group_church.title as purpose_fio
                    FROM partnership_churchdeal

                    JOIN partnership_churchpartner ON partnership_churchdeal.partnership_id = partnership_churchpartner.id
                    JOIN group_church ON partnership_churchpartner.church_id = group_church.id

                    WHERE partnership_churchdeal.id = payment_payment.object_id and payment_payment.content_type_id = 101
                    '''
            }).extra(
            select={
                'purpose_date': '''
                    SELECT
                    partnership_deal.date_created as purpose_date
                    FROM partnership_deal

                    WHERE partnership_deal.id = payment_payment.object_id and payment_payment.content_type_id = 40
                    UNION ALL
                    SELECT
                    partnership_churchdeal.date_created as purpose_date
                    FROM partnership_churchdeal

                    WHERE partnership_churchdeal.id = payment_payment.object_id and payment_payment.content_type_id = 101
                    '''
            }).extra(
            select={
                'purpose_manager_fio': '''
                    SELECT
                    CONCAT(au2.last_name, ' ', au2.first_name, ' ', a2.middle_name) as purpose_manager_fio
                    FROM partnership_deal

                    JOIN account_customuser a2 on partnership_deal.responsible_id = a2.user_ptr_id
                    JOIN auth_user au2 ON a2.user_ptr_id = au2.id

                    WHERE partnership_deal.id = payment_payment.object_id and payment_payment.content_type_id = 40
                    UNION ALL
                    SELECT
                    CONCAT(au2.last_name, ' ', au2.first_name, ' ', a2.middle_name) as purpose_manager_fio
                    FROM partnership_churchdeal

                    JOIN account_customuser a2 on partnership_churchdeal.responsible_id = a2.user_ptr_id
                    JOIN auth_user au2 ON a2.user_ptr_id = au2.id

                    WHERE partnership_churchdeal.id = payment_payment.object_id and payment_payment.content_type_id = 101
                    '''
            }).extra(
            select={
                'purpose_type': '''
                    SELECT
                    partnership_deal.type as purpose_type
                    FROM partnership_deal

                    WHERE partnership_deal.id = payment_payment.object_id and payment_payment.content_type_id = 40
                    UNION ALL
                    SELECT
                    partnership_churchdeal.type as purpose_type
                    FROM partnership_churchdeal

                    WHERE partnership_churchdeal.id = payment_payment.object_id and payment_payment.content_type_id = 101
                    '''
            }).extra(
            select={
                'purpose_id': '''
                    SELECT
                    partnership_partnership.user_id as purpose_id
                    FROM partnership_deal

                    JOIN partnership_partnership ON partnership_deal.partnership_id = partnership_partnership.id

                    WHERE partnership_deal.id = payment_payment.object_id and payment_payment.content_type_id = 40
                    UNION ALL
                    SELECT
                    partnership_churchpartner.church_id as purpose_id
                    FROM partnership_churchdeal

                    JOIN partnership_churchpartner ON partnership_churchdeal.partnership_id = partnership_churchpartner.id

                    WHERE partnership_churchdeal.id = payment_payment.object_id and payment_payment.content_type_id = 101
                    '''
            })

    def annotate_manager_name(self):
        return self.annotate(
            manager_name=Concat(
                'manager__last_name', V(' '),
                'manager__first_name', V(' '),
                'manager__middle_name'))

    def add_church_report_info(self):
        return self.annotate(
            church_title=F('church_reports__church__title'),
            church_id=F('church_reports__church'),
            report_date=F('church_reports__date'),
            pastor_fio=Concat(
                F('church_reports__pastor__last_name'), V(' '),
                F('church_reports__pastor__first_name'), V(' '),
                F('church_reports__pastor__middle_name')),
            pastor_id=F('church_reports__pastor')
        )


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

    def for_user_by_church_report(self, user):
        return self.get_queryset().for_user_by_church_report(user=user)

    def add_deal_fio(self):
        return self.get_queryset().add_deal_fio()

    def annotate_manager_name(self):
        return self.get_queryset().annotate_manager_name()
