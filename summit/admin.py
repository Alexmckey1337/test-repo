# -*- coding: utf-8
from __future__ import unicode_literals

from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .models import SummitAnket, Summit, SummitType, SummitAnketNote
from .resources import SummitAnketResource


class SummitTypeAdmin(admin.ModelAdmin):
    fields = ('title', 'image', 'consultants')
    filter_horizontal = ('consultants',)


class SummitAnketNoteInline(admin.TabularInline):
    model = SummitAnketNote


class SummitAnketAdmin(ImportExportModelAdmin):
    list_display = ('name', 'user', 'summit', 'code',)
    list_filter = ('summit', 'user__department', 'protected',)
    search_fields = ['code', 'user__last_name', ]
    resource_class = SummitAnketResource

    inlines = [SummitAnketNoteInline, ]

    class Meta:
        model = SummitAnket


admin.site.register(SummitAnket, SummitAnketAdmin)
admin.site.register(Summit)
admin.site.register(SummitType, SummitTypeAdmin)
