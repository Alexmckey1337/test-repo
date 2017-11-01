from .models import Task
from rest_framework.viewsets import ModelViewSet
from .serializers import TaskCreateUpdateSerializer, TaskDisplaySerializer
from django.db.models import Q
from .pagintation import TaskPagination


class TaskViewSet(ModelViewSet):
    queryset = Task.objects.select_related('executor', 'creator', 'target')
    serializer_display_class = TaskDisplaySerializer
    serializer_create_update_class = TaskCreateUpdateSerializer
    pagination_class = TaskPagination

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return self.serializer_display_class
        return self.serializer_create_update_class

    def get_queryset(self):
        return self.queryset.filter(
            Q(creator=self.request.user) | Q(executor=self.request.user) | Q(
                division__in=self.request.user.divisions.all()))
