# -*- coding: utf-8
from __future__ import unicode_literals

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Department, Hierarchy
from .serializers import DepartmentSerializer, HierarchySerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = (IsAuthenticated,)


class HierarchyViewSet(viewsets.ModelViewSet):
    queryset = Hierarchy.objects.exclude(title='Архонт').all()
    serializer_class = HierarchySerializer
    permission_classes = (IsAuthenticated,)
