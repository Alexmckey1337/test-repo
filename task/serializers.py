from .models import Task, TaskType
from rest_framework import serializers
from status.models import Division
from group.serializers import UserNameSerializer
from account.models import CustomUser
from django.utils.translation import ugettext_lazy as _


class TaskTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskType
        fields = ('id', 'title')


class DivisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Division
        fields = ('id', 'title')


class TaskCreateUpdateSerializer(serializers.ModelSerializer):
    description = serializers.CharField(required=True)
    creator = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())

    class Meta:
        model = Task
        fields = ('id', 'type', 'division', 'executor', 'target',
                  'date_published', 'description', 'creator')

    def create(self, validate_data):
        executor = validate_data.get('executor')
        creator = validate_data.get('creator')

        if (creator and executor) and (executor not in CustomUser.objects.for_user(creator)):
            raise serializers.ValidationError(
                {'message': _('Невозможно создать задачу. Указанный исполнитель не в Вашем подчинение')})

        task = Task.objects.create(**validate_data)
        return task

    def update(self, instance, validate_data):
        if validate_data.get('status') == Task.DONE and not validate_data.get('finish_report'):
            raise serializers.ValidationError('Невозможно завершить задачу. Отчет о завершение не передан.')


class TaskDisplaySerializer(TaskCreateUpdateSerializer):
    type = TaskTypeSerializer(read_only=True)
    division = DivisionSerializer(read_only=True)
    executor = UserNameSerializer(read_only=True)
    creator = UserNameSerializer(read_only=True)
    target = UserNameSerializer(read_only=True)

    class Meta(TaskCreateUpdateSerializer.Meta):
        fields = TaskCreateUpdateSerializer.Meta.fields + (
            'date_finish', 'finish_report', 'status', 'creator'
        )

        read_only_fields = ['__all__']
