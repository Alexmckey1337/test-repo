# -*- coding: utf-8
from models import Notification
from serializers import NotificationSerializer
from rest_framework.decorators import list_route
from rest_framework.decorators import api_view
from rest_framework import viewsets, filters
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.contrib.auth import update_session_auth_hash
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.template.loader import get_template
from django.template import Context
from django.core.mail import EmailMultiAlternatives
from rest_framework.permissions import AllowAny
import hashlib
import random
import json
from django.utils import timezone
from datetime import timedelta

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer


    @list_route()
    def today(self, request):
        weekday = timezone.now().weekday() + 1
        date = timezone.now().date()
        date_notifications = Notification.objects.filter(date=date).all()
        #weekday_events = Notification.objects.filter(day=weekday, cyclic=True).all()
        objects = date_notifications
        page = self.paginate_queryset(objects)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(objects, many=True)
        return Response(serializer.data)
