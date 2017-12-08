import operator
from datetime import datetime, date, timedelta

import django_filters
from django import forms
from django.db import models
from django.db.models import Q
from django.utils import six
from django_filters import rest_framework, STRICTNESS
from rest_framework.filters import BaseFilterBackend

from event.models import ChurchReport
from partnership.models import Deal, ChurchDeal
from payment.models import Payment

if six.PY3:
    from functools import reduce


class PaymentFilterByPurpose(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        purpose = request.query_params.getlist('purpose', None)
        if not purpose:
            return queryset
        return queryset.filter(content_type__model__in=purpose)


class PaymentFilter(rest_framework.FilterSet):
    sum_to = django_filters.NumberFilter(name="sum", lookup_expr='lte')
    sum_from = django_filters.NumberFilter(name="sum", lookup_expr='gte')
    eff_sum_to = django_filters.NumberFilter(name="effective_sum", lookup_expr='lte')
    eff_sum_from = django_filters.NumberFilter(name="effective_sum", lookup_expr='gte')
    create_to = django_filters.DateFilter(name="created_at", lookup_expr='lte')
    create_from = django_filters.DateFilter(name="created_at", lookup_expr='gte')
    sent_to = django_filters.DateFilter(name="sent_date", lookup_expr='lte')
    sent_from = django_filters.DateFilter(name="sent_date", lookup_expr='gte')

    class Meta:
        model = Payment
        fields = ['sum_from', 'sum_to', 'eff_sum_from', 'eff_sum_to', 'currency_sum',
                  'currency_rate', 'create_from', 'create_to', 'sent_from', 'sent_to', 'manager']

    # TODO its hell
    @property
    def qs(self):
        if not hasattr(self, '_qs'):
            if not self.is_bound:
                self._qs = self.queryset.all()
                return self._qs

            if not self.form.is_valid():
                if self.strict == STRICTNESS.RAISE_VALIDATION_ERROR:
                    raise forms.ValidationError(self.form.errors)
                elif self.strict == STRICTNESS.RETURN_NO_RESULTS:
                    self._qs = self.queryset.none()
                    return self._qs
                    # else STRICTNESS.IGNORE...  ignoring

            # start with all the results and filter from there
            qs = self.queryset.all()
            for name, filter_ in six.iteritems(self.filters):
                value = self.form.cleaned_data.get(name)

                if value is not None:  # valid & clean data
                    if name == 'create_to':
                        value = value + timedelta(days=1)
                    qs = filter_.filter(qs, value)

            self._qs = qs

        return self._qs


class FilterByDealFIO(BaseFilterBackend):
    include_self_master = False

    user_orm_lookups = ['partnership__user__first_name__icontains',
                        'partnership__user__last_name__icontains',
                        'partnership__user__middle_name__icontains',
                        'partnership__user__search_name__icontains'
                        ]

    church_orm_lookups = ['partnership__church__title__icontains']

    def get_user_deals(self, request):
        return Deal.objects.for_user(request.user)

    def get_church_deals(self, request):
        return ChurchDeal.objects.for_user(request.user)

    def get_user_deal_ids(self, request):
        purpose_fio = request.query_params.get('search_purpose_fio', None)
        orm_lookups = self.user_orm_lookups

        deals = self.get_user_deals(request)
        for search_term in purpose_fio.replace(',', ' ').split():
            queries = [
                models.Q(**{orm_lookup: search_term})
                for orm_lookup in orm_lookups]
            deals = deals.filter(reduce(operator.or_, queries))

        return deals.values_list('id', flat=True)

    def get_church_deal_ids(self, request):
        purpose_fio = request.query_params.get('search_purpose_fio', None)
        orm_lookups = self.church_orm_lookups

        deals = self.get_church_deals(request)
        for search_term in purpose_fio.replace(',', ' ').split():
            queries = [
                models.Q(**{orm_lookup: search_term})
                for orm_lookup in orm_lookups]
            deals = deals.filter(reduce(operator.or_, queries))

        return deals.values_list('id', flat=True)

    def filter_queryset(self, request, queryset, view):
        purpose_fio = request.query_params.get('search_purpose_fio', None)
        if not purpose_fio:
            return queryset
        user_deal_ids = self.get_user_deal_ids(request)
        church_deal_ids = self.get_church_deal_ids(request)

        return queryset.filter(
            Q(content_type__model='deal') & Q(object_id__in=user_deal_ids) |
            Q(content_type__model='churchdeal') & Q(object_id__in=church_deal_ids)
        )


class FilterByDealDate(BaseFilterBackend):
    include_self_master = False

    def get_user_deals(self, request):
        return Deal.objects.for_user(request.user)

    def get_church_deals(self, request):
        return ChurchDeal.objects.for_user(request.user)

    def filter_queryset(self, request, queryset, view):
        date_from = request.query_params.get('purpose_date_from', None)
        date_to = request.query_params.get('purpose_date_to', None)
        if not (date_from or date_to):
            return queryset
        date_from = datetime.strptime(date_from, "%Y-%m-%d") if date_from else None
        date_from = date(date_from.year, date_from.month, 1) if date_from else None
        date_to = datetime.strptime(date_to, "%Y-%m-%d") if date_to else None
        last_day = 31
        while date_to is not None:
            try:
                date_to = date(date_to.year, date_to.month, last_day) if date_to else None
            except ValueError:
                last_day -= 1
            else:
                break

        user_deals = self.get_user_deals(request)
        if date_from and date_to:
            user_deals = user_deals.filter(date_created__range=(date_from, date_to))
        elif date_from:
            user_deals = user_deals.filter(date_created__gte=date_from)
        elif date_to:
            user_deals = user_deals.filter(date_created__lte=date_to)

        user_deal_ids = user_deals.values_list('id', flat=True)

        church_deals = self.get_church_deals(request)
        if date_from and date_to:
            church_deals = church_deals.filter(date_created__range=(date_from, date_to))
        elif date_from:
            church_deals = church_deals.filter(date_created__gte=date_from)
        elif date_to:
            church_deals = church_deals.filter(date_created__lte=date_to)

        church_deal_ids = church_deals.values_list('id', flat=True)

        return queryset.filter(
            Q(content_type__model='deal') & Q(object_id__in=user_deal_ids) |
            Q(content_type__model='churchdeal') & Q(object_id__in=church_deal_ids)
        )


# class FilterByDealManagerFIO(BaseFilterBackend):
#     include_self_master = False
#
#     def get_deals(self, request):
#         return Deal.objects.for_user(request.user)
#
#     def filter_queryset(self, request, queryset, view):
#         manager_fio = request.query_params.get('search_purpose_manager_fio', None)
#         if not manager_fio:
#             return queryset
#
#         orm_lookups = [
#             'responsible__first_name__icontains',
#             'responsible__last_name__icontains',
#             'responsible__middle_name__icontains',
#             'responsible__search_name__icontains']
#
#         deals = self.get_deals(request)
#         for search_term in manager_fio.replace(',', ' ').split():
#             queries = [
#                 models.Q(**{orm_lookup: search_term})
#                 for orm_lookup in orm_lookups]
#             deals = deals.filter(reduce(operator.or_, queries))
#
#         deal_ids = deals.values_list('id', flat=True)
#
#         return queryset.filter(content_type__model='deal', object_id__in=deal_ids)


class FilterByDealManager(BaseFilterBackend):
    def get_user_deals(self, request):
        return Deal.objects.for_user(request.user)

    def get_church_deals(self, request):
        return ChurchDeal.objects.for_user(request.user)

    def filter_queryset(self, request, queryset, view):
        responsible_id = request.query_params.get('responsible_id')
        if not responsible_id:
            return queryset

        user_deals = self.get_user_deals(request).filter(responsible_id=responsible_id)
        user_deal_ids = user_deals.values_list('id', flat=True)

        church_deals = self.get_church_deals(request).filter(responsible_id=responsible_id)
        church_deal_ids = church_deals.values_list('id', flat=True)

        return queryset.filter(
            Q(content_type__model='deal') & Q(object_id__in=user_deal_ids) |
            Q(content_type__model='churchdeal') & Q(object_id__in=church_deal_ids)
        )


class FilterByDealType(BaseFilterBackend):
    def get_user_deals(self, request):
        return Deal.objects.for_user(request.user)

    def get_church_deals(self, request):
        return ChurchDeal.objects.for_user(request.user)

    def filter_queryset(self, request, queryset, view):
        deal_type = request.query_params.get('deal_type')
        if deal_type not in ['1', '2']:
            return queryset

        user_deals = self.get_user_deals(request).filter(type=deal_type)
        user_deal_ids = user_deals.values_list('id', flat=True)

        church_deals = self.get_church_deals(request).filter(type=deal_type)
        church_deal_ids = church_deals.values_list('id', flat=True)

        return queryset.filter(
            Q(content_type__model='deal') & Q(object_id__in=user_deal_ids) |
            Q(content_type__model='churchdeal') & Q(object_id__in=church_deal_ids)
        )


class FilterByChurchReportPastor(BaseFilterBackend):
    @staticmethod
    def get_reports(request):
        return ChurchReport.objects.for_user(request.user)

    def filter_queryset(self, request, queryset, view):
        pastor_id = request.query_params.get('pastor_id')
        if not pastor_id:
            return queryset

        reports = self.get_reports(request).filter(pastor_id=pastor_id)
        reports_ids = reports.values_list('id', flat=True)

        return queryset.filter(content_type__model='churchreport', object_id__in=reports_ids)


class FilterByChurchReportDate(BaseFilterBackend):
    @staticmethod
    def get_reports(request):
        return ChurchReport.objects.for_user(request.user)

    def filter_queryset(self, request, queryset, view):
        date_from = request.query_params.get('report_date_from', None)
        date_to = request.query_params.get('report_date_to', None)
        if not (date_from or date_to):
            return queryset

        reports = self.get_reports(request).filter(date__range=[date_from, date_to])
        report_ids = reports.values_list('id', flat=True)

        return queryset.filter(content_type__model='churchreport', object_id__in=report_ids)


class FilterByChurchReportChurchTitle(BaseFilterBackend):
    @staticmethod
    def get_reports(request):
        return ChurchReport.objects.for_user(request.user)

    def filter_queryset(self, request, queryset, view):
        church_id = request.query_params.get('church_id')
        if not church_id:
            return queryset

        reports = self.get_reports(request).filter(pastor_id=church_id)
        reports_ids = reports.values_list('id', flat=True)

        return queryset.filter(content_type__model='churchreport', object_id__in=reports_ids)
