# -*- coding: utf-8
from __future__ import unicode_literals

import calendar
import json
import logging
from datetime import datetime

from django.db import transaction, IntegrityError, connection
from django.db.models import (IntegerField, Sum, When, Case, Count, OuterRef, Exists, Q,
                              BooleanField, F)
from django.utils.translation import ugettext_lazy as _
from django_filters import rest_framework
from rest_framework import status, filters, exceptions, views
from rest_framework.decorators import list_route, detail_route
from rest_framework.parsers import JSONParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.account.models import CustomUser
from apps.event.api.filters import (
    ChurchReportFilter, MeetingFilter, MeetingCustomFilter, MeetingFilterByMaster,
    ChurchReportDepartmentFilter, ChurchReportFilterByMaster, EventSummaryFilter,
    EventSummaryMasterFilter, ChurchReportPaymentStatusFilter, MeetingStatusFilter, ChurchReportStatusFilter)
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
from common.filters import FieldSearchFilter
from common.parsers import MultiPartAndJsonParser

logger = logging.getLogger(__name__)

MEETINGS_SUMMARY_ORDERING_FIELDS = ('last_name', 'master__last_name', 'meetings_submitted',
                                    'meetings_expired', 'meetings_in_progress')

REPORTS_SUMMARY_ORDERING_FIELDS = ('last_name', 'master__last_name', 'reports_submitted',
                                   'reports_expired', 'reports_in_progress')

EVENT_SUMMARY_SEARCH_FIELDS = {'search_fio': ('last_name', 'first_name', 'middle_name')}


class IntervalFormatError(Exception):
    pass


class IntervalOrderError(Exception):
    pass


class LastPeriodFormatError(Exception):
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
                       filters.OrderingFilter,
                       MeetingFilterByMaster,
                       MeetingStatusFilter)

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
                    When(Q(status=True) & Q(can_s=True), then=False),
                    output_field=BooleanField(), default=True))

        return self.queryset.for_user(self.request.user)

    @detail_route(methods=['POST'])
    def clean_image(self, request, pk):
        meeting = self.get_object()
        if not meeting.image:
            raise exceptions.ValidationError(
                {'message': _('No image form this meeting. Nothing to clean.')})
        meeting.image = None
        meeting.save()

        return Response({'message': 'Image was successfully deleted'})

    @detail_route(methods=['POST'], serializer_class=MeetingDetailSerializer,
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
        if Meeting.objects.filter(owner=meeting.owner, status=Meeting.EXPIRED).exists() and \
                        meeting.status == Meeting.IN_PROGRESS:
            raise exceptions.ValidationError({
                'detail': _('Невозможно подать отчет. Данный лидер имеет просроченные отчеты.')
            })
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

    @detail_route(methods=['GET'], serializer_class=MeetingVisitorsSerializer,
                  pagination_class=MeetingVisitorsPagination)
    def visitors(self, request, pk):
        meeting = self.get_object()
        visitors = meeting.home_group.uusers.all()

        page = self.paginate_queryset(visitors)
        if page is not None:
            visitors = self.get_serializer(page, many=True)
            return self.get_paginated_response(visitors.data)

        visitors = self.serializer_class(visitors, many=True)
        return Response(visitors.data, status=status.HTTP_200_OK)

    @list_route(methods=['GET'], serializer_class=MeetingStatisticSerializer)
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

    @list_route(methods=['GET'], serializer_class=MeetingDashboardSerializer)
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

    @list_route(methods=['GET'], serializer_class=MobileReportsDashboardSerializer)
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

    @list_route(methods=['GET'], serializer_class=MeetingSummarySerializer,
                filter_backends=(filters.OrderingFilter, EventSummaryFilter,
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
                       filters.OrderingFilter,
                       ChurchReportPaymentStatusFilter,
                       ChurchReportStatusFilter,)

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

    @detail_route(methods=['POST'])
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

    @list_route(methods=['GET'], serializer_class=ChurchReportStatisticSerializer)
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

    @list_route(methods=['GET'], serializer_class=ChurchReportsDashboardSerializer)
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

    @list_route(methods=['GET'], serializer_class=ChurchReportSummarySerializer,
                filter_backends=(filters.OrderingFilter, EventSummaryMasterFilter,
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


class ChurchReportStatsView(views.APIView):
    SQL = """
        SELECT
          date_part('year', r.date) _year,
          date_part('week', r.date) week,
          sum(r.count_people) count_people,
          sum(r.new_people) new_people,
          sum(r.count_repentance) count_repentance,
          sum(r.tithe) tithe,
          sum(r.donations) donations,
          sum(r.transfer_payments) transfer_payments,
          sum(r.pastor_tithe) pastor_tithe
        FROM event_churchreport r
          JOIN account_customuser a ON r.pastor_id = a.user_ptr_id
        {filter}
        GROUP BY date_part('year', r.date), date_part('week', r.date)
        ORDER BY date_part('year', r.date), date_part('week', r.date);
    """
    WEEKS_TEMPLATE = "(date_part('week', r.date) BETWEEN {w1} AND {w2} AND date_part('year', r.date) = {year})"
    YEARS_TEMPLATE = "date_part('year', r.date) IN ({years})"

    @staticmethod
    def strpyear(datestr):
        return datetime.strptime(datestr, '%Y')

    @staticmethod
    def strpmonth(datestr):
        return datetime.strptime(datestr, '%Y%m')

    @staticmethod
    def get_weeks_of_month(year, month):
        c = calendar.Calendar()
        months = [int(d.strftime('%W')) or 1 for d in c.itermonthdates(year, month)
                  if d.weekday() == 6 and d.month == month and d.year == year]
        return min(months), max(months)

    def get_range_weeks_of_month(self, year, month):
        f, t = self.get_weeks_of_month(year, month)
        return range(f, t + 1)

    def get_weeks_of_year(self, year):
        return 1, self.get_weeks_of_month(year, 12)[1]

    def get_range_weeks_of_year(self, year):
        f, t = self.get_weeks_of_year(year)
        return range(f, t + 1)

    def months_to_weeks(self, from_, to_):
        from_year, to_year = (from_ - 1) // 12, (to_ - 1) // 12
        from_month, to_month = from_ % 12 or 12, to_ % 12 or 12
        return {
            'from': {'year': from_year, 'week': self.get_weeks_of_month(from_year, from_month)[0]},
            'to': {'year': to_year, 'week': self.get_weeks_of_month(to_year, to_month)[1]}
        }

    def years_to_weeks(self, from_, to_):
        return {
            'from': {'year': from_, 'week': 1},
            'to': {'year': to_, 'week': self.get_weeks_of_year(to_)[1]}
        }

    def week_to_month(self, year, week):
        for month in range(1, 13):
            from_, to_ = self.get_weeks_of_month(year, month)
            if from_ <= week <= to_:
                return month

    def get_months_of_interval(self, interval):
        fromto = interval.split('-')
        if len(fromto) == 1:
            from_, to_ = self.strpmonth(fromto[0]), datetime.now()
        elif len(fromto) == 2:
            from_, to_ = self.strpmonth(fromto[0]), self.strpmonth(fromto[1])
        else:
            raise IntervalFormatError()
        return from_.year * 12 + from_.month, to_.year * 12 + to_.month

    def get_years_of_interval(self, interval):
        fromto = interval.split('-')
        if len(fromto) == 1:
            from_, to_ = self.strpyear(fromto[0]), datetime.now()
        elif len(fromto) == 2:
            from_, to_ = self.strpyear(fromto[0]), self.strpyear(fromto[1])
        else:
            raise IntervalFormatError()
        return from_.year, to_.year

    def get_weeks_of_interval(self, interval):
        fromto = interval.split('-')
        if len(fromto) == 1:
            from_year, to_year = self.strpyear(fromto[0][:4]).year, datetime.now().year
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

    def get_weeks_by_interval(self, interval):
        if not interval:
            return []
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

    def get_weeks_by_last_period(self, last):
        if not last:
            return []
        if last[-1] == 'y':
            from_, to_ = datetime.now().year - int(last[:-1]) + 1, datetime.now().year
            weeks = self.years_to_weeks(from_, to_)
        elif last[-1] == 'm':
            current_month = datetime.now().year * 12 + datetime.now().month
            from_, to_ = current_month - int(last[:-1]) + 1, current_month
            weeks = self.months_to_weeks(from_, to_)
        elif last[-1] == 'w':
            now = datetime.now()
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

    def get_weeks(self):
        weeks = (
                self.get_weeks_by_interval(self.request.query_params.get('interval', '')) or
                self.get_weeks_by_last_period(self.request.query_params.get('last', '')) or
                self.get_weeks_by_last_period('3m')
        )
        if not weeks:
            return {}
        logger.info(weeks)
        invalid_year = weeks['from']['year'] > weeks['to']['year']
        invalid_week = weeks['from']['year'] == weeks['to']['year'] and weeks['from']['week'] > weeks['to']['week']
        if invalid_year or invalid_week:
            raise IntervalOrderError()
        now = datetime.now()
        from_ = [weeks['from']['week'], self.get_weeks_of_year(weeks['from']['year'])[1]]
        to_ = [1, weeks['to']['week']]
        if weeks['from']['year'] == weeks['to']['year']:
            from_[1] = weeks['to']['week']
            to_[0] = weeks['from']['week']
        elif now.year == weeks['from']['year']:
            from_[1] = int(now.strftime('%W'))
        weeks['from']['week'] = from_
        weeks['to']['week'] = to_
        logger.info(weeks)
        return weeks

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
        return ('(' + ' OR '.join(where_weeks) + ')') if weeks else ''

    def get_where_church(self):
        church = self.request.query_params.get('church')
        if not church:
            return ''
        return " AND r.church_id = {church}".format(church=church)

    def get_where_pastor_tree(self):
        pastor_tree = self.request.query_params.get('pastor_tree')
        if not pastor_tree:
            return ''
        try:
            pastor = CustomUser.objects.get(pk=pastor_tree)
        except CustomUser.DoesNotExist:
            return ' AND FALSE'
        return " AND a.path like '{path}%' AND a.depth >= {depth}".format(path=pastor.path, depth=pastor.depth)

    def get_where_pastor(self):
        pastor = self.request.query_params.get('pastor')
        if not pastor:
            return ''
        return " AND r.pastor_id = {pastor}".format(pastor=pastor)

    def get_where_filter(self, weeks):
        where = ''
        where += self.get_where_weeks(weeks)
        where += self.get_where_church()
        where += self.get_where_pastor()
        where += self.get_where_pastor_tree()
        return 'WHERE ' + where if where else ''

    def get_data(self, weeks):
        where = self.get_where_filter(weeks)
        query = self.SQL.format(filter=where)
        with connection.cursor() as connect:
            connect.execute(query)
            result = connect.fetchall()
        logger.info(query)
        logger.info(result)
        return [
            {
                'year': int(r[0]),
                'week': int(r[1]),
                'month': self.week_to_month(int(r[0]), int(r[1])),
                'count_people': int(r[2]),
                'count_new_people': int(r[3]),
                'count_repentance': int(r[4]),
                'tithe': r[5],
                'donations': r[6],
                'transfer_payments': r[7],
                'pastor_tithe': r[8],
            }
            for r in result
        ]

    def group_by(self, y, m, w, aggr_by_key):
        return {
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

    def group_by_week(self, result, weeks):
        def aggr_by_key(key, func=sum):
            return func([r.get(key, 0) for r in result if (r['year'] == y and r['week'] == w)] or [0])

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

    def group_by_month(self, result, weeks):
        def aggr_by_key(key, func=sum):
            return func([r.get(key, 0) for r in result if (r['year'] == y and r['month'] == m)] or [0])

        y = weeks['from']['year']
        months = set()
        for w in range(weeks['from']['week'][0], weeks['from']['week'][1] + 1):
            months.add(self.week_to_month(y, w))
        for m in months:
            yield self.group_by(y, m, list(self.get_weeks_of_month(y, m)), aggr_by_key)

        for y in range(weeks['from']['year'] + 1, weeks['to']['year']):
            year_weeks = self.get_weeks_of_year(y)
            months = set()
            for w in range(year_weeks[0], year_weeks[1] + 1):
                months.add(self.week_to_month(y, w))
            for m in months:
                yield self.group_by(y, m, list(self.get_weeks_of_month(y, m)), aggr_by_key)

        y = weeks['to']['year']
        if y > weeks['from']['year']:
            months = set()
            for w in range(weeks['to']['week'][0], weeks['to']['week'][1] + 1):
                months.add(self.week_to_month(y, w))
            for m in months:
                yield self.group_by(y, m, list(self.get_weeks_of_month(y, m)), aggr_by_key)

    def group_by_year(self, result, weeks):
        def aggr_by_key(key, func=sum):
            return func([r.get(key, 0) for r in result if r['year'] == y] or [0])

        y = weeks['from']['year']
        yield self.group_by(y, (1, 12), list(self.get_weeks_of_year(y)), aggr_by_key)

        for y in range(weeks['from']['year'] + 1, weeks['to']['year']):
            yield self.group_by(y, (1, 12), list(self.get_weeks_of_year(y)), aggr_by_key)

        y = weeks['to']['year']
        if y > weeks['from']['year']:
            yield self.group_by(y, (1, 12), list(self.get_weeks_of_year(y)), aggr_by_key)

    def get(self, request, *args, **kwargs):
        try:
            weeks = self.get_weeks()
        except IntervalFormatError:
            raise exceptions.ValidationError({'detail': _('Invalid "interval" format')})
        except IntervalOrderError:
            raise exceptions.ValidationError({'detail': _('Invalid "interval" order')})
        except LastPeriodFormatError:
            raise exceptions.ValidationError({'detail': _('Invalid "last" format')})
        group_by = request.query_params.get('group_by', 'week')
        result = self.get_data(weeks)
        if group_by == 'week':
            return Response(data=self.group_by_week(result, weeks))
        if group_by == 'month':
            return Response(data=self.group_by_month(result, weeks))
        if group_by == 'year':
            return Response(data=self.group_by_year(result, weeks))
        return Response(data=[])
