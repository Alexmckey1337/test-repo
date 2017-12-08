# -*- coding: utf-8
from __future__ import unicode_literals

from django.contrib import admin

from status.models import Status, Division


class StatusAdmin(admin.ModelAdmin):
    list_display = ('title',)

    class Meta:
        model = Status


admin.site.register(Status, StatusAdmin)


class DivisionAdmin(admin.ModelAdmin):
    list_display = ('title',)

    class Meta:
        model = Division


admin.site.register(Division, DivisionAdmin)
