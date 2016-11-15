# -*- coding: utf-8
from __future__ import unicode_literals

from django.contrib import admin
from import_export.admin import ExportMixin
from import_export.formats import base_formats

from .models import SummitAnket, Summit, SummitType, SummitAnketNote, SummitLesson
from .resources import SummitAnketResource


class SummitTypeAdmin(admin.ModelAdmin):
    fields = ('title', 'club_name', 'image', 'consultants')
    list_display = ('title', 'club_name')
    filter_horizontal = ('consultants',)


class SummitLessonInline(admin.TabularInline):
    fields = ('name', 'summit')
    model = SummitLesson


class SummitAdmin(admin.ModelAdmin):
    inlines = [SummitLessonInline, ]


class SummitAnketNoteInline(admin.TabularInline):
    model = SummitAnketNote


class SummitAnketAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ('name', 'user', 'summit', 'code', 'visited', 'is_member')
    list_editable = ('visited',)
    readonly_fields = ('user', 'summit')
    list_filter = ('summit', 'user__department', 'protected',)
    search_fields = ['code', 'user__last_name', ]

    resource_class = SummitAnketResource
    formats = (base_formats.XLSX,)

    inlines = [SummitAnketNoteInline, ]

    class Meta:
        model = SummitAnket


admin.site.register(SummitAnket, SummitAnketAdmin)
admin.site.register(Summit, SummitAdmin)
admin.site.register(SummitType, SummitTypeAdmin)
