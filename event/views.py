# -*- coding: utf-8
from __future__ import unicode_literals

import logging
import django_filters
from django.db import transaction, IntegrityError
from django.utils import six
from rest_framework import mixins
from rest_framework import status
from rest_framework import viewsets, filters
from rest_framework.decorators import api_view
from rest_framework.decorators import list_route
from rest_framework.generics import CreateAPIView, get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from account.models import CustomUser
from account.pagination import ShortPagination
from group.models import HomeGroup
from group.serializers import HomeGroupListSerializer
from navigation.table_fields import event_table
from .models import Participation, Event, EventAnket, EventType, MeetingAttend, Meeting
from .serializers import (
    ParticipationSerializer, EventSerializer, EventTypeSerializer, EventAnketSerializer,
    MeetingSerializer, MeetingUserSerializer)

logger = logging.getLogger(__name__)


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


class MeetingViewSet(mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.CreateModelMixin,
                     mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    queryset = Meeting.objects.all()

    serializer_class = MeetingSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = MeetingPagination

    @list_route(methods=['get'])
    def get_home_leaders(self, request):
        params = request.query_params
        leader_id = params.get('leader_id')

        serializer = HomeGroupListSerializer

        if not leader_id:
            return Response({'message': 'Некоректные данные.'},
                            status=status.HTTP_400_BAD_REQUEST)
        home_groups = HomeGroup.objects.filter(leader__id=leader_id)
        serializer = serializer(home_groups, many=True)
        return Response(serializer.data)

    @list_route(methods=['get'])
    def get_home_users(self, request):
        params = request.query_params
        home_group_id = params.get('home_group_id')

        serializer = MeetingUserSerializer

        if not home_group_id:
            return Response({'message': 'Некоректные данные'},
                            status=status.HTTP_400_BAD_REQUEST)
        users = CustomUser.objects.filter(home_groups__id=home_group_id)
        serializer = serializer(users, many=True)
        return Response(serializer.data)


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
    from_date = django_filters.DateFilter(name="from_date", lookup_expr='gte')
    to_date = django_filters.DateFilter(name="to_date", lookup_expr='lte')

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
        except IntegrityError as err:
            data = {'message': 'При сохранении возникла ошибка. Попробуйте еще раз.'}
            logger.error(err)
            return Response(data, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
