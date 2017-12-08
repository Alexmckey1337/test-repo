# -*- coding: utf-8
from __future__ import unicode_literals

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from hierarchy.api.serializers import DepartmentSerializer, HierarchySerializer
from hierarchy.models import Department, Hierarchy


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = (IsAuthenticated,)


class HierarchyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Hierarchy.objects.exclude(title='Архонт').all()
    serializer_class = HierarchySerializer
    pagination_class = None
    permission_classes = (IsAuthenticated,)
