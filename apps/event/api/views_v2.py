import logging
from django.db import transaction, IntegrityError
from django.db.models import (IntegerField, Sum, When, Case, Count, OuterRef, Exists, Q,
                              BooleanField)
from django.http import QueryDict, Http404
from django.utils.translation import ugettext_lazy as _
from django_filters import rest_framework
from rest_framework import status, exceptions
from rest_framework.decorators import action
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
    MeetingWithoutColumnPagination, MeetingVisitorsPagination, ChurchReportPagination,
    MeetingSummaryPagination, ReportsSummaryPagination)
from apps.event.api.serializers import (
    MeetingVisitorsSerializer, MeetingSerializer, MeetingDetailSerializer,
    MeetingListSerializer, ChurchReportStatisticSerializer,
    MeetingStatisticSerializer, ChurchReportSerializer,
    ChurchReportListSerializer, MeetingDashboardSerializer,
    ChurchReportDetailSerializer, ChurchReportsDashboardSerializer,
    MeetingSummarySerializer, ChurchReportSummarySerializer, MobileReportsDashboardSerializer)
from apps.event.models import Meeting, ChurchReport, MeetingAttend
from common.filters import FieldSearchFilter, OrderingFilterWithPk
from common.parsers import MultiPartAndJsonParser


logger = logging.getLogger(__name__)

MEETINGS_SUMMARY_ORDERING_FIELDS = ('last_name', 'master__last_name', 'meetings_submitted',
                                    'meetings_expired', 'meetings_in_progress')

EVENT_SUMMARY_SEARCH_FIELDS = {'search_fio': ('last_name', 'first_name', 'middle_name')}

class MeetingViewSet(ModelViewSet, EventUserTreeMixin):
    queryset = Meeting.objects.select_related('owner', 'type', 'home_group__leader')

    serializer_class = MeetingSerializer
    serializer_retrieve_class = MeetingDetailSerializer
    serializer_list_class = MeetingListSerializer

    permission_classes = (IsAuthenticated,)
    pagination_class = MeetingWithoutColumnPagination

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
                       'total_sum', 'new_count', 'guest_count', 'repentance_count')

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
        """
        New version of submit action.
        Pass users' ids who attended meeting as list
        """

        meeting = self.get_object()
        attends = self.validate_to_submit(meeting, request.data)
        meeting.status = Meeting.SUBMITTED
        meeting_serializer = self.serializer_class(meeting, data=request.data, partial=True)
        meeting_serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                self.perform_update(meeting_serializer)
                users_qs = CustomUser.objects.all()
                new_attends = list()
                for attend in attends['attended']:
                    user = users_qs.get(user_ptr_id=attend)
                    new_attends.append(MeetingAttend(
                        meeting=meeting,
                        user=user,
                        attended=True,
                        note='',

                        is_stable=user.is_stable,
                        master=user.master,
                        church=user.cchurch,
                        home_group=user.hhome_group,
                    ))
                for attend in attends['missed']:
                    user = users_qs.get(user_ptr_id=attend)
                    new_attends.append(MeetingAttend(
                        meeting=meeting,
                        user=user,
                        attended=False,
                        note='',

                        is_stable=user.is_stable,
                        master=user.master,
                        church=user.cchurch,
                        home_group=user.hhome_group,
                    ))
                MeetingAttend.objects.bulk_create(new_attends)
        except IntegrityError:
            data = {'detail': _('При сохранении возникла ошибка. Попробуйте еще раз.')}
            return Response(data, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        headers = self.get_success_headers(meeting_serializer.data)
        return Response({'message': _('Отчет Домашней Группы успешно подан.')},
                        status=status.HTTP_200_OK, headers=headers)

    @staticmethod
    def validate_to_submit(meeting, data):
        """
        New version validate_to_submit for submit_meeting
        """
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

        attends = data.getlist('attends')
        valid_visitors = list(meeting.home_group.uusers.values_list('id', flat=True))
        try:
            valid_attends = [user_id for user_id in attends if int(user_id) in valid_visitors]
        except Exception as e:
            print(e)
            raise exceptions.ValidationError({
                'detail': _('Список должен состоять из идентификаторов пользователей, например "13885" ')
            })
        missed = [user_id for user_id in valid_visitors if user_id not in valid_attends]

        if not valid_attends:
            raise exceptions.ValidationError({
                'detail': _('Переданный список присутствующих некорректен.')
            })
        attends = {'attended': valid_attends, 'missed':missed}
        return attends

    def post(self, request, pk, *args, **kwargs):
        return self.submit(request, pk, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        meeting = self.get_object()
        meeting_serializer = self.get_serializer(meeting, data=request.data, partial=True)
        meeting_serializer.is_valid(raise_exception=True)

        data = request.data
        if isinstance(data, QueryDict):
            data._mutable = True



        try:
            with transaction.atomic():
                self.perform_update(meeting_serializer)
                attends = data.getlist('attends')
                if attends:
                    MeetingAttend.objects.filter(user__id__in=attends, meeting=meeting).update(attended=True)
                    MeetingAttend.objects.exclude(user__id__in=attends, meeting=meeting).update(attended=False)
                else:
                    MeetingAttend.objects.filter(meeting=meeting).update(attended=False)

        except IntegrityError as err:
            data = {'detail': _('При обновлении возникла ошибка. Попробуйте еще раз.')}
            logger.error(err)
            return Response(data, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        headers = self.get_success_headers(meeting_serializer.data)
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
        try:
            master = CustomUser.objects.get(id=master_id)
        except CustomUser.DoesNotExist:
            raise exceptions.ValidationError(_('Master with id = %s does not exist') % master_id)
        if master_id:
            query = CustomUser.objects.for_user(user=master)
        else:
            query = CustomUser.objects.for_user(self.request.user)

        statistics['new_repentance'] = query.filter(repentance_date__range=[from_date, to_date]).count()

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
            user, extra_perms=False).filter(status__in=[1, 3]).count() or None

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

        hg_leaders = CustomUser.objects.for_user(user).filter(home_group__leader__isnull=False)
        hg_leaders = hg_leaders.annotate(
            meetings_in_progress=Sum(Case(
                When(home_group__meeting__status=1, then=1),
                output_field=IntegerField(), default=0), distinct=True),
            meetings_submitted=Sum(Case(
                When(home_group__meeting__status=2, then=1),
                output_field=IntegerField(), default=0), distinct=True),
            meetings_expired=Sum(Case(
                When(home_group__meeting__status=3, then=1),
                output_field=IntegerField(), default=0), distinct=True)).distinct()
        hg_leaders = self.filter_queryset(hg_leaders)

        page = self.paginate_queryset(hg_leaders)
        leaders = self.serializer_class(page, many=True)
        return self.get_paginated_response(leaders.data)