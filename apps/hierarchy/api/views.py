from rest_framework import viewsets
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.hierarchy.api.permissions import VoCanSeeDepartment
from apps.hierarchy.api.serializers import DepartmentSerializer, HierarchySerializer
from apps.hierarchy.models import Department, Hierarchy


class DepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = (IsAuthenticated,)


class HierarchyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Hierarchy.objects.exclude(title='Архонт').all()
    serializer_class = HierarchySerializer
    pagination_class = None
    permission_classes = (IsAuthenticated,)


class VoDepartmentListView(GenericAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = (VoCanSeeDepartment,)
    pagination_class = None

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
