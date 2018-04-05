from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.hierarchy.api.serializers import DepartmentSerializer, HierarchySerializer
from apps.hierarchy.models import Department, Hierarchy


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = (IsAuthenticated,)


class HierarchyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Hierarchy.objects.exclude(title='Архонт').all()
    serializer_class = HierarchySerializer
    pagination_class = None
    permission_classes = (IsAuthenticated,)
