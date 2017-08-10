# -*- coding: utf-8
from __future__ import unicode_literals

import redis
from rest_framework import viewsets, status
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from summit.models import SummitTicket
from .serializers import NotificationSerializer
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
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = NotificationPagination

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

    @list_route(methods=['GET'], filter_backends=[FilterByUserBirthday])
    def birthdays(self, request):
        queryset = self.filter_queryset(self.queryset)
        birthdays = self.serializer_class(queryset, many=True)

        if request.query_params.get('only_count'):
            return Response({'birthdays_count': len(queryset)})

        return Response(birthdays.data, status=status.HTTP_200_OK)

    @list_route(methods=['GET'], filter_backends=[FilterByUserRepentance])
    def repentance(self, request):
        queryset = self.filter_queryset(self.queryset)
        repentance = self.serializer_class(queryset, many=True)

        if request.query_params.get('only_count'):
            return Response({'repentance_count': len(queryset)})

        return Response(repentance.data, status=status.HTTP_200_OK)
