from django.contrib import admin

from apps.manager.models import Manager
from apps.group.models import HomeGroup


class ManagerAdmin(admin.ModelAdmin):
    list_display = ('group', 'person')
    list_editable = ('person',)

    class Meta:
        model = Manager


admin.site.register(Manager, ManagerAdmin)