# -*- coding: utf-8
from models import Notification
from serializers import NotificationSerializer
from rest_framework.decorators import list_route
from rest_framework import viewsets, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated,)
    @list_route()
    def today(self, request):
        weekday = timezone.now().weekday() + 1
        date = timezone.now().date()
        date_notifications = Notification.objects.filter(date=date).all()
        objects = date_notifications
        page = self.paginate_queryset(objects)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(objects, many=True)
        return Response(serializer.data)

