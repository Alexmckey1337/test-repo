# -*- coding: utf-8
from models import Status
from serializers import StatusSerializer
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
from report.models import UserReport


class StatusViewSet(viewsets.ModelViewSet):
    queryset = Status.objects.all()
    serializer_class = StatusSerializer
