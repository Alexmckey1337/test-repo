# -*- coding: utf-8
from __future__ import unicode_literals

import django_filters
from django.utils import six
from rest_framework import viewsets, filters
from rest_framework.decorators import api_view
from rest_framework.decorators import list_route
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from account.pagination import ShortPagination
from navigation.models import event_table
from .models import Participation, Event, EventAnket, EventType
from .serializers import ParticipationSerializer, EventSerializer, EventTypeSerializer, EventAnketSerializer


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
                     'user__user__hierarchy__title', 'user__user__department__title',
                     'user__user__email',)
    ordering_fields = ('user__user__first_name', 'user__user__last_name', 'user__user__hierarchy__level',
                       'user__user__country', 'user__user__region', 'user__user__city', 'user__user__district',
                       'user__user__address', 'user__user__skype', 'user__user__phone_number',
                       'user__user__hierarchy__title', 'user__user__department__title',
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
