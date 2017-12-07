from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from task.api.pagintation import TaskPagination
from task.api.serializers import TaskCreateUpdateSerializer, TaskDisplaySerializer
from task.models import Task


class TaskViewSet(ModelViewSet):
    queryset = Task.objects.select_related('executor', 'creator', 'target')
    serializer_display_class = TaskDisplaySerializer
    serializer_create_update_class = TaskCreateUpdateSerializer
    pagination_class = TaskPagination
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return self.serializer_display_class
        return self.serializer_create_update_class

    def get_queryset(self):
        return self.queryset.filter(
            Q(creator=self.request.user) | Q(executor=self.request.user) | Q(
                division__in=self.request.user.divisions.all()))
