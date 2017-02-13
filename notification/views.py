# -*- coding: utf-8
from __future__ import unicode_literals

from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated

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
        page = self.paginate_queryset(date_notifications)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)
