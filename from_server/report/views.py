# -*- coding: utf-8
from models import UserReport, DayReport, MonthReport, YearReport
from serializers import UserReportSerializer, DayReportSerializer, MonthReportSerializer, YearReportSerializer
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
from account.models import CustomUser as User
from django.utils import timezone
from datetime import timedelta


class UserReportViewSet(viewsets.ModelViewSet):
    queryset = UserReport.objects.all()
    serializer_class = UserReportSerializer
    filter_backends = (filters.DjangoFilterBackend,
                       filters.SearchFilter,)
    search_fields = ('@date', 'user', )
    filter_fields = ['date', ]


class DayReportViewSet(viewsets.ModelViewSet):
    queryset = DayReport.objects.all()
    serializer_class = DayReportSerializer
    filter_backends = (filters.DjangoFilterBackend,
                       filters.SearchFilter,)
    #search_fields = ('@date', 'user', )
    filter_fields = ['date', 'event', 'department', ]


class MonthReportViewSet(viewsets.ModelViewSet):
    queryset = MonthReport.objects.all()
    serializer_class = MonthReportSerializer
    filter_backends = (filters.DjangoFilterBackend,
                       filters.SearchFilter,)
    #search_fields = ('@date', 'user', )
    filter_fields = ['department', ]


class YearReportViewSet(viewsets.ModelViewSet):
    queryset = YearReport.objects.all()
    serializer_class = YearReportSerializer
    filter_backends = (filters.DjangoFilterBackend,
                       filters.SearchFilter,)
    #search_fields = ('@date', 'user', )
    filter_fields = ['department', ]
