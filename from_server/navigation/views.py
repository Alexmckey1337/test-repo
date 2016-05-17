# -*- coding: utf-8
from models import Navigation
from rest_framework import viewsets, filters
from serializers import NavigationSerializer
from datetime import timedelta
from django.utils import timezone
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from collections import OrderedDict
from rest_framework.decorators import api_view
from django.shortcuts import render


class NavigationViewSet(viewsets.ModelViewSet):
    queryset = Navigation.objects.all()
    serializer_class = NavigationSerializer