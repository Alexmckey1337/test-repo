# -*- coding: utf-8
from __future__ import unicode_literals

import redis
from rest_framework import viewsets, status
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from summit.models import SummitTicket
from .serializers import BirthdayNotificationSerializer, RepentanceNotificationSerializer
from account.models import CustomUser
from account.filters import FilterByUserBirthday, FilterByUserRepentance
from rest_framework.pagination import PageNumberPagination


class NotificationPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'results': data,
        })


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    permission_classes = (IsAuthenticated,)
    pagination_class = NotificationPagination
    serializer_class = BirthdayNotificationSerializer

    @list_route()
    def tickets(self, request):
        try:
            r = redis.StrictRedis(host='redis', port=6379, db=0)
            ticket_ids = r.smembers('summit:ticket:{}'.format(request.user.id))
            tickets = SummitTicket.objects.filter(id__in=ticket_ids)
        except Exception as err:
            tickets = SummitTicket.objects.none()
            print(err)
        return Response({'tickets_count': tickets.count()})

    @list_route(methods=['GET'],
                filter_backends=[FilterByUserBirthday],
                serializer_class=BirthdayNotificationSerializer,
                pagination_class=NotificationPagination)
    def birthdays(self, request):
        birthdays = self.filter_queryset(self.request.user.get_descendants())

        if request.query_params.get('only_count'):
            return Response({'birthdays_count': len(birthdays)})

        page = self.paginate_queryset(birthdays)
        if page is not None:
            birthdays = self.get_serializer(page, many=True)
            return self.get_paginated_response(birthdays.data)

        birthdays = self.serializer_class(birthdays, many=True)

        return Response(birthdays.data, status=status.HTTP_200_OK)

    @list_route(methods=['GET'],
                filter_backends=[FilterByUserRepentance],
                serializer_class=RepentanceNotificationSerializer,
                pagination_class=NotificationPagination)
    def repentance(self, request):
        repentance = self.filter_queryset(self.request.user.get_descendants())

        if request.query_params.get('only_count'):
            return Response({'repentance_count': len(repentance)})

        page = self.paginate_queryset(repentance)
        if page is not None:
            repentance = self.get_serializer(page, many=True)
            return self.get_paginated_response(repentance.data)

        repentance = self.serializer_class(repentance, many=True)

        return Response(repentance.data, status=status.HTTP_200_OK)

    @list_route(methods=['GET'])
    def exports(self, request):
        try:
            r = redis.StrictRedis(host='redis', port=6379, db=0)
            export_urls = r.smembers('export:%s' % request.user.id)
        except Exception as err:
            export_urls = []
            print(err)

        return Response({'export_urls': export_urls})
