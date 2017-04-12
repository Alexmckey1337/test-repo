# -*- coding: utf-8
from __future__ import unicode_literals

import django_filters
from django.db import transaction, IntegrityError
from django.db.models import IntegerField, Sum, When, Case, Count
from django.utils import six
from rest_framework import status
from rest_framework import viewsets, filters
from rest_framework.decorators import api_view
from rest_framework.decorators import list_route
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from account.models import CustomUser
from account.pagination import ShortPagination
from common.filters import FieldSearchFilter
from common.views_mixins import ModelWithoutDeleteViewSet
from group.models import HomeGroup, Church
from group.serializers import HomeGroupListSerializer, ChurchListSerializer
from navigation.table_fields import event_table
from .models import Participation, Event, EventAnket, EventType, MeetingAttend, Meeting, ChurchReport
from .serializers import (MeetingListSerializer, MeetingDetailSerializer, MeetingSerializer,
                          ChurchReportSerializer, ChurchReportListSerializer, MeetingStatisticsSerializer)
from .serializers import ParticipationSerializer, EventSerializer, EventTypeSerializer, EventAnketSerializer


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


class MeetingFilter(django_filters.FilterSet):
    from_date = django_filters.DateFilter(name="date", lookup_type='gte')
    to_date = django_filters.DateFilter(name="date", lookup_type='lte')

    class Meta:
        model = Meeting
        fields = ['type', 'home_group', 'from_date', 'to_date']


class MeetingViewSet(ModelWithoutDeleteViewSet):
    queryset = Meeting.objects.all()

    serializer_class = MeetingSerializer
    serializer_list_class = MeetingListSerializer
    serializer_retrieve_class = MeetingDetailSerializer

    filter_backends = (filters.DjangoFilterBackend,
                       FieldSearchFilter,
                       filters.OrderingFilter,)

    filter_class = MeetingFilter
    permission_classes = (IsAuthenticated,)
    pagination_class = MeetingPagination

    field_search_fields = {
        'search_date': ('date',)
    }

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return self.serializer_retrieve_class
        if self.action == 'list':
            return self.serializer_list_class
        return self.serializer_class

    def get_queryset(self):
        if self.action == 'list':
            return self.queryset.annotate(
                visitors_attended=Sum(Case(When(attends__attended=True, then=1),
                                           output_field=IntegerField(), default=0)),
                visitors_absent=Sum(Case(When(attends__attended=False, then=1),
                                         output_field=IntegerField(), default=0)))
        return self.queryset

    def create(self, request, *args, **kwargs):
        data = request.data
        home_group_id = data.get('home_group')
        leader_id = data.get('owner')

        home_group = get_object_or_404(HomeGroup, pk=home_group_id)

        if home_group.leader.id != leader_id:
            return Response({'message': 'Невозможно создать отчет. '
                                        'Указанный пользователь не является лидером данной Домашней Группы.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if not data.get('visitors'):
            return Response({'message': 'Невозможно создать отчет. '
                                        'Список присутствующих не передан.'},
                            status=status.HTTP_400_BAD_REQUEST)

        visitors = data.pop('visitors')
        valid_attends = [user.id for user in home_group.users.all()]
        meeting = self.get_serializer(data=data)
        meeting.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                new_meeting = meeting.save()
                for visitor in visitors:
                    for attend in visitor.get('attends'):
                        if attend.get('user') in valid_attends:
                            MeetingAttend.objects.create(meeting_id=new_meeting.id,
                                                         user_id=attend.get('user'),
                                                         attended=attend.get('attended', False),
                                                         note=attend.get('note', ''))
        except IntegrityError:
            data = {'message': 'При сохранении возникла ошибка. Попробуйте еще раз.'}
            return Response(data, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        headers = self.get_success_headers(meeting.data)
        return Response(meeting.data, status=status.HTTP_201_CREATED, headers=headers)

    @list_route(methods=['get'])
    def get_leader_groups(self, request):
        serializer = HomeGroupListSerializer
        leader_id = request.query_params.get('leader_id')

        if not leader_id:
            return Response({'message': 'Некоректные данные.'},
                            status=status.HTTP_400_BAD_REQUEST)
        home_groups = HomeGroup.objects.filter(leader__id=leader_id)
        home_groups_list = serializer(home_groups, many=True)
        return Response(home_groups_list.data)

    @list_route(methods=['get'])
    def statistics(self, request):
        serializer = MeetingStatisticsSerializer
        queryset = self.filter_queryset(self.queryset)
        statistics = queryset.aggregate(
            total_visitors=Count('visitors'),
            total_visits=Sum(Case(When(attends__attended=True, then=1),
                                  output_field=IntegerField(), default=0)),
            total_absents=Sum(Case(When(attends__attended=False, then=1),
                                   output_field=IntegerField(), default=0)))
        statistics.update(queryset.aggregate(total_donations=Sum('total_sum')))

        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')
        statistics['new_repentance'] = CustomUser.objects.filter(repentance_date__range=[from_date, to_date]).count()

        statistics = serializer(statistics)
        return Response(statistics.data)


class ChurchReportViewSet(ModelWithoutDeleteViewSet):
    queryset = ChurchReport.objects.all()

    filter_backends = (filters.DjangoFilterBackend,
                       filters.OrderingFilter,)

    permission_classes = (IsAuthenticated,)
    pagination_class = MeetingPagination

    serializer_class = ChurchReportSerializer
    serializer_list_class = ChurchReportListSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return self.serializer_list_class
        return self.serializer_class

    def create(self, request, *args, **kwargs):
        data = request.data
        pastor_id = data.get('pastor')
        church_id = data.get('church')

        church = get_object_or_404(Church, pk=church_id)

        if church.pastor.id != pastor_id:
            return Response({'message': 'Невозможно создать отчет. '
                                        'Данный пользователь не является пастором данной Церкви.'},
                            status=status.HTTP_400_BAD_REQUEST)

        report = self.get_serializer(data=request.data)
        report.is_valid(raise_exception=True)
        self.perform_create(report)
        headers = self.get_success_headers(report.data)
        return Response(report.data, status=status.HTTP_201_CREATED, headers=headers)

    @list_route(methods=['get'])
    def get_pastor_churches(self, request):
        serializer = ChurchListSerializer
        pastor_id = request.query_params.get('pastor_id')
        if not pastor_id:
            return Response({'message': 'Некоректные данные.'},
                            status=status.HTTP_400_BAD_REQUEST)

        churches = Church.objects.filter(pastor__id=pastor_id)
        churches_list = serializer(churches, many=True)
        return Response(churches_list.data)

    @list_route(methods=['get'])
    def statistics(self, request):
        pass


class ParticipationPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'page_size'
    max_page_size = 30
    permission_classes = (IsAuthenticated,)

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'common_table': event_table(),
            'results': data
        })


class EventFilter(filters.FilterSet):
    from_date = django_filters.DateFilter(name="from_date", lookup_type='gte')
    to_date = django_filters.DateFilter(name="to_date", lookup_type='lte')

    class Meta:
        model = Event
        fields = ['event_type', 'to_date', 'from_date', ]


class EventTypeViewSet(viewsets.ModelViewSet):
    queryset = EventType.objects.all()
    serializer_class = EventTypeSerializer
    filter_backends = (filters.DjangoFilterBackend,
                       filters.SearchFilter,)
    search_fields = ()
    permission_classes = (IsAuthenticated,)
    filter_fields = []


class EventAnketViewSet(viewsets.ModelViewSet):
    queryset = EventAnket.objects.all()
    serializer_class = EventAnketSerializer
    filter_backends = (filters.DjangoFilterBackend,
                       filters.SearchFilter,)
    search_fields = ()
    permission_classes = (IsAuthenticated,)
    filter_fields = []


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    filter_backends = (filters.DjangoFilterBackend,
                       filters.SearchFilter,)
    search_fields = ()
    filter_class = EventFilter
    pagination_class = ShortPagination
    permission_classes = (IsAuthenticated,)


class ParticipationViewSet(viewsets.ModelViewSet):
    queryset = Participation.objects.all()
    serializer_class = ParticipationSerializer
    filter_backends = (filters.DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter,)
    pagination_class = ParticipationPagination
    filter_fields = ['event', 'user__user__master', 'user__user', ]
    search_fields = ('user__user__first_name', 'user__user__last_name', 'user__user__middle_name',
                     'user__user__country', 'user__user__region', 'user__user__city', 'user__user__district',
                     'user__user__address', 'user__user__skype', 'user__user__phone_number',
                     'user__user__hierarchy__title',
                     'user__user__email',)
    ordering_fields = ('user__user__first_name', 'user__user__last_name', 'user__user__hierarchy__level',
                       'user__user__country', 'user__user__region', 'user__user__city', 'user__user__district',
                       'user__user__address', 'user__user__skype', 'user__user__phone_number',
                       'user__user__hierarchy__title',
                       'user__user__email',)
    permission_classes = (IsAuthenticated,)

    @list_route()
    def disciples(self, request):
        from .utils import get_disciple_participations
        q = get_disciple_participations(request.user)
        queryset = self.filter_queryset(q)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@api_view(['POST'])
def update_participation(request):
    '''POST: (id, check, value)'''
    response_dict = dict()
    if request.method == 'POST':
        data = request.data
        try:
            object = Participation.objects.get(id=data['id'])
            for key, value in six.iteritems(data):
                setattr(object, key, value)
            object.save()
            object.recount()
            serializer = ParticipationSerializer(object, context={'request': request})
            response_dict['data'] = serializer.data
            response_dict['message'] = "Участие успешно изменено."
            response_dict['status'] = True
        except Participation.DoesNotExist:
            response_dict['message'] = "Участие не существует."
            response_dict['status'] = False
    return Response(response_dict)


"""
class CreateMeetingView(CreateAPIView):
    serializer_class = MeetingSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        owner = get_object_or_404(CustomUser, id=data.get('owner'))
        owner_users_id = list(owner.get_children().values_list('id', flat=True))
        meeting_attend = data.pop('users')
        meeting_users_id = [int(a['user']) for a in meeting_attend]
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        valid_attend = [a for a in meeting_attend if int(a['user']) in owner_users_id]
        for user_id in owner_users_id:
            if user_id not in meeting_users_id:
                valid_attend.append({'user': user_id, 'attended': False, 'note': ''})

        try:
            with transaction.atomic():
                meeting = serializer.save()
                MeetingAttend.objects.bulk_create([MeetingAttend(
                    user_id=attend['user'], meeting_id=meeting.id, attended=attend['attended'],
                    note=attend['note']) for attend in valid_attend])
        except IntegrityError:
            data = {'message': 'При сохранении возникла ошибка. Попробуйте еще раз.'}
            return Response(data, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
"""
