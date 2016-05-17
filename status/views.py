# -*- coding: utf-8
from models import Status, Division
from serializers import StatusSerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

class StatusViewSet(viewsets.ModelViewSet):
    queryset = Status.objects.all()
    serializer_class = StatusSerializer
    permission_classes = (IsAuthenticated,)

class DivisionViewSet(viewsets.ModelViewSet):
    queryset = Division.objects.all()
    serializer_class = StatusSerializer
    permission_classes = (IsAuthenticated,)
