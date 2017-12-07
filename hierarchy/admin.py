# -*- coding: utf-8
from __future__ import unicode_literals

from django.contrib import admin

from hierarchy.models import Department, Hierarchy


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('title',)

    class Meta:
        model = Department


admin.site.register(Department, DepartmentAdmin)


class HierarchyAdmin(admin.ModelAdmin):
    list_display = ('title', 'level',)

    class Meta:
        model = Hierarchy


admin.site.register(Hierarchy, HierarchyAdmin)
