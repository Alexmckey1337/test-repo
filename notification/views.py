# -*- coding: utf-8
from __future__ import unicode_literals

import redis
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from summit.models import SummitTicket
from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated,)

    @list_route()
    def today(self, request):
        date = timezone.now().date()
        date_notifications = Notification.objects.filter(date=date)
        try:
            r = redis.StrictRedis(host='localhost', port=6379, db=0)
            ticket_ids = r.smembers('summit:ticket:{}'.format(request.user.id))
            tickets = SummitTicket.objects.filter(id__in=ticket_ids)
        except Exception as err:
            tickets = SummitTicket.objects.none()
            print(err)
        return Response({'count': date_notifications.count() + tickets.count()})
