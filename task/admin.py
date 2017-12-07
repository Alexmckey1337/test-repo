from django.contrib import admin
from task.models import Task, TaskType


admin.site.register(Task)
admin.site.register(TaskType)
