# -*- coding: utf-8
from __future__ import unicode_literals

from django.db.models import IntegerField, Sum, When, Case, Count
from rest_framework import status, filters, exceptions
from rest_framework.decorators import list_route, detail_route
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils.translation import ugettext_lazy as _
from django.db import transaction, IntegrityError

from account.models import CustomUser
from common.filters import FieldSearchFilter
from common.views_mixins import ModelWithoutDeleteViewSet

from .filters import ChurchReportFilter, MeetingFilter, CommonEventFilter
from .models import Meeting, ChurchReport, MeetingAttend
from .serializers import (UserNameSerializer, MeetingSerializer, MeetingDetailSerializer,
                          MeetingListSerializer, ChurchReportStatisticSerializer,
                          MeetingStatisticSerializer, ChurchReportSerializer,
                          ChurchReportListSerializer)


class MeetingPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'results': data
        })


class MeetingViewSet(ModelWithoutDeleteViewSet):
    queryset = Meeting.objects.all()

    serializer_class = MeetingSerializer
    serializer_retrieve_class = MeetingDetailSerializer
    serializer_list_class = MeetingListSerializer

    permission_classes = (IsAuthenticated,)
    pagination_class = MeetingPagination

    filter_backends = (filters.DjangoFilterBackend,
                       CommonEventFilter,
                       FieldSearchFilter,
                       filters.OrderingFilter)

    filter_fields = ('data', 'type', 'owner', 'home_group', 'church', 'status')

    filter_class = MeetingFilter

    field_search_fields = {
        'search_date': ('date',)
    }

    def get_serializer_class(self):
        if self.action == 'list':
            return self.serializer_list_class
        if self.action in ['retrieve', 'update', 'partial_update']:
            return self.serializer_retrieve_class
        return self.serializer_class

    def get_queryset(self):
        if self.action == 'list':
            return self.queryset.annotate(
                visitors_attended=Sum(Case(
                    When(attends__attended=True, then=1),
                    output_field=IntegerField(), default=0)),

                visitors_absent=Sum(Case(When(
                    attends__attended=False, then=1),
                    output_field=IntegerField(), default=0))
            )
        return self.queryset

    @detail_route(methods=['POST'], serializer_class=MeetingDetailSerializer)
    def submit(self, request, pk):
        home_meeting = self.get_object()
        self.validate_to_submit(meeting=home_meeting, data=request.data)

        home_meeting.status = 2
        meeting = self.serializer_class(home_meeting, data=request.data, partial=True)
        meeting.is_valid(raise_exception=True)

        valid_attends = [user.id for user in home_meeting.home_group.users.all()]
        visitors = request.data.pop('visitors')

        try:
            with transaction.atomic():
                self.perform_update(meeting)
                for visitor in visitors:
                    for attend in visitor.get('attends'):
                        if attend.get('user') in valid_attends:
                            MeetingAttend.objects.create(meeting_id=home_meeting.id,
                                                         user_id=attend.get('user'),
                                                         attended=attend.get('attended', False),
                                                         note=attend.get('note', ''))
        except IntegrityError:
            data = {'message': _('При сохранении возникла ошибка. Попробуйте еще раз.')}
            return Response(data, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        headers = self.get_success_headers(meeting.data)
        return Response(meeting.data, status=status.HTTP_201_CREATED, headers=headers)

    @staticmethod
    def validate_to_submit(meeting, data):
        if meeting.type.code == 'service' and int(data.get('total_sum')) != 0:
            raise exceptions.ValidationError(
                _('Невозможно подать отчет. Отчет типа - {%s} не должен содержать '
                  'денежную сумму. ' % meeting.type.name))

        if not data.get('visitors'):
            raise exceptions.ValidationError(
                _('Невозможно подать отчет. Список присутствующих не передан.'))

        if meeting.status == 2:
            raise exceptions.ValidationError(
                _('Невозможно повторно подать отчет. Данный отчет - {%s}, '
                  'уже был подан ранее. ') % meeting)

    def update(self, request, *args, **kwargs):
        meeting = self.get_object()
        meeting = self.get_serializer(meeting, data=request.data, partial=True)
        meeting.is_valid(raise_exception=True)

        if not request.data.get('attends'):
            self.perform_update(meeting)
            return Response(meeting.data)

        attends = request.data.pop('attends')

        try:
            with transaction.atomic():
                self.perform_update(meeting)
                for attend in attends:
                    MeetingAttend.objects.filter(id=attend.get('id')).update(
                        user=attend.get('user'),
                        attended=attend.get('attended', False),
                        note=attend.get('note', '')
                    )
        except IntegrityError:
            data = {'message': _('При обновлении возникла ошибка. Попробуйте еще раз.')}
            return Response(data, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        headers = self.get_success_headers(meeting.data)
        return Response(meeting.data, status=status.HTTP_201_CREATED, headers=headers)

    @detail_route(methods=['GET'], serializer_class=UserNameSerializer)
    def visitors(self, request, pk):
        meeting = self.get_object()
        visitors = meeting.home_group.users.all()
        visitors = self.serializer_class(visitors, many=True)

        return Response(visitors.data)

    @list_route(methods=['GET'], serializer_class=MeetingStatisticSerializer)
    def statistics(self, request):
        queryset = self.filter_queryset(self.queryset)

        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')

        statistics = queryset.aggregate(
            total_visitors=Count('visitors'),
            total_visits=Sum(Case(When(attends__attended=True, then=1),
                                  output_field=IntegerField(), default=0)),
            total_absent=Sum(Case(When(attends__attended=False, then=1),
                                  output_field=IntegerField(), default=0)),
            reports_in_progress=Sum(Case(When(status=1, then=1),
                                         output_field=IntegerField(), default=0)),
            reports_submitted=Sum(Case(When(status=2, then=1),
                                       output_field=IntegerField(), default=0)),
            reports_expired=Sum(Case(When(status=3, then=1),
                                     output_field=IntegerField(), default=0))
        )
        statistics.update(queryset.aggregate(total_donations=Sum('total_sum')))
        statistics['new_repentance'] = CustomUser.objects.filter(
            repentance_date__range=[from_date, to_date]).count()

        statistics = self.serializer_class(statistics)
        return Response(statistics.data)


class ChurchReportViewSet(ModelWithoutDeleteViewSet):
    queryset = ChurchReport.objects.all()

    serializer_class = ChurchReportSerializer
    serializer_list_class = ChurchReportListSerializer

    permission_classes = (IsAuthenticated,)
    pagination_class = MeetingPagination

    filter_backends = (filters.DjangoFilterBackend,
                       FieldSearchFilter,
                       filters.OrderingFilter,)

    filter_class = ChurchReportFilter

    field_search_fields = {
        'search_date': ('date',)
    }

    def get_serializer_class(self):
        if self.action == 'list':
            return self.serializer_list_class
        return self.serializer_class

    @detail_route(methods=['POST'])
    def submit(self, request, pk):
        church_report = self.get_object()
        if church_report.status == 2:
            raise exceptions.ValidationError(
                _('Невозможно подать отчет. Данный отчет уже был подан ранее'))

        report = self.get_serializer(church_report, data=request.data, partial=True)
        report.is_valid(raise_exception=True)
        church_report.status = 2
        self.perform_update(report)
        headers = self.get_success_headers(report.data)

        return Response(report.data, status=status.HTTP_201_CREATED, headers=headers)

    @list_route(methods=['GET'], serializer_class=ChurchReportStatisticSerializer)
    def statistics(self, request):
        queryset = self.filter_queryset(self.queryset)
        statistics = queryset.aggregate(
            total_peoples=Sum('count_people'),
            total_new_peoples=Sum('new_people'),
            total_repentance=Sum('count_repentance'),
            total_tithe=Sum('tithe'),
            total_donations=Sum('donations'),
            total_transfer_payments=Sum('transfer_payments'),
            total_pastor_tithe=Sum('pastor_tithe'))

        statistics = self.serializer_class(statistics)
        statistics.is_valid(raise_exception=True)

        return Response(statistics.data)
