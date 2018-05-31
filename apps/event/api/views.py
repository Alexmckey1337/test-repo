import calendar
import json
import logging
from collections import defaultdict, OrderedDict
from copy import deepcopy
from datetime import datetime
from decimal import Decimal
from functools import reduce
from itertools import chain
from operator import or_
from typing import NamedTuple, List, Dict, Iterable, Tuple

import pytz
from django.contrib.contenttypes.models import ContentType
from django.db import transaction, IntegrityError, connection, DataError
from django.db.models import (IntegerField, Sum, When, Case, Count, OuterRef, Exists, Q,
                              BooleanField, F)
from django.http import QueryDict
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django_filters import rest_framework
from rest_framework import status, exceptions, views
from rest_framework.decorators import action, api_view
from rest_framework.parsers import JSONParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.account.models import CustomUser
from apps.event.api.filters import (
    ChurchReportFilter, MeetingFilter, MeetingCustomFilter, MeetingFilterByMaster,
    ChurchReportDepartmentFilter, ChurchReportFilterByMaster, EventSummaryFilter,
    EventSummaryMasterFilter, ChurchReportPaymentStatusFilter, MeetingStatusFilter,
    ChurchReportStatusFilter, CommonGroupsLast5Filter, MeetingsTypeMultipleFilter)
from apps.event.api.mixins import EventUserTreeMixin
from apps.event.api.pagination import (
    MeetingPagination, MeetingVisitorsPagination, ChurchReportPagination,
    MeetingSummaryPagination, ReportsSummaryPagination)
from apps.event.api.serializers import (
    MeetingVisitorsSerializer, MeetingSerializer, MeetingDetailSerializer,
    MeetingListSerializer, ChurchReportStatisticSerializer,
    MeetingStatisticSerializer, ChurchReportSerializer,
    ChurchReportListSerializer, MeetingDashboardSerializer,
    ChurchReportDetailSerializer, ChurchReportsDashboardSerializer,
    MeetingSummarySerializer, ChurchReportSummarySerializer, MobileReportsDashboardSerializer)
from apps.event.models import Meeting, ChurchReport, MeetingAttend
from apps.payment.api.views_mixins import CreatePaymentMixin, ListPaymentMixin
from apps.payment.models import Payment, Currency
from common.filters import FieldSearchFilter, OrderingFilterWithPk
from common.parsers import MultiPartAndJsonParser
from common.utils import encode_month, decode_month

logger = logging.getLogger(__name__)

MEETINGS_SUMMARY_ORDERING_FIELDS = ('last_name', 'master__last_name', 'meetings_submitted',
                                    'meetings_expired', 'meetings_in_progress')

REPORTS_SUMMARY_ORDERING_FIELDS = ('last_name', 'master__last_name', 'reports_submitted',
                                   'reports_expired', 'reports_in_progress')

EVENT_SUMMARY_SEARCH_FIELDS = {'search_fio': ('last_name', 'first_name', 'middle_name')}

SEX_FIELDS = ('male', 'female', 'unknown')
CONGREGATION_FIELDS = ('stable', 'unstable')
CONVERT_FIELDS = CONGREGATION_FIELDS
AGE_FIELDS = ('12-', '13-25', '26-40', '41-60', '60+', 'unknown')


class Report(NamedTuple):
    code: str
    ids: List[int]
    year: int
    week: int
    count_people: int
    new_people: int
    count_repentance: int
    tithe: Decimal
    donations: Decimal
    transfer_payments: Decimal
    pastor_tithe: Decimal


class MeetingReport(NamedTuple):
    ids: List[int]
    year: int
    week: int
    code: str
    total_guest_count: int
    total_new_count: int
    total_repentance_count: int
    total_sum: Decimal


class MeetingAttendReport(NamedTuple):
    year: int
    week: int
    sex: List[int]
    congregation: List[int]
    convert: List[int]
    age: List[int]


def by_currencies(func):
    """
    Decorator for group data by currencies.

    For example:
    If:
        result = {
            'uah': [
                {'year': 2017, 'month': 1, 'week': 2, 'count': 2},
                {'year': 2017, 'month': 1, 'week': 3, 'count': 4}
            ],
            'usd': [{'year': 2017, 'month': 1, 'week': 2, 'count': 3}]
        }

        currency = 'uah'
        res = [{'year': 2017, 'month': 1, 'week': 2, 'count': 2},{'year': 2017, 'month': 1, 'week': 3, 'count': 4}]
            @by_currencies
            def group_by_month(self, res, weeks):
                return [{'year': 2017, 'month': 1, 'week': [1, 4], 'count': 6}]
        currency = 'usd', res = [{'year': 2017, 'month': 1, 'week': 2, 'count': 3}]
            @by_currencies
            def group_by_month(self, result, weeks):
                return [{'year': 2017, 'month': 1, 'week': [1, 4], 'count': 3}]

    Then `by_currencies.wrap` returning:
        {
            'uah': [{'year': 2017, 'month': 1, 'week': [1, 4], 'count': 6}],
            'usd': [{'year': 2017, 'month': 1, 'week': [1, 4], 'count': 3}]
        }

    :param func:
    :return:
    """

    def wrap(self, result, weeks):
        """

        :param self:
        :param result:
        :param weeks: {from: {year: XXXX, week: YY}, to: {year: XXXX, week: YY}}
        :return:
        """
        stats = dict()
        for currency, res in result.items():
            stats[currency] = func(self, res, weeks)
        return stats

    return wrap


def reverse_currencies(func):
    """
    Decorator for reverse dict by currency by date to dict by date[currency].

    For example:
    If:
        @reverse_currencies
        def by_currencies(*args, **kwargs):
            return {
                'uah': [{'year': 2017, 'month': 1, 'week': [1, 4], 'count': 6}],
                'usd': [{'year': 2017, 'month': 1, 'week': [1, 4], 'count': 3}]
            }

    Then `reverse_currencies.wrap` returning:
         [
            'date': {'year': 2017, 'month': 1, 'week': [1, 4]},
            'result': {
                'uah': {'count': 6},
                'usd': {'count': 3}
            }
        ]

    :param func: func
    :return: wrap
    """

    def wrap(*args, **kwargs):
        result = defaultdict(dict)
        data_by_currencies = func(*args, **kwargs)
        for currency, data in data_by_currencies.items():
            for d in data:
                result[(d.pop('year'), d.pop('month'), d.pop('week'))][currency] = d

        return [{'date': {'year': d[0], 'month': d[1], 'week': d[2]}, 'result': r} for d, r in result.items()]

    return wrap


def weeks_to_list(get_weeks):
    """
    Convert
        from format {from: {year: YYYY, week: WW}, to: {year: YYYY, week: WW}}
        to format {from: {year: YYYY, week: [from_WW, to_WW]}, to: {year: YYYY, week: [from_WW, to_WW]}}

    :param get_weeks: func
    :return:
    """

    def wrap(self):
        weeks = get_weeks(self)

        now = timezone.now()
        from_ = [weeks['from']['week'], self.get_weeks_of_year(weeks['from']['year'])[1]]
        to_ = [1, weeks['to']['week']]
        if weeks['from']['year'] == weeks['to']['year']:
            from_[1] = weeks['to']['week']
            to_[0] = weeks['from']['week']
        elif now.year == weeks['from']['year']:
            from_[1] = int(now.strftime('%W'))
        weeks['from']['week'] = from_
        weeks['to']['week'] = to_
        # logger.info(weeks)
        return weeks

    return wrap


class IntervalFormatError(Exception):
    pass


class IntervalOrderError(Exception):
    pass


class LastPeriodFormatError(Exception):
    pass


class InvalidWeekNumber(Exception):
    pass


class MeetingViewSet(ModelViewSet, EventUserTreeMixin):
    queryset = Meeting.objects.select_related('owner', 'type', 'home_group__leader')

    serializer_class = MeetingSerializer
    serializer_retrieve_class = MeetingDetailSerializer
    serializer_list_class = MeetingListSerializer

    permission_classes = (IsAuthenticated,)
    pagination_class = MeetingPagination

    filter_backends = (rest_framework.DjangoFilterBackend,
                       MeetingCustomFilter,
                       FieldSearchFilter,
                       OrderingFilterWithPk,
                       MeetingFilterByMaster,
                       MeetingStatusFilter,
                       CommonGroupsLast5Filter,
                       MeetingsTypeMultipleFilter
                       )

    filter_fields = ('data', 'type', 'owner', 'home_group', 'status', 'department', 'church')

    ordering_fields = ('id', 'date', 'owner__last_name', 'home_group__title', 'type__code',
                       'status', 'home_group__phone_number', 'visitors_attended', 'visitors_absent',
                       'total_sum',)

    filter_class = MeetingFilter

    field_search_fields = {
        'search_date': ('date',),
        'search_title': (
            'id',
            'home_group__title',
            'owner__last_name', 'owner__first_name', 'owner__middle_name',
        )
    }

    def get_serializer_class(self):
        if self.action == 'list':
            return self.serializer_list_class
        if self.action in ['retrieve', 'update', 'partial_update']:
            return self.serializer_retrieve_class
        return self.serializer_class

    def get_queryset(self):
        if self.action == 'list':
            subqs = Meeting.objects.filter(owner=OuterRef('owner'), status=Meeting.EXPIRED)
            quseyset = self.queryset.for_user(self.request.user)

            return quseyset.prefetch_related('attends').annotate_owner_name().annotate(
                visitors_attended=Sum(Case(
                    When(attends__attended=True, then=1),
                    output_field=IntegerField(), default=0)),

                visitors_absent=Sum(Case(When(
                    attends__attended=False, then=1),
                    output_field=IntegerField(), default=0))
            ).annotate(can_s=Exists(subqs)).annotate(
                can_submit=Case(
                    When(Q(status=True) & Q(can_s=True), then=True),  # then=True,
                    output_field=BooleanField(), default=True))

        return self.queryset.for_user(self.request.user)

    @action(detail=True, methods=['POST'])
    def clean_image(self, request, pk):
        meeting = self.get_object()
        if not meeting.image:
            raise exceptions.ValidationError(
                {'message': _('No image form this meeting. Nothing to clean.')})
        meeting.image = None
        meeting.save()

        return Response({'message': 'Image was successfully deleted'})

    @action(detail=True, methods=['POST'], serializer_class=MeetingDetailSerializer,
            parser_classes=(MultiPartAndJsonParser, JSONParser, FormParser))
    def submit(self, request, pk):
        home_meeting = self.get_object()
        valid_attends = self.validate_to_submit(home_meeting, request.data)

        home_meeting.status = Meeting.SUBMITTED
        meeting = self.serializer_class(home_meeting, data=request.data, partial=True)
        meeting.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                self.perform_update(meeting)
                for attend in valid_attends:
                    MeetingAttend.objects.create(
                        meeting_id=home_meeting.id,
                        user_id=attend.get('user_id'),
                        attended=attend.get('attended', False),
                        note=attend.get('note', '')
                    )
        except IntegrityError:
            data = {'detail': _('При сохранении возникла ошибка. Попробуйте еще раз.')}
            return Response(data, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        headers = self.get_success_headers(meeting.data)
        return Response({'message': _('Отчет Домашней Группы успешно подан.')},
                        status=status.HTTP_200_OK, headers=headers)

    @staticmethod
    def validate_to_submit(meeting, data):
        # if Meeting.objects.filter(owner=meeting.owner, status=Meeting.EXPIRED).exists() and \
        #                 meeting.status == Meeting.IN_PROGRESS:
        #     raise exceptions.ValidationError({
        #         'detail': _('Невозможно подать отчет. Данный лидер имеет просроченные отчеты.')
        #     })
        if isinstance(data, QueryDict):
            data._mutable = True

        if meeting.type.code == 'service' and data.get('total_sum'):
            raise exceptions.ValidationError({
                'detail': _('Невозможно подать отчет. Отчет типа - {%s} не должен содержать '
                            'денежную сумму.' % meeting.type.name)
            })

        if not data.get('attends'):
            raise exceptions.ValidationError({
                'detail': _('Невозможно подать отчет. Список присутствующих не передан.')
            })

        if meeting.status == Meeting.SUBMITTED:
            raise exceptions.ValidationError({
                'detail': _('Невозможно повторно подать отчет. Данный отчет - {%s}, '
                            'уже был подан ранее.') % meeting
            })

        attends = data.pop('attends')
        valid_visitors = list(meeting.home_group.uusers.values_list('id', flat=True))
        valid_attends = [attend for attend in json.loads(attends[0]) if attend.get('user_id') in valid_visitors]

        if not valid_attends:
            raise exceptions.ValidationError({
                'detail': _('Переданный список присутствующих некорректен.')
            })

        return valid_attends

    def update(self, request, *args, **kwargs):
        meeting = self.get_object()
        meeting = self.get_serializer(meeting, data=request.data, partial=True)
        meeting.is_valid(raise_exception=True)

        if not request.data.get('attends'):
            self.perform_update(meeting)
            return Response(meeting.data)

        data = request.data
        if isinstance(data, QueryDict):
            data._mutable = True

        attends = json.loads(data.pop('attends')[0])

        try:
            with transaction.atomic():
                self.perform_update(meeting)
                for attend in attends:
                    MeetingAttend.objects.filter(id=attend.get('id')).update(
                        user=attend.get('user_id', None),
                        attended=attend.get('attended', False),
                        note=attend.get('note', '')
                    )
        except IntegrityError as err:
            data = {'detail': _('При обновлении возникла ошибка. Попробуйте еще раз.')}
            logger.error(err)
            return Response(data, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        headers = self.get_success_headers(meeting.data)
        return Response({'message': _('Отчет Домашней Группы успешно изменен.')},
                        status=status.HTTP_200_OK, headers=headers)

    @action(detail=True, methods=['GET'], serializer_class=MeetingVisitorsSerializer,
            pagination_class=MeetingVisitorsPagination)
    def visitors(self, request, pk):
        meeting = self.get_object()
        visitors = meeting.home_group.uusers.order_by('last_name', 'first_name', 'middle_name', 'pk')

        page = self.paginate_queryset(visitors)
        if page is not None:
            visitors = self.get_serializer(page, many=True)
            return self.get_paginated_response(visitors.data)

        visitors = self.serializer_class(visitors, many=True)
        return Response(visitors.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], serializer_class=MeetingStatisticSerializer)
    def statistics(self, request):
        queryset = self.filter_queryset(self.queryset.for_user(self.request.user))

        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')

        statistics = queryset.aggregate(
            total_visitors=Count('visitors'),
            total_visits=Sum(Case(
                When(attends__attended=True, then=1),
                output_field=IntegerField(), default=0)),
            total_absent=Sum(Case(
                When(attends__attended=False, then=1),
                output_field=IntegerField(), default=0)),
        )
        statistics.update(queryset.aggregate(
            reports_in_progress=Sum(Case(
                When(status=1, then=1),
                output_field=IntegerField(), default=0)),
            reports_submitted=Sum(Case(
                When(status=2, then=1),
                output_field=IntegerField(), default=0)),
            reports_expired=Sum(Case(
                When(status=3, then=1),
                output_field=IntegerField(), default=0))))

        statistics.update(queryset.aggregate(total_donations=Sum('total_sum')))

        master_id = request.query_params.get('master_tree')
        if master_id:
            query = CustomUser.objects.for_user(user=CustomUser.objects.get(id=master_id))
        else:
            query = CustomUser.objects.for_user(self.request.user)

        statistics['new_repentance'] = query.filter(
            repentance_date__range=[from_date, to_date]).count()

        statistics = self.serializer_class(statistics)
        return Response(statistics.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], serializer_class=MeetingDashboardSerializer)
    def dashboard_counts(self, request):
        user = self.user_for_dashboard(request)
        queryset = self.queryset.for_user(user, extra_perms=False)

        dashboards_counts = queryset.aggregate(
            meetings_in_progress=Sum(Case(
                When(status=1, then=1),
                output_field=IntegerField(), default=0)),
            meetings_submitted=Sum(Case(
                When(status=2, then=1),
                output_field=IntegerField(), default=0)),
            meetings_expired=Sum(Case(
                When(status=3, then=1),
                output_field=IntegerField(), default=0))
        )

        dashboards_counts = self.serializer_class(dashboards_counts)
        return Response(dashboards_counts.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], serializer_class=MobileReportsDashboardSerializer)
    def mobile_dashboard(self, request):
        user = self.user_for_dashboard(request)
        queryset = self.queryset.for_user(user, extra_perms=False).filter(status__in=[1, 3])

        mobile_counts = queryset.aggregate(
            service=Sum(Case(
                When(type=1, then=1),
                output_field=IntegerField(), default=0)),
            home_meetings=Sum(Case(
                When(type=2, then=1),
                output_field=IntegerField(), default=0)),
            night=Sum(Case(
                When(type=3, then=1),
                output_field=IntegerField(), default=0))
        )

        mobile_counts['church_reports'] = ChurchReport.objects.for_user(
            user, extra_perms=False).filter(status__in=[1, 3]).count()

        if not mobile_counts['church_reports']:
            mobile_counts['church_reports'] = None

        mobile_counts = self.serializer_class(mobile_counts)
        return Response(mobile_counts.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], serializer_class=MeetingSummarySerializer,
            filter_backends=(OrderingFilterWithPk, EventSummaryFilter,
                             EventSummaryMasterFilter, FieldSearchFilter),
            ordering_fields=MEETINGS_SUMMARY_ORDERING_FIELDS,
            field_search_fields=EVENT_SUMMARY_SEARCH_FIELDS,
            pagination_class=MeetingSummaryPagination)
    def meetings_summary(self, request):
        user = self.master_for_summary(request)

        queryset = self.filter_queryset(CustomUser.objects.for_user(user).filter(
            home_group__leader__isnull=False).annotate(
            meetings_in_progress=Sum(Case(
                When(home_group__meeting__status=1, then=1),
                output_field=IntegerField(), default=0), distinct=True),
            meetings_submitted=Sum(Case(
                When(home_group__meeting__status=2, then=1),
                output_field=IntegerField(), default=0), distinct=True),
            meetings_expired=Sum(Case(
                When(home_group__meeting__status=3, then=1),
                output_field=IntegerField(), default=0), distinct=True)).distinct())

        page = self.paginate_queryset(queryset)
        leaders = self.serializer_class(page, many=True)
        return self.get_paginated_response(leaders.data)


class ChurchReportViewSet(ModelViewSet, CreatePaymentMixin,
                          EventUserTreeMixin, ListPaymentMixin):
    queryset = ChurchReport.objects.base_queryset().annotate_total_sum().annotate_value()

    serializer_class = ChurchReportSerializer
    serializer_list_class = ChurchReportListSerializer
    serializer_retrieve_class = ChurchReportDetailSerializer

    permission_classes = (IsAuthenticated,)
    pagination_class = ChurchReportPagination

    filter_backends = (rest_framework.DjangoFilterBackend,
                       ChurchReportFilterByMaster,
                       ChurchReportDepartmentFilter,
                       FieldSearchFilter,
                       OrderingFilterWithPk,
                       ChurchReportPaymentStatusFilter,
                       ChurchReportStatusFilter,
                       CommonGroupsLast5Filter,)

    filter_class = ChurchReportFilter

    ordering_fields = ('id', 'date', 'church__title', 'pastor__last_name', 'count_people',
                       'new_people', 'count_repentance', 'tithe', 'donations', 'pastor_tithe',
                       'currency_donations', 'transfer_payments',
                       'total_sum', 'value', 'payment_status')

    field_search_fields = {
        'search_date': ('date',),
        'search_title': (
            'id',
            'church__title',
            'pastor__last_name', 'pastor__first_name', 'pastor__middle_name',
        )
    }

    def get_queryset(self):
        return self.queryset.for_user(self.request.user).annotate(
            total_payments=Sum('payments__effective_sum')).annotate(
            payment_status=Case(
                When(Q(total_payments__lt=F('value')) & Q(total_payments__gt=0), then=1),
                When(total_payments__gte=F('value'), then=2),
                default=0, output_field=IntegerField())
        )

    def get_serializer_class(self):
        if self.action == 'list':
            return self.serializer_list_class
        if self.action == 'retrieve':
            return self.serializer_retrieve_class
        return self.serializer_class

    @action(detail=True, methods=['POST'])
    def submit(self, request, pk):
        church_report = self.get_object()
        if church_report.status == ChurchReport.SUBMITTED:
            raise exceptions.ValidationError({
                'detail': _('Невозможно подать отчет. Данный отчет уже был подан ранее.')
            })

        if ChurchReport.objects.filter(
                pastor=church_report.pastor,
                status=ChurchReport.EXPIRED).exists() and church_report.status == ChurchReport.IN_PROGRESS:
            raise exceptions.ValidationError({
                'detail': _('Невозможно подать отчет. Данный пастор имеет просроченные отчеты.')
            })

        data = request.data
        church_report.status = ChurchReport.SUBMITTED
        report = self.get_serializer(church_report, data=data, partial=True)
        report.is_valid(raise_exception=True)
        self.perform_update(report)
        headers = self.get_success_headers(report.data)

        return Response(
            {'message': _('Отчет Церкви успешно подан.')},
            status=status.HTTP_200_OK, headers=headers,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.payments.exists():
            raise exceptions.ValidationError({'message': _('Невозможно удалить отчет. '
                                                           'По данному отчету есть поданные платежи')})
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(
            {"message": _("Отчет Церкви успешно обновлен")},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=['GET'], serializer_class=ChurchReportStatisticSerializer)
    def statistics(self, request):
        user = request.query_params.get('master_tree', request.user)
        queryset = self.filter_queryset(self.queryset.for_user(user))

        statistics = queryset.aggregate(
            total_peoples=Sum('count_people'),
            total_new_peoples=Sum('new_people'),
            total_repentance=Sum('count_repentance'),
            total_tithe=Sum('tithe'),
            total_donations=Sum('donations'),
            total_transfer_payments=Sum('transfer_payments'),
            total_pastor_tithe=Sum('pastor_tithe'),
            church_reports_in_progress=Sum(Case(
                When(status=1, then=1),
                output_field=IntegerField(), default=0)),
            church_reports_submitted=Sum(Case(
                When(status=2, then=1),
                output_field=IntegerField(), default=0)),
            church_reports_expired=Sum(Case(
                When(status=3, then=1),
                output_field=IntegerField(), default=0))
        )

        statistics = self.serializer_class(statistics)
        return Response(statistics.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], serializer_class=ChurchReportsDashboardSerializer)
    def dashboard_counts(self, request):
        user = self.user_for_dashboard(request)
        queryset = self.queryset.for_user(user, extra_perms=False)

        dashboards_counts = queryset.aggregate(
            church_reports_in_progress=Sum(Case(
                When(status=1, then=1),
                output_field=IntegerField(), default=0)),
            church_reports_submitted=Sum(Case(
                When(status=2, then=1),
                output_field=IntegerField(), default=0)),
            church_reports_expired=Sum(Case(
                When(status=3, then=1),
                output_field=IntegerField(), default=0))
        )

        dashboards_counts = self.serializer_class(dashboards_counts)
        return Response(dashboards_counts.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], serializer_class=ChurchReportSummarySerializer,
            filter_backends=(OrderingFilterWithPk, EventSummaryMasterFilter,
                             EventSummaryFilter, FieldSearchFilter),
            ordering_fields=REPORTS_SUMMARY_ORDERING_FIELDS,
            field_search_fields=EVENT_SUMMARY_SEARCH_FIELDS,
            pagination_class=ReportsSummaryPagination)
    def reports_summary(self, request):
        user = self.master_for_summary(request)

        queryset = self.filter_queryset(CustomUser.objects.for_user(user).filter(
            church__pastor__isnull=False).annotate(
            reports_in_progress=Sum(Case(
                When(church__churchreport__status=1, then=1),
                output_field=IntegerField(), default=0), distinct=True),
            reports_submitted=Sum(Case(
                When(church__churchreport__status=2, then=1),
                output_field=IntegerField(), default=0), distinct=True),
            reports_expired=Sum(Case(
                When(church__churchreport__status=3, then=1),
                output_field=IntegerField(), default=0), distinct=True)).distinct()
                                        )

        page = self.paginate_queryset(queryset)
        pastors = self.serializer_class(page, many=True)
        return self.get_paginated_response(pastors.data)


class WeekMixin:
    request = None

    @staticmethod
    def strpyear(datestr: str) -> datetime:
        """
        Convert string of year to datetime object with timezone

        For example:
            self.strpyear('1928') == datetime.datetime(1928, 1, 1, 0, 0, tzinfo=<UTC>)

        :param datestr: year like as YYYY
        :return: datetime
        """
        return pytz.utc.localize(datetime.strptime(datestr, '%Y'))

    @staticmethod
    def strpmonth(datestr: str) -> datetime:
        """
        Convert string of year and month to datetime object with timezone

        For example:
            self.strpyear('192804') == datetime.datetime(1928, 4, 1, 0, 0, tzinfo=<UTC>)

        :param datestr: string of year and month in format YYYYmm
        :return: datetime
        """
        return pytz.utc.localize(datetime.strptime(datestr, '%Y%m'))

    def get_weeks_of_year(self, year: int) -> Tuple[int, int]:
        """
        Convert year to tuple (1, last_week_number)

        For example:
            self.get_weeks_of_year(1928) == (1, 52)

        :param year: year number
        :return: first week number (always 1), last week number
        """
        return 1, self.get_weeks_of_month(year, 12)[1]

    @staticmethod
    def get_weeks_of_month(year: int, month: int) -> Tuple[int, int]:
        """
        Convert month of year to tuple (first_week_number, last_week_number)

        For example:
            self.get_weeks_of_month(1928, 4) == (13, 17)

        :param year: year number
        :param month: month number
        :return: first week number, last week number
        """
        c = calendar.Calendar()
        months = [int(d.strftime('%W')) or 1 for d in c.itermonthdates(year, month)
                  if d.weekday() == 6 and d.month == month and d.year == year]
        return min(months), max(months)

    def get_range_weeks_of_month(self, year: int, month: int) -> Iterable[int]:
        """
        Convert month of year to range of its weeks

        For example:
            self.get_range_weeks_of_month(1928, 4) == range(13, 17)

        :param year: year number
        :param month: month number
        :return: range from first week number to last week number
        """
        f, t = self.get_weeks_of_month(year, month)
        return range(f, t + 1)

    def get_range_weeks_of_year(self, year) -> Iterable[int]:
        """
        Convert year to range of its weeks

        For example:
            self.get_range_weeks_of_year(1928) == range(1, 52)

        :param year: year number
        :return: range from first week number (always 1) to last week number
        """
        f, t = self.get_weeks_of_year(year)
        return range(f, t + 1)

    def week_to_month(self, year: int, week: int) -> int:
        """
        Convert week number of year to month number of year

        :param year: year number
        :param week: week number
        :return: month number
        """
        for month in range(1, 13):
            from_, to_ = self.get_weeks_of_month(year, month)
            if from_ <= week <= to_:
                return month
        raise InvalidWeekNumber()

    def months_to_weeks(self, from_: int, to_: int) -> Dict[str, Dict[str, int]]:
        """
        Convert from_ month count and to_ month count to dict
        {from: {year: XXXX, week: YY}, to: {year: XXXX, week: YY}}

        :param from_: from month count
        :param to_: to month count
        :return: dict from-to
        """
        from_year, from_month = decode_month(from_)
        to_year, to_month = decode_month(to_)
        return {
            'from': {'year': from_year, 'week': self.get_weeks_of_month(from_year, from_month)[0]},
            'to': {'year': to_year, 'week': self.get_weeks_of_month(to_year, to_month)[1]}
        }

    def years_to_weeks(self, from_: int, to_: int) -> Dict[str, Dict[str, int]]:
        """
        Convert from_ year and to_ year to dict
        {from: {year: XXXX, week: 1}, to: {year: XXXX, week: LAST}}

        :param from_: from year
        :param to_: to year
        :return: dict from-to
        """
        return {
            'from': {'year': from_, 'week': 1},
            'to': {'year': to_, 'week': self.get_weeks_of_year(to_)[1]}
        }

    def get_weeks_of_interval(self, interval: str) -> Dict[str, Dict[str, int]]:
        """
        Getting interval of weeks in format.
        {from: {year: XXXX, week: YY}, to: {year: XXXX, week: YY}}

        If the upper limit is not specified, then the last week of the current year is taken.

        For example:
            self.get_weeks_of_interval('20153-201742') == {from:{year:2015,week:3},to:{year:2017,week:42}}
            self.get_weeks_of_interval('201615') == {from:{year:2016,week:15},to:{year:2018,week:52}}

        :param interval: interval of weeks in format `YYYYWW[-YYYYWW]`, eg. `20153-201742`, `201615`
        :return:  dict from-to
        """
        fromto = interval.split('-')
        if len(fromto) == 1:
            from_year, to_year = self.strpyear(fromto[0][:4]).year, timezone.now().year
            from_week, to_week = fromto[0][4:], self.get_weeks_of_year(to_year)[1]
        elif len(fromto) == 2:
            from_year, to_year = self.strpyear(fromto[0][:4]).year, self.strpyear(fromto[1][:4]).year
            from_week, to_week = fromto[0][4:], fromto[1][4:]
        else:
            raise IntervalFormatError()
        return {
            'from': {'year': from_year, 'week': int(from_week)},
            'to': {'year': to_year, 'week': int(to_week)}
        }

    def get_months_of_interval(self, interval: str) -> Tuple[int, int]:
        """
        Getting interval of months count.

        If the upper limit is not specified, then the current month of the current year is taken.

        For example:
            self.get_months_of_interval('20158-20176') == (24188, 24210)
            self.get_months_of_interval('201611') == (24203, 24218)

        :param interval: interval of weeks in format `YYYYmm[-YYYYmm]`, eg. `20158-20176`, `201611`
        :return:  tuple of months count (YYYY1*12+mm1, YYYY2*12+mm2)
        """
        fromto = interval.split('-')
        if len(fromto) == 1:
            from_, to_ = self.strpmonth(fromto[0]), timezone.now()
        elif len(fromto) == 2:
            from_, to_ = self.strpmonth(fromto[0]), self.strpmonth(fromto[1])
        else:
            raise IntervalFormatError()
        return encode_month(from_.year, from_.month), encode_month(to_.year, to_.month)

    def get_years_of_interval(self, interval: str):
        """
        Getting interval of years.

        If the upper limit is not specified, then the current year is taken.

        For example:
            self.get_years_of_interval('2015-2017') == (2015, 2017)
            self.get_years_of_interval('2016') == (2016, 2018)

        :param interval: interval of weeks in format `YYYY[-YYYY]`, eg. `2015-2017`, `2016`
        :return:  tuple of weeks count (YYYY1*12+mm1, YYYY2*12+mm2)
        """
        fromto = interval.split('-')
        if len(fromto) == 1:
            from_, to_ = self.strpyear(fromto[0]), timezone.now()
        elif len(fromto) == 2:
            from_, to_ = self.strpyear(fromto[0]), self.strpyear(fromto[1])
        else:
            raise IntervalFormatError()
        return from_.year, to_.year

    def get_weeks_by_interval(self, interval: str) -> Dict[str, Dict[str, int]]:
        """
        Getting interval of weeks in format.
        {from: {year: XXXX, week: YY}, to: {year: XXXX, week: YY}}

        :param interval: interval of weeks in format (one of `y:YYYY[-YYYY]`, `m:YYYYmm[-YYYYmm]`, `w:YYYYWW[-YYYYWW]`)
        :return:  dict from-to
        """
        if not interval:
            return {}
        p, interval, *_ = interval.split(':')
        if p == 'm':
            from_, to_ = self.get_months_of_interval(interval)
            weeks = self.months_to_weeks(from_, to_)
        elif p == 'y':
            from_, to_ = self.get_years_of_interval(interval)
            weeks = self.years_to_weeks(from_, to_)
        elif p == 'w':
            weeks = self.get_weeks_of_interval(interval)
        else:
            raise IntervalFormatError()
        return weeks

    def get_weeks_by_last_period(self, last: str) -> Dict[str, Dict[str, int]]:
        """
        Getting interval of weeks in format.
        {from: {year: XXXX, week: YY}, to: {year: XXXX, week: YY}}

        :param last: period in format (one of `\d+y`, `\d+m`, `\d+w`)
        :return:  dict from-to
        """
        if not last:
            return {}
        if last[-1] == 'y':
            from_, to_ = timezone.now().year - int(last[:-1]) + 1, datetime.now().year
            weeks = self.years_to_weeks(from_, to_)
        elif last[-1] == 'm':
            now = timezone.now()
            current_month = encode_month(now.year, now.month)
            from_, to_ = current_month - int(last[:-1]) + 1, current_month
            weeks = self.months_to_weeks(from_, to_)
        elif last[-1] == 'w':
            now = timezone.now()
            from_year, to_year = now.year, now.year
            from_week, to_week = int(now.strftime('%W')) - int(last[:-1]) + 1, int(now.strftime('%W'))
            while from_week <= 0:
                from_year -= 1
                from_week = self.get_weeks_of_year(from_year)[1] + from_week
            weeks = {
                'from': {'year': from_year, 'week': from_week},
                'to': {'year': to_year, 'week': to_week}
            }
        else:
            raise LastPeriodFormatError()
        return weeks

    @weeks_to_list
    def get_weeks(self) -> Dict[str, Dict[str, int]]:
        """
        Getting interval of weeks from query parameters.

        Available query parameters is:
            - ?last=\d+[ymw]
            - ?interval=[ymw]:\d+
            - ?interval=[ymw]:\d+-\d+

        Default is weeks of last 3 month

        :return:  dict {from: {year: XXXX, week: YY}, to: {year: XXXX, week: YY}}
        """
        weeks = (
                self.get_weeks_by_interval(self.request.query_params.get('interval', '')) or
                self.get_weeks_by_last_period(self.request.query_params.get('last', '')) or
                self.get_weeks_by_last_period('3m')
        )
        if not weeks:
            return {}
        # logger.info(weeks)
        invalid_year = weeks['from']['year'] > weeks['to']['year']
        invalid_week = weeks['from']['year'] == weeks['to']['year'] and weeks['from']['week'] > weeks['to']['week']
        if invalid_year or invalid_week:
            raise IntervalOrderError()
        return weeks

    def group_by(self, y, m, w, aggr_by_key):
        return {
            'year': y,
            'week': w,
            'month': m,
        }

    @reverse_currencies
    @by_currencies
    def group_by_week(self, result, weeks):
        def aggr_by_key(key, func=sum, default=0):
            return func([r.get(key, default) for r in result if (r['year'] == y and r['week'] == w)] or [default])

        y = weeks['from']['year']
        for w in range(weeks['from']['week'][0], weeks['from']['week'][1] + 1):
            m = self.week_to_month(y, w)
            yield self.group_by(y, m, w, aggr_by_key)

        for y in range(weeks['from']['year'] + 1, weeks['to']['year']):
            year_weeks = self.get_weeks_of_year(y)
            for w in range(year_weeks[0], year_weeks[1] + 1):
                m = self.week_to_month(y, w)
                yield self.group_by(y, m, w, aggr_by_key)

        y = weeks['to']['year']
        if y > weeks['from']['year']:
            for w in range(weeks['to']['week'][0], weeks['to']['week'][1] + 1):
                m = self.week_to_month(y, w)
                yield self.group_by(y, m, w, aggr_by_key)

    @reverse_currencies
    @by_currencies
    def group_by_month(self, result, weeks):
        def aggr_by_key(key, func=sum, default=0):
            return func([r.get(key, default) for r in result if (r['year'] == y and r['month'] == m)] or [default])

        y = weeks['from']['year']
        months = set()
        for w in range(weeks['from']['week'][0], weeks['from']['week'][1] + 1):
            months.add(self.week_to_month(y, w))
        for m in months:
            yield self.group_by(y, m, tuple(self.get_weeks_of_month(y, m)), aggr_by_key)

        for y in range(weeks['from']['year'] + 1, weeks['to']['year']):
            year_weeks = self.get_weeks_of_year(y)
            months = set()
            for w in range(year_weeks[0], year_weeks[1] + 1):
                months.add(self.week_to_month(y, w))
            for m in months:
                yield self.group_by(y, m, tuple(self.get_weeks_of_month(y, m)), aggr_by_key)

        y = weeks['to']['year']
        if y > weeks['from']['year']:
            months = set()
            for w in range(weeks['to']['week'][0], weeks['to']['week'][1] + 1):
                months.add(self.week_to_month(y, w))
            for m in months:
                yield self.group_by(y, m, tuple(self.get_weeks_of_month(y, m)), aggr_by_key)

    @reverse_currencies
    @by_currencies
    def group_by_year(self, result, weeks):
        def aggr_by_key(key, func=sum, default=0):
            return func([r.get(key, default) for r in result if r['year'] == y] or [default])

        y = weeks['from']['year']
        yield self.group_by(y, (1, 12), tuple(self.get_weeks_of_year(y)), aggr_by_key)

        for y in range(weeks['from']['year'] + 1, weeks['to']['year']):
            yield self.group_by(y, (1, 12), tuple(self.get_weeks_of_year(y)), aggr_by_key)

        y = weeks['to']['year']
        if y > weeks['from']['year']:
            yield self.group_by(y, (1, 12), tuple(self.get_weeks_of_year(y)), aggr_by_key)


class ChurchReportStatsView(WeekMixin, views.APIView):
    SQL = """
        SELECT
          currency.code,
          array_agg(report.id) ids,
          date_part('year', report.date) _year,
          date_part('week', report.date) week,
          sum(report.count_people) count_people,
          sum(report.new_people) new_people,
          sum(report.count_repentance) count_repentance,
          sum(report.tithe) tithe,
          sum(report.donations) donations,
          sum(report.transfer_payments) transfer_payments,
          sum(report.pastor_tithe) pastor_tithe
        FROM event_churchreport report
          JOIN account_customuser customuser ON report.pastor_id = customuser.user_ptr_id
          JOIN payment_currency currency ON report.currency_id = currency.id
        {filter}
        GROUP BY date_part('year', report.date), date_part('week', report.date), currency.code
        ORDER BY date_part('year', report.date), date_part('week', report.date);
    """
    WEEKS_TEMPLATE = ("(date_part('week', report.date) BETWEEN {w1} AND {w2} AND " +
                      "date_part('year', report.date) = {year})")
    YEARS_TEMPLATE = "date_part('year', report.date) IN ({years})"

    payment_content_type = ContentType.objects.get_for_model(ChurchReport)

    def get_where_weeks(self, weeks):
        where_weeks = [
            self.WEEKS_TEMPLATE.format(
                year=weeks['from']['year'], w1=weeks['from']['week'][0], w2=weeks['from']['week'][1]),
            self.WEEKS_TEMPLATE.format(
                year=weeks['to']['year'], w1=weeks['to']['week'][0], w2=weeks['to']['week'][1])
        ]
        years = ','.join([str(y) for y in range(weeks['from']['year'] + 1, weeks['to']['year'])])
        if years:
            where_weeks += [self.YEARS_TEMPLATE.format(years=years)]
        return ('(' + ' OR '.join(where_weeks) + ')') if weeks else '', []

    def get_where_church(self):
        church = self.request.query_params.get('church')
        if not church:
            return '', []
        return " AND report.church_id = %s", [church]

    def get_where_pastor_tree(self):
        pastor_tree = self.request.query_params.get('pastor_tree')
        if not pastor_tree and self.request.user.is_staff:
            return '', []
        if not pastor_tree:
            pastor_tree = self.request.user.id
        try:
            pastor = CustomUser.objects.get(pk=pastor_tree)
        except CustomUser.DoesNotExist:
            return ' AND FALSE', []
        return " AND customuser.path like %s AND customuser.depth >= %s", [f'{pastor.path}%', pastor.depth]

    def get_where_pastor(self):
        pastor = self.request.query_params.get('pastor')
        if not pastor:
            return '', []
        return " AND report.pastor_id = %s", [pastor]

    def get_where_filter(self, weeks):
        where = list()
        where.append(self.get_where_weeks(weeks))
        where.append(self.get_where_church())
        where.append(self.get_where_pastor())
        where.append(self.get_where_pastor_tree())
        a = tuple(zip(*where))
        return ('WHERE ' + ' '.join(a[0]), list(chain(*a[1]))) if where else ('', [])

    def get_data(self, weeks: Dict[str, Dict[str, int]]) -> Dict[str, List[Dict]]:
        """
        :param weeks: {
                 'from': {'year': XXXX, 'week': YY},
                 'to': {'year': XXXX, 'week': YY},
               }
        :return:
        """
        where, params = self.get_where_filter(weeks)
        query = self.SQL.format(filter=where)
        try:
            with connection.cursor() as connect:
                connect.execute(query, params)
                reports = connect.fetchall()
                result = [Report(*r) for r in reports]
        except DataError:
            raise exceptions.ValidationError({'detail': _('Invalid filter params')})
        # logger.info(query)
        # logger.info(result)
        d = defaultdict(list)
        for r in result:
            d[r.code].append({
                'ids': set(r.ids),
                'year': int(r.year),
                'week': int(r.week),
                'month': self.week_to_month(int(r.year), int(r.week)),
                'count_people': int(r.count_people),
                'count_new_people': int(r.new_people),
                'count_repentance': int(r.count_repentance),
                'tithe': r.tithe,
                'donations': r.donations,
                'transfer_payments': r.transfer_payments,
                'pastor_tithe': r.pastor_tithe,
            })
        return d

    def group_by(self, y, m, w, aggr_by_key):
        ids = aggr_by_key('ids', lambda a: reduce(or_, a), default=set())
        return {
            # 'ids': ids,
            'payments_sum': Payment.objects.filter(
                object_id__in=ids,
                content_type=self.payment_content_type).aggregate(eff_sum=Sum('effective_sum'))['eff_sum'] or 0,
            'year': y,
            'week': w,
            'month': m,
            'count_people': aggr_by_key('count_people', max),
            'count_new_people': aggr_by_key('count_new_people'),
            'count_repentance': aggr_by_key('count_repentance'),
            'tithe': aggr_by_key('tithe'),
            'donations': aggr_by_key('donations'),
            'transfer_payments': aggr_by_key('transfer_payments'),
            'pastor_tithe': aggr_by_key('pastor_tithe'),
        }

    def get(self, request, *args, **kwargs):
        try:
            weeks = self.get_weeks()
        except IntervalFormatError:
            raise exceptions.ValidationError({'detail': _('Invalid "interval" format')})
        except IntervalOrderError:
            raise exceptions.ValidationError({'detail': _('Invalid "interval" order')})
        except LastPeriodFormatError:
            raise exceptions.ValidationError({'detail': _('Invalid "last" format')})

        result = self.get_data(weeks)

        group_by = request.query_params.get('group_by', 'week')
        if group_by == 'week':
            return Response(data=self.group_by_week(result, weeks))
        if group_by == 'month':
            return Response(data=self.group_by_month(result, weeks))
        if group_by == 'year':
            return Response(data=self.group_by_year(result, weeks))
        return Response(data=[])


class MeetingStatsView(WeekMixin, views.APIView):
    SQL = """
        SELECT
          array_agg(report.id) ids,
          date_part('year', report.date) _year,
          date_part('week', report.date) week,
          coalesce(cur.code, church.report_currency::char),
          sum(guest_count) total_guest_count,
          sum(new_count) total_new_count,
          sum(repentance_count) total_repentance_count,
          sum(total_sum) total_sum
        FROM event_meeting report
          JOIN account_customuser customuser ON report.owner_id = customuser.user_ptr_id
          LEFT JOIN group_homegroup hg ON report.home_group_id = hg.id
          LEFT JOIN group_church church ON hg.church_id = church.id
          LEFT JOIN payment_currency cur ON church.report_currency = cur.id
        {filter}
        GROUP BY date_part('year', report.date), date_part('week', report.date), coalesce(cur.code, church.report_currency::char)
        ORDER BY date_part('year', report.date), date_part('week', report.date), coalesce(cur.code, church.report_currency::char);
    """
    WEEKS_TEMPLATE = ("(date_part('week', report.date) BETWEEN {w1} AND {w2} AND " +
                      "date_part('year', report.date) = {year})")
    YEARS_TEMPLATE = "date_part('year', report.date) IN ({years})"

    def group_by(self, y, m, w, aggr_by_key):
        # ids = aggr_by_key('ids', lambda a: reduce(or_, a), default=set())
        return {
            # 'ids': ids,
            'year': y,
            'week': w,
            'month': m,
            'total_guest_count': aggr_by_key('total_guest_count'),
            'total_new_count': aggr_by_key('total_new_count'),
            'total_repentance_count': aggr_by_key('total_repentance_count'),
            'total_sum': aggr_by_key('total_sum'),
        }

    def get_where_weeks(self, weeks):
        where_weeks = [
            self.WEEKS_TEMPLATE.format(
                year=weeks['from']['year'], w1=weeks['from']['week'][0], w2=weeks['from']['week'][1]),
            self.WEEKS_TEMPLATE.format(
                year=weeks['to']['year'], w1=weeks['to']['week'][0], w2=weeks['to']['week'][1])
        ]
        years = ','.join([str(y) for y in range(weeks['from']['year'] + 1, weeks['to']['year'])])
        if years:
            where_weeks += [self.YEARS_TEMPLATE.format(years=years)]
        return ('(' + ' OR '.join(where_weeks) + ')') if weeks else '', []

    def get_where_department(self):
        department = self.request.query_params.get('department')
        if not department:
            return '', []
        return " AND church.department_id = %s", [department]

    def get_where_church(self):
        church = self.request.query_params.get('church')
        if not church:
            return '', []
        return " AND hg.church_id = %s", [church]

    def get_where_home_group(self):
        hg = self.request.query_params.get('hg')
        if not hg:
            return '', []
        return " AND report.home_group_id = %s", [hg]

    def get_where_meeting_type(self):
        meeting_type = self.request.query_params.get('meeting_type')
        if not meeting_type:
            return '', []
        return " AND report.type_id = %s", [meeting_type]

    def get_where_leader_tree(self):
        leader_tree = self.request.query_params.get('leader_tree')
        if not leader_tree and self.request.user.is_staff:
            return '', []
        if not leader_tree:
            leader_tree = self.request.user.id
        try:
            leader = CustomUser.objects.get(pk=leader_tree)
        except CustomUser.DoesNotExist:
            return ' AND FALSE', []
        return " AND customuser.path like %s AND customuser.depth >= %s", [f'{leader.path}%', leader.depth]

    def get_where_leader(self):
        leader = self.request.query_params.get('leader')
        if not leader:
            return '', []
        return " AND report.owner_id = %s", [leader]

    def get_where_filter(self, weeks):
        where = list()
        where.append(self.get_where_weeks(weeks))
        where.append(self.get_where_home_group())
        where.append(self.get_where_church())
        where.append(self.get_where_department())
        where.append(self.get_where_meeting_type())
        where.append(self.get_where_leader())
        where.append(self.get_where_leader_tree())
        a = tuple(zip(*where))
        return ('WHERE ' + ' '.join(a[0]), list(chain(*a[1]))) if where else ('', [])

    def get_data(self, weeks: Dict[str, Dict[str, int]]) -> Dict[str, List[Dict]]:
        """
        :param weeks: {
                 'from': {'year': XXXX, 'week': YY},
                 'to': {'year': XXXX, 'week': YY},
               }
        :return:
        """
        where, params = self.get_where_filter(weeks)
        query = self.SQL.format(filter=where)
        try:
            with connection.cursor() as connect:
                connect.execute(query, params)
                reports = connect.fetchall()
                result = [MeetingReport(*r) for r in reports]
        except DataError:
            raise exceptions.ValidationError({'detail': _('Invalid filter params')})
        # logger.info(query)
        # logger.info(result)
        d = defaultdict(list)
        for r in result:
            d[r.code].append({
                'ids': set(r.ids),
                'year': int(r.year),
                'week': int(r.week),
                'month': self.week_to_month(int(r.year), int(r.week)),
                'total_guest_count': r.total_guest_count,
                'total_new_count': r.total_new_count,
                'total_repentance_count': r.total_repentance_count,
                'total_sum': r.total_sum,
            })
        return d

    def get(self, request, *args, **kwargs):
        try:
            weeks = self.get_weeks()
        except IntervalFormatError:
            raise exceptions.ValidationError({'detail': _('Invalid "interval" format')})
        except IntervalOrderError:
            raise exceptions.ValidationError({'detail': _('Invalid "interval" order')})
        except LastPeriodFormatError:
            raise exceptions.ValidationError({'detail': _('Invalid "last" format')})

        result = self.get_data(weeks)
        # logger.info(result)
        # logger.info(weeks)

        group_by = request.query_params.get('group_by', 'week')
        if group_by == 'week':
            return Response(data=self.group_by_week(result, weeks))
        if group_by == 'month':
            return Response(data=self.group_by_month(result, weeks))
        if group_by == 'year':
            return Response(data=self.group_by_year(result, weeks))
        return Response(data=[])


class MeetingAttendStatsView(WeekMixin, views.APIView):
    SQL = """
        select
          date_part('year', report.date) _year,
          date_part('week', report.date) week,
          array[count(distinct user_id) FILTER (WHERE a.sex = 'male'),
          count(distinct user_id) FILTER (WHERE a.sex = 'female'),
          count(distinct user_id) FILTER (WHERE a.sex != 'female' and a.sex != 'male')] sex,
          array[count(distinct user_id) FILTER (WHERE h3.code = 'congregation' and a.is_stable),
          count(distinct user_id) FILTER (WHERE h3.code = 'congregation' and not a.is_stable)] congregation,
          array[count(distinct user_id) FILTER (WHERE h3.code = 'convert' and a.is_stable),
          count(distinct user_id) FILTER (WHERE h3.code = 'convert' and not a.is_stable)] convert,
          array[count(distinct user_id) FILTER (WHERE age(report.date, a.born_date) < '13 year'),
          count(distinct user_id) FILTER (WHERE age(report.date, a.born_date) between '13 year' and '26 year'),
          count(distinct user_id) FILTER (WHERE age(report.date, a.born_date) between '26 year' and '41 year'),
          count(distinct user_id) FILTER (WHERE age(report.date, a.born_date) between '41 year' and '61 year'),
          count(distinct user_id) FILTER (WHERE age(report.date, a.born_date) >= '61 year'),
          count(distinct user_id) FILTER (WHERE a.born_date is null)] age
        from event_meetingattend e
          join account_customuser a on e.user_id = a.user_ptr_id
          join hierarchy_hierarchy h3 on a.hierarchy_id = h3.id
          join event_meeting report on e.meeting_id = report.id
          join group_homegroup hg on report.home_group_id = hg.id
          join group_church church on hg.church_id = church.id
          {filter} AND report.status = 2
        GROUP BY date_part('year', report.date), date_part('week', report.date)
        ORDER BY date_part('year', report.date), date_part('week', report.date);
    """
    WEEKS_TEMPLATE = ("(date_part('week', report.date) BETWEEN {w1} AND {w2} AND " +
                      "date_part('year', report.date) = {year})")
    YEARS_TEMPLATE = "date_part('year', report.date) IN ({years})"

    def group_by(self, y, m, w, aggr_by_key):
        def sum_lists(length):
            def f(a):
                return [sum(b) for b in zip(*a)]

            return {
                'func': f,
                'default': [0] * length
            }

        return {
            'sex': aggr_by_key('sex', **sum_lists(3)),
            'congregation': aggr_by_key('congregation', **sum_lists(2)),
            'convert': aggr_by_key('convert', **sum_lists(2)),
            'age': aggr_by_key('age', **sum_lists(6)),
            'year': y,
            'week': w,
            'month': m,
        }

    def get_where_weeks(self, weeks):
        where_weeks = [
            self.WEEKS_TEMPLATE.format(
                year=weeks['from']['year'], w1=weeks['from']['week'][0], w2=weeks['from']['week'][1]),
            self.WEEKS_TEMPLATE.format(
                year=weeks['to']['year'], w1=weeks['to']['week'][0], w2=weeks['to']['week'][1])
        ]
        years = ','.join([str(y) for y in range(weeks['from']['year'] + 1, weeks['to']['year'])])
        if years:
            where_weeks += [self.YEARS_TEMPLATE.format(years=years)]
        return ('(' + ' OR '.join(where_weeks) + ')') if weeks else '', []

    def get_where_department(self):
        department = self.request.query_params.get('department')
        if not department:
            return '', []
        return " AND church.department_id = %s", [department]

    def get_where_attended(self):
        attended = self.request.query_params.get('attended', '')
        if attended.lower() in ('true', 't', '1'):
            return " AND e.attended", []
        if attended.lower() in ('false', 'f', '0'):
            return " AND not e.attended", []
        return '', []

    def get_where_church(self):
        church = self.request.query_params.get('church')
        if not church:
            return '', []
        return " AND hg.church_id = %s", [church]

    def get_where_home_group(self):
        hg = self.request.query_params.get('hg')
        if not hg:
            return '', []
        return " AND report.home_group_id = %s", [hg]

    def get_where_meeting_type(self):
        meeting_type = self.request.query_params.get('meeting_type')
        if not meeting_type:
            return '', []
        return " AND report.type_id = %s", [meeting_type]

    def get_where_leader_tree(self):
        leader_tree = self.request.query_params.get('leader_tree')
        if not leader_tree and self.request.user.is_staff:
            return '', []
        if not leader_tree:
            leader_tree = self.request.user.id
        try:
            leader = CustomUser.objects.get(pk=leader_tree)
        except CustomUser.DoesNotExist:
            return ' AND FALSE', []
        return " AND a.path like %s AND a.depth >= %s", [f'{leader.path}%', leader.depth]

    def get_where_leader(self):
        leader = self.request.query_params.get('leader')
        if not leader:
            return '', []
        return " AND report.owner_id = %s", [leader]

    def get_where_filter(self, weeks):
        where = [self.get_where_weeks(weeks), (' AND report.status = %s ', [str(Meeting.SUBMITTED)]),
                 self.get_where_home_group(), self.get_where_church(), self.get_where_department(),
                 self.get_where_attended(), self.get_where_meeting_type(), self.get_where_leader(),
                 self.get_where_leader_tree()]
        a = tuple(zip(*where))
        return ('WHERE ' + ' '.join(a[0]), list(chain(*a[1]))) if where else ('', [])

    def get_data(self, weeks: Dict[str, Dict[str, int]]) -> Dict[str, List[Dict]]:
        """
        :param weeks: {
                 'from': {'year': XXXX, 'week': YY},
                 'to': {'year': XXXX, 'week': YY},
               }
        :return:
        """
        where, params = self.get_where_filter(weeks)
        query = self.SQL.format(filter=where)
        # logger.info(query)
        # logger.info(params)
        try:
            with connection.cursor() as connect:
                connect.execute(query, params)
                reports = connect.fetchall()
                result = [MeetingAttendReport(*r) for r in reports]
        except DataError:
            raise exceptions.ValidationError({'detail': _('Invalid filter params')})
        # logger.warning(result)
        d = defaultdict(list)
        for r in result:
            d['res'].append({
                'year': int(r.year),
                'week': int(r.week),
                'month': self.week_to_month(int(r.year), int(r.week)),
                'sex': r.sex,
                'congregation': r.congregation,
                'convert': r.convert,
                'age': r.age,
            })
        return d or {'res': []}

    def get(self, request, *args, **kwargs):
        try:
            weeks = self.get_weeks()
        except IntervalFormatError:
            raise exceptions.ValidationError({'detail': _('Invalid "interval" format')})
        except IntervalOrderError:
            raise exceptions.ValidationError({'detail': _('Invalid "interval" order')})
        except LastPeriodFormatError:
            raise exceptions.ValidationError({'detail': _('Invalid "last" format')})

        result = self.get_data(weeks)
        # logger.info(result)
        # logger.info(weeks)

        group_by = request.query_params.get('group_by', 'week')
        data = {
            'week': lambda: self.group_by_week(result, weeks),
            'month': lambda: self.group_by_month(result, weeks),
            'year': lambda: self.group_by_year(result, weeks),
        }.get(group_by, lambda: self.group_by_week(result, weeks))()

        return Response(data=[
            {
                'date': d['date'],
                'result': {
                    'sex': dict(zip(SEX_FIELDS, d['result']['res']['sex'])),
                    'congregation': dict(zip(CONGREGATION_FIELDS, d['result']['res']['congregation'])),
                    'convert': dict(zip(CONVERT_FIELDS, d['result']['res']['convert'])),
                    'age': dict(zip(AGE_FIELDS, d['result']['res']['age'])),
                }
            }
            for d in data
        ])


def create_empty_dict_by_keys(keys):
    return {k: 0 for k in keys}


attends_empty = {
    "sex": create_empty_dict_by_keys(SEX_FIELDS),
    "congregation": create_empty_dict_by_keys(CONGREGATION_FIELDS),
    "convert": create_empty_dict_by_keys(CONVERT_FIELDS),
    "age": create_empty_dict_by_keys(AGE_FIELDS),
}

meeting_empty = {c.code: {
    'total_sum': Decimal('0.00'),
    'total_guest_count': 0,
    'total_new_count': 0,
    'total_repentance_count': 0,
} for c in Currency.objects.all()}


def merge_data(meetings_stats, attends_stats):
    def dict_to_tuple(d):
        return d['year'], d['month'], d['week']

    meeting_dates = list()
    attends_dates = list()
    aa = OrderedDict()
    mm = OrderedDict()

    for a in attends_stats:
        d = dict_to_tuple(a['date'])
        attends_dates.append(d)
        aa[d] = a['result']
    for m in meetings_stats:
        d = dict_to_tuple(m['date'])
        meeting_dates.append(d)
        mm[dict_to_tuple(m['date'])] = m['result']

    dates = sorted(list(set(meeting_dates) | set(attends_dates)))

    result = list()
    for d in dates:
        attends_result = aa.get(d, attends_empty)
        meeting_result = mm.get(d, deepcopy(meeting_empty))
        attends_result['guest_count'] = sum([g.pop('total_guest_count', 0) for g in meeting_result.values()])
        attends_result['new_count'] = sum([g.pop('total_new_count', 0) for g in meeting_result.values()])
        attends_result['repentance_count'] = sum([g.pop('total_repentance_count', 0) for g in meeting_result.values()])
        money = {k: {'total_sum': v['total_sum']} for k, v in meeting_empty.items()}
        money.update(meeting_result)
        attends_result['money'] = money
        result.append({
            'date': {'year': d[0], 'month': d[1], 'week': d[2]},
            'result': attends_result,
        })

    return result


@api_view(['GET'])
def all_stats(request, *args, **kwargs):
    r1 = MeetingStatsView.as_view()(request._request, *args, **kwargs)
    r2 = MeetingAttendStatsView.as_view()(request._request, *args, **kwargs)

    data = merge_data(r1.data, r2.data)

    return Response(data=data)
