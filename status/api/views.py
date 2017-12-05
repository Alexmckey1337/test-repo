# -*- coding: utf-8
from __future__ import unicode_literals

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from status.models import Status, Division
from status.api.serializers import StatusSerializer


class StatusViewSet(viewsets.ModelViewSet):
    queryset = Status.objects.all()
    serializer_class = StatusSerializer
    permission_classes = (IsAuthenticated,)


class DivisionViewSet(viewsets.ModelViewSet):
    queryset = Division.objects.all()
    serializer_class = StatusSerializer
    permission_classes = (IsAuthenticated,)
